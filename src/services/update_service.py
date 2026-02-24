import os
import re
from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True, order=True)
class ParsedVersion:
    major: int
    minor: int
    patch: int
    stage_rank: int
    stage_num: int


class UpdateService:
    """Checks remote release/tag metadata and reports update availability."""

    DEFAULT_REPOSITORY = "Pankyop/AiringDeck"
    VERSION_PATTERN = re.compile(
        r"(?i)\bv?(?P<maj>\d+)\.(?P<min>\d+)\.(?P<patch>\d+)"
        r"(?:(?:[-_.]?)(?P<pre>alpha|a|beta|b|rc)(?:[-_.]?(?P<num>\d+))?)?\b"
    )

    def __init__(self):
        self._repo = os.getenv("AIRINGDECK_UPDATE_REPOSITORY", self.DEFAULT_REPOSITORY).strip()
        self._feed_url = os.getenv("AIRINGDECK_UPDATE_FEED_URL", "").strip()
        self._tags_url = os.getenv("AIRINGDECK_UPDATE_TAGS_URL", "").strip()
        self._download_url = os.getenv("AIRINGDECK_UPDATE_DOWNLOAD_URL", "").strip()

        if not self._feed_url and self._repo:
            self._feed_url = f"https://api.github.com/repos/{self._repo}/releases/latest"
        if not self._tags_url and self._repo:
            self._tags_url = f"https://api.github.com/repos/{self._repo}/tags"

    @property
    def feed_url(self) -> str:
        return self._feed_url

    @property
    def tags_url(self) -> str:
        return self._tags_url

    def _request_json(self, url: str) -> Any | None:
        if not url:
            return None
        response = requests.get(
            url,
            timeout=8,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "AiringDeck-UpdateChecker",
            },
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    def _extract_version(self, raw: str) -> str | None:
        if not raw:
            return None
        match = self.VERSION_PATTERN.search(raw)
        if not match:
            return None
        major = int(match.group("maj"))
        minor = int(match.group("min"))
        patch = int(match.group("patch"))
        pre = (match.group("pre") or "").lower()
        pre_num = match.group("num")
        if not pre:
            return f"{major}.{minor}.{patch}"

        normalized_pre = {
            "a": "alpha",
            "alpha": "alpha",
            "b": "beta",
            "beta": "beta",
            "rc": "rc",
        }[pre]
        serial = int(pre_num or "1")
        return f"{major}.{minor}.{patch}-{normalized_pre}.{serial}"

    def _parse_version(self, raw: str) -> ParsedVersion:
        normalized = self._extract_version(raw)
        if not normalized:
            raise ValueError(f"Invalid version: {raw}")

        base, _, pre = normalized.partition("-")
        major_s, minor_s, patch_s = base.split(".")
        major, minor, patch = int(major_s), int(minor_s), int(patch_s)

        if not pre:
            return ParsedVersion(major, minor, patch, 3, 0)

        stage, _, serial_s = pre.partition(".")
        stage_rank = {"alpha": 0, "beta": 1, "rc": 2}.get(stage, 0)
        serial = int(serial_s or "1")
        return ParsedVersion(major, minor, patch, stage_rank, serial)

    def _is_newer(self, latest: str, current: str) -> bool:
        return self._parse_version(latest) > self._parse_version(current)

    def _summarize_notes(self, body: str) -> str:
        if not body:
            return "A new version is available."
        lines: list[str] = []
        for raw in body.splitlines():
            line = raw.strip()
            if not line:
                continue
            if line.startswith("#"):
                continue
            if line.startswith("- "):
                line = line[2:].strip()
            if line.startswith("* "):
                line = line[2:].strip()
            if not line:
                continue
            lines.append(f"• {line}")
            if len(lines) >= 6:
                break
        return "\n".join(lines) if lines else "A new version is available."

    def _pick_windows_installer_asset(self, payload: dict[str, Any]) -> str | None:
        assets = payload.get("assets")
        if not isinstance(assets, list):
            return None

        ranked: list[tuple[int, str]] = []
        for asset in assets:
            if not isinstance(asset, dict):
                continue
            name = str(asset.get("name") or "").strip().lower()
            url = str(asset.get("browser_download_url") or "").strip()
            if not url:
                continue
            if name.endswith(".exe") and "setup" in name:
                ranked.append((0, url))
            elif name.endswith(".exe"):
                ranked.append((1, url))
            elif name.endswith(".msi"):
                ranked.append((2, url))
            elif name.endswith(".msix") or name.endswith(".msixbundle"):
                ranked.append((3, url))

        if not ranked:
            return None
        ranked.sort(key=lambda item: item[0])
        return ranked[0][1]

    def _from_release_payload(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        raw_tag = str(payload.get("tag_name") or payload.get("name") or "").strip()
        latest_version = self._extract_version(raw_tag)
        if not latest_version:
            return None
        direct_download = self._pick_windows_installer_asset(payload)
        return {
            "latest_version": latest_version,
            "title": str(payload.get("name") or f"v{latest_version}"),
            "notes": self._summarize_notes(str(payload.get("body") or "")),
            "download_url": self._download_url
            or direct_download
            or str(payload.get("html_url") or f"https://github.com/{self._repo}/releases/latest"),
            "published_at": str(payload.get("published_at") or ""),
            "source": "release",
        }

    def _from_tags_payload(self, payload: Any) -> dict[str, Any] | None:
        if not isinstance(payload, list):
            return None
        for tag in payload:
            raw_tag = str((tag or {}).get("name") or "").strip()
            latest_version = self._extract_version(raw_tag)
            if not latest_version:
                continue
            return {
                "latest_version": latest_version,
                "title": f"v{latest_version}",
                "notes": "A new update is available. Check release notes on GitHub.",
                "download_url": self._download_url
                or f"https://github.com/{self._repo}/releases",
                "published_at": "",
                "source": "tag",
            }
        return None

    def check_latest(self, current_version: str) -> dict[str, Any]:
        current = self._extract_version(current_version) or current_version
        if not current:
            raise ValueError("Current version is empty")

        candidate = None
        release_payload = self._request_json(self._feed_url)
        if isinstance(release_payload, dict):
            candidate = self._from_release_payload(release_payload)

        if candidate is None:
            tags_payload = self._request_json(self._tags_url)
            candidate = self._from_tags_payload(tags_payload)

        if not candidate:
            return {
                "available": False,
                "current_version": current,
            }

        latest = candidate["latest_version"]
        if not self._is_newer(latest, current):
            return {
                "available": False,
                "current_version": current,
                "latest_version": latest,
            }

        return {
            "available": True,
            "current_version": current,
            **candidate,
        }
