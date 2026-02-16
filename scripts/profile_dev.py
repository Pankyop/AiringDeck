import argparse
import os
import pstats
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def _write_stats(profile_path: Path, output_path: Path, sort_key: str, limit: int) -> None:
    with output_path.open("w", encoding="utf-8") as fh:
        stats = pstats.Stats(str(profile_path), stream=fh)
        stats.strip_dirs().sort_stats(sort_key).print_stats(limit)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run AiringDeck in DEV profiling mode")
    parser.add_argument("--duration-ms", type=int, default=15000, help="Auto-exit delay in milliseconds")
    parser.add_argument("--top", type=int, default=40, help="How many lines to keep in pstats reports")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    profiles_dir = project_root / "profiles"
    profiles_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    profile_raw = profiles_dir / f"dev_profile_{timestamp}.prof"
    stdout_log = profiles_dir / f"dev_profile_{timestamp}_stdout.log"
    stderr_log = profiles_dir / f"dev_profile_{timestamp}_stderr.log"
    report_cum = profiles_dir / f"dev_profile_{timestamp}_cum.txt"
    report_self = profiles_dir / f"dev_profile_{timestamp}_self.txt"

    env = os.environ.copy()
    env["AIRINGDECK_PROFILE"] = "1"
    env["AIRINGDECK_AUTO_EXIT_MS"] = str(max(1000, args.duration_ms))

    cmd = [sys.executable, "-m", "cProfile", "-o", str(profile_raw), "src/main.py"]
    print("Running:", " ".join(cmd))
    print(f"Profiling output directory: {profiles_dir}")

    with stdout_log.open("w", encoding="utf-8") as out_fh, stderr_log.open("w", encoding="utf-8") as err_fh:
        result = subprocess.run(
            cmd,
            cwd=project_root,
            env=env,
            stdout=out_fh,
            stderr=err_fh,
            timeout=max(60, args.duration_ms // 1000 + 45),
            check=False,
        )

    if result.returncode != 0:
        print(f"Profiling run failed with exit code {result.returncode}")
        print(f"See logs: {stdout_log} and {stderr_log}")
        return result.returncode

    _write_stats(profile_raw, report_cum, "cumulative", args.top)
    _write_stats(profile_raw, report_self, "tottime", args.top)

    print("Profiling completed successfully.")
    print(f"Raw profile: {profile_raw}")
    print(f"Cumulative report: {report_cum}")
    print(f"Self-time report: {report_self}")
    print(f"Stdout log: {stdout_log}")
    print(f"Stderr log: {stderr_log}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
