import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _read_app_version(root: Path) -> str:
    version_file = root / "src" / "version.py"
    text = version_file.read_text(encoding="utf-8")
    match = re.search(r'APP_VERSION\s*=\s*"([^"]+)"', text)
    if not match:
        raise RuntimeError("Cannot parse APP_VERSION from src/version.py")
    return match.group(1)


def _find_iscc() -> str | None:
    if shutil.which("ISCC.exe"):
        return "ISCC.exe"
    local_programs = Path.home() / "AppData" / "Local" / "Programs" / "Inno Setup 6" / "ISCC.exe"
    candidates = [
        Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
        local_programs,
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None


def _build_exe(root: Path) -> None:
    cmd = [sys.executable, "scripts/build_windows.py"]
    subprocess.run(cmd, cwd=root, check=True)


def _build_installer(root: Path, version: str, iscc: str, source_exe: Path) -> None:
    iss_path = root / "installer" / "AiringDeck.iss"
    cmd = [
        iscc,
        f"/DAppVersion={version}",
        f"/DSourceExe={source_exe}",
        str(iss_path),
    ]
    subprocess.run(cmd, cwd=root, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build AiringDeck Windows installer (Inno Setup).")
    parser.add_argument(
        "--skip-build-exe",
        action="store_true",
        help="Skip EXE build and use existing dist/AiringDeck.exe",
    )
    args = parser.parse_args()

    root = _project_root()
    version = _read_app_version(root)
    source_exe = root / "dist" / "AiringDeck.exe"

    if not args.skip_build_exe:
        _build_exe(root)

    if not source_exe.exists():
        raise FileNotFoundError(f"Missing executable: {source_exe}")

    iscc = _find_iscc()
    if not iscc:
        raise RuntimeError(
            "Inno Setup compiler (ISCC.exe) not found. Install Inno Setup 6 and retry."
        )

    _build_installer(root, version, iscc, source_exe)
    print(f"Installer generated in: {root / 'dist'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
