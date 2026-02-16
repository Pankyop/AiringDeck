import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def run(cmd: list[str], desc: str) -> int:
    print(f"\n=== {desc} ===")
    print(" ".join(cmd))
    return subprocess.run(cmd, cwd=ROOT, check=False).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Run debug/quality checks for AiringDeck")
    parser.add_argument("--with-profile", action="store_true", help="Include system profiling run")
    parser.add_argument("--profile-duration", type=int, default=30, help="Profile duration seconds")
    args = parser.parse_args()

    failures = []

    checks = [
        ([sys.executable, "-m", "py_compile", "src/main.py", "src/core/app_controller.py", "src/core/anime_model.py", "src/core/worker.py"], "Compile checks"),
        ([sys.executable, "-m", "ruff", "check", "src", "tests", "scripts"], "Static lint (ruff)"),
        ([sys.executable, "-m", "bandit", "-q", "-r", "src"], "Security scan (bandit)"),
        ([sys.executable, "-m", "coverage", "run", "--source=src", "-m", "pytest", "-q"], "Unit tests"),
        ([sys.executable, "-m", "coverage", "report", "-m", "-i"], "Coverage report"),
    ]

    for cmd, desc in checks:
        code = run(cmd, desc)
        if code != 0:
            failures.append((desc, code))

    if args.with_profile:
        code = run(
            [
                sys.executable,
                "scripts/profile_system.py",
                "--duration",
                str(args.profile_duration),
                "--interval",
                "1.0",
            ],
            "Runtime system profiling",
        )
        if code != 0:
            failures.append(("Runtime system profiling", code))

    if failures:
        print("\nFAILED CHECKS:")
        for desc, code in failures:
            print(f"- {desc}: exit {code}")
        return 1

    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
