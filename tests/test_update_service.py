from services.update_service import UpdateService


class _Resp:
    def __init__(self, status_code=200, payload=None, exc=None):
        self.status_code = status_code
        self._payload = payload or {}
        self._exc = exc

    def raise_for_status(self):
        if self._exc:
            raise self._exc

    def json(self):
        return self._payload


def test_check_latest_from_release_newer(monkeypatch):
    monkeypatch.setenv("AIRINGDECK_UPDATE_REPOSITORY", "owner/repo")
    svc = UpdateService()

    def fake_request(url):
        if url.endswith("/releases/latest"):
            return {
                "tag_name": "v3.3.0",
                "name": "3.3.0 Stable",
                "body": "- Faster startup\n- Better update UX",
                "html_url": "https://github.com/owner/repo/releases/tag/v3.3.0",
                "assets": [
                    {
                        "name": "AiringDeck-Setup-3.3.0.exe",
                        "browser_download_url": "https://github.com/owner/repo/releases/download/v3.3.0/AiringDeck-Setup-3.3.0.exe",
                    }
                ],
                "published_at": "2026-02-19T18:00:00Z",
            }
        return None

    monkeypatch.setattr(svc, "_request_json", fake_request)

    out = svc.check_latest("3.3.0-beta.1")

    assert out["available"] is True
    assert out["latest_version"] == "3.3.0"
    assert "Faster startup" in out["notes"]
    assert out["download_url"].endswith("AiringDeck-Setup-3.3.0.exe")


def test_check_latest_release_without_assets_uses_release_page(monkeypatch):
    monkeypatch.setenv("AIRINGDECK_UPDATE_REPOSITORY", "owner/repo")
    svc = UpdateService()

    def fake_request(url):
        if url.endswith("/releases/latest"):
            return {
                "tag_name": "v3.4.0",
                "name": "3.4.0 Stable",
                "body": "- Menu refresh",
                "html_url": "https://github.com/owner/repo/releases/tag/v3.4.0",
            }
        return None

    monkeypatch.setattr(svc, "_request_json", fake_request)
    out = svc.check_latest("3.3.0")

    assert out["available"] is True
    assert out["download_url"].endswith("/v3.4.0")


def test_check_latest_release_not_newer(monkeypatch):
    monkeypatch.setenv("AIRINGDECK_UPDATE_REPOSITORY", "owner/repo")
    svc = UpdateService()

    def fake_request(url):
        if url.endswith("/releases/latest"):
            return {"tag_name": "v3.3.0-beta.1", "name": "3.3.0 beta.1"}
        return None

    monkeypatch.setattr(svc, "_request_json", fake_request)

    out = svc.check_latest("3.3.0-beta.1")

    assert out["available"] is False
    assert out["latest_version"] == "3.3.0-beta.1"


def test_check_latest_fallback_to_tags(monkeypatch):
    monkeypatch.setenv("AIRINGDECK_UPDATE_REPOSITORY", "owner/repo")
    svc = UpdateService()

    def fake_request(url):
        if url.endswith("/releases/latest"):
            return None
        if url.endswith("/tags"):
            return [{"name": "v3.4.0-rc.1"}]
        return None

    monkeypatch.setattr(svc, "_request_json", fake_request)

    out = svc.check_latest("3.3.0")

    assert out["available"] is True
    assert out["latest_version"] == "3.4.0-rc.1"
    assert out["source"] == "tag"


def test_extract_version_handles_normalized_prerelease(monkeypatch):
    monkeypatch.setenv("AIRINGDECK_UPDATE_REPOSITORY", "owner/repo")
    svc = UpdateService()

    assert svc._extract_version("3.3.0b1") == "3.3.0-beta.1"
    assert svc._extract_version("v3.3.0rc2") == "3.3.0-rc.2"
    assert svc._extract_version("release-3.3.0") == "3.3.0"


def test_request_json_handles_404(monkeypatch):
    monkeypatch.setenv("AIRINGDECK_UPDATE_REPOSITORY", "owner/repo")
    svc = UpdateService()

    monkeypatch.setattr("services.update_service.requests.get", lambda *args, **kwargs: _Resp(status_code=404))

    assert svc._request_json("https://example.com/feed") is None


def test_request_json_returns_payload_on_200(monkeypatch):
    monkeypatch.setenv("AIRINGDECK_UPDATE_REPOSITORY", "owner/repo")
    svc = UpdateService()

    monkeypatch.setattr(
        "services.update_service.requests.get",
        lambda *args, **kwargs: _Resp(status_code=200, payload={"ok": True}),
    )

    out = svc._request_json("https://example.com/feed")
    assert out == {"ok": True}


def test_check_latest_returns_unavailable_when_no_release_or_tags(monkeypatch):
    monkeypatch.setenv("AIRINGDECK_UPDATE_REPOSITORY", "owner/repo")
    svc = UpdateService()
    monkeypatch.setattr(svc, "_request_json", lambda *_: None)

    out = svc.check_latest("3.3.0")
    assert out["available"] is False
    assert out["current_version"] == "3.3.0"
