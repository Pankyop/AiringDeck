import PyInstaller.__main__
import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path

CPU_PROFILE_FLAGS = {
    "baseline": "",
    # Intel 10th gen+ and AMD Zen2+ are generally covered by AVX2 target.
    "avx2": "/O2 /GL /arch:AVX2",
    # Optional, use only for controlled deployments with known AVX-512 support.
    "avx512": "/O2 /GL /arch:AVX512",
}


def _build_args(project_root: Path):
    return [
        str(project_root / "src" / "main.py"),
        f"--paths={project_root / 'src'}",
        "--name=AiringDeck",
        "--onefile",
        "--windowed",
        "--python-option=O",
        "--add-data=src/ui/qml;src/ui/qml",
        "--add-data=resources;resources",
        "--hidden-import=PySide6",
        "--hidden-import=requests",
        "--hidden-import=keyring",
        "--hidden-import=dotenv",
        "--clean",
        "--noconfirm",
    ]


def build(cpu_profile: str, require_native: bool):
    """Build Windows executable with optional CPU-focused optimization profile."""
    project_root = Path(__file__).parent.parent
    cflags = CPU_PROFILE_FLAGS[cpu_profile]
    if cflags and platform.system() == "Windows":
        os.environ["CL"] = f"{os.environ.get('CL', '')} {cflags}".strip()
        print(f"Using CL flags for profile '{cpu_profile}': {os.environ['CL']}")
    else:
        print(f"Using CPU profile '{cpu_profile}' without extra compiler flags.")

    try:
        subprocess.run(
            [sys.executable, "setup.py", "build_ext", "--inplace"],
            cwd=project_root,
            check=True,
        )
        print("Native extension build completed.")
    except subprocess.CalledProcessError as exc:
        if require_native:
            raise
        print(f"Native extension build failed, using Python fallback. Details: {exc}")

    PyInstaller.__main__.run(_build_args(project_root))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build AiringDeck for Windows")
    parser.add_argument(
        "--cpu-profile",
        choices=tuple(CPU_PROFILE_FLAGS.keys()),
        default="avx2",
        help="CPU optimization target. Use 'avx2' for Intel 10th+/AMD Zen2+.",
    )
    parser.add_argument(
        "--require-native",
        action="store_true",
        help="Fail build if native C extension cannot be compiled.",
    )
    args = parser.parse_args()
    build(args.cpu_profile, args.require_native)
