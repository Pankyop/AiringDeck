import argparse
import csv
import statistics
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

import psutil


@dataclass
class Sample:
    timestamp: str
    pid: int
    cpu_percent: float
    rss_mb: float
    vms_mb: float
    read_bps: float
    write_bps: float
    threads: int
    handles: int
    tcp_total: int
    tcp_established: int


def _pick_runtime_process(start_time: float) -> psutil.Process | None:
    candidates = []
    for p in psutil.process_iter(["pid", "name", "create_time", "memory_info"]):
        try:
            if p.info["name"] and "AiringDeck" in p.info["name"] and p.info["create_time"] >= start_time - 1:
                candidates.append(p)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.memory_info().rss)


def _quantile(values, q):
    if not values:
        return 0.0
    if len(values) == 1:
        return float(values[0])
    return float(statistics.quantiles(values, n=100)[max(0, min(99, q - 1))])


def run_profile(exe: Path, out_dir: Path, duration: int, interval: float) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = out_dir / f"system_profile_{ts}.csv"
    summary_path = out_dir / f"system_profile_{ts}_summary.txt"

    # Clean stale processes.
    for p in psutil.process_iter(["name"]):
        try:
            if p.info["name"] and "AiringDeck" in p.info["name"]:
                p.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    start_time = time.time()
    subprocess.Popen([str(exe)], cwd=str(exe.parent.parent))
    proc = None
    for _ in range(40):
        time.sleep(0.25)
        proc = _pick_runtime_process(start_time)
        if proc is not None:
            break
    if proc is None:
        raise RuntimeError("Runtime process AiringDeck not found")

    # Prime counters
    try:
        io_prev = proc.io_counters()
    except Exception:
        io_prev = None
    proc.cpu_percent(interval=None)
    last_t = time.time()

    samples: list[Sample] = []
    for _ in range(int(duration / interval)):
        time.sleep(interval)
        candidate = _pick_runtime_process(start_time)
        if candidate is None:
            break
        if candidate.pid != proc.pid:
            proc = candidate
            try:
                io_prev = proc.io_counters()
            except Exception:
                io_prev = None
            proc.cpu_percent(interval=None)
            last_t = time.time()
            continue
        if not proc.is_running():
            break
        now = time.time()
        dt = max(0.001, now - last_t)
        last_t = now

        try:
            mem = proc.memory_info()
            cpu_pct = proc.cpu_percent(interval=None) / max(1, psutil.cpu_count(logical=True))
            io_now = proc.io_counters() if io_prev is not None else None
            if io_prev and io_now:
                read_bps = max(0.0, (io_now.read_bytes - io_prev.read_bytes) / dt)
                write_bps = max(0.0, (io_now.write_bytes - io_prev.write_bytes) / dt)
                io_prev = io_now
            else:
                read_bps = 0.0
                write_bps = 0.0
            conns = proc.net_connections(kind="tcp")
            tcp_total = len(conns)
            tcp_est = sum(1 for c in conns if c.status == psutil.CONN_ESTABLISHED)
            handles = proc.num_handles() if hasattr(proc, "num_handles") else 0
            sample = Sample(
                timestamp=datetime.now().isoformat(),
                pid=proc.pid,
                cpu_percent=round(cpu_pct, 2),
                rss_mb=round(mem.rss / (1024 * 1024), 2),
                vms_mb=round(mem.vms / (1024 * 1024), 2),
                read_bps=round(read_bps, 2),
                write_bps=round(write_bps, 2),
                threads=proc.num_threads(),
                handles=handles,
                tcp_total=tcp_total,
                tcp_established=tcp_est,
            )
            samples.append(sample)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            break

    # Stop app
    for p in psutil.process_iter(["name"]):
        try:
            if p.info["name"] and "AiringDeck" in p.info["name"]:
                p.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if not samples:
        raise RuntimeError("No samples collected")

    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(asdict(samples[0]).keys()))
        writer.writeheader()
        for s in samples:
            writer.writerow(asdict(s))

    cpu_vals = [s.cpu_percent for s in samples]
    rss_vals = [s.rss_mb for s in samples]
    read_vals = [s.read_bps for s in samples]
    write_vals = [s.write_bps for s in samples]
    tcp_vals = [s.tcp_total for s in samples]
    est_vals = [s.tcp_established for s in samples]
    pids = sorted({s.pid for s in samples})

    summary = [
        f"AiringDeck system profile ({ts})",
        f"samples={len(samples)}, duration_s={duration}, interval_s={interval}",
        f"profiled_pids={','.join(str(p) for p in pids)}",
        f"cpu_avg_pct={statistics.mean(cpu_vals):.2f}",
        f"cpu_p95_pct={_quantile(cpu_vals, 95):.2f}",
        f"cpu_peak_pct={max(cpu_vals):.2f}",
        f"rss_avg_mb={statistics.mean(rss_vals):.2f}",
        f"rss_p95_mb={_quantile(rss_vals, 95):.2f}",
        f"rss_peak_mb={max(rss_vals):.2f}",
        f"io_read_avg_bps={statistics.mean(read_vals):.2f}",
        f"io_write_avg_bps={statistics.mean(write_vals):.2f}",
        f"io_read_peak_bps={max(read_vals):.2f}",
        f"io_write_peak_bps={max(write_vals):.2f}",
        f"tcp_total_peak={max(tcp_vals)}",
        f"tcp_established_peak={max(est_vals)}",
        f"csv={csv_path}",
    ]
    summary_path.write_text("\n".join(summary), encoding="utf-8")
    return csv_path, summary_path


def main():
    parser = argparse.ArgumentParser(description="System profiling for AiringDeck runtime")
    parser.add_argument("--duration", type=int, default=70, help="Duration in seconds")
    parser.add_argument("--interval", type=float, default=1.0, help="Sampling interval in seconds")
    parser.add_argument("--exe", default="dist/AiringDeck.exe", help="Path to AiringDeck executable")
    parser.add_argument("--out", default="profiles", help="Output directory")
    args = parser.parse_args()

    csv_path, summary_path = run_profile(Path(args.exe), Path(args.out), args.duration, args.interval)
    print(f"CSV: {csv_path}")
    print(f"Summary: {summary_path}")
    print(summary_path.read_text(encoding='utf-8'))


if __name__ == "__main__":
    raise SystemExit(main())
