#!/usr/bin/env python3
"""
Experiment 2: Microarchitectural Profiling Runner (perf stat)
Orchestrates hardware performance counter collection across heap variants.
Captures L1 data cache misses, LLC misses, branch mispredictions, and IPC.
"""

import argparse
import csv
import json
import os
import platform
import shutil
import subprocess
import sys

MODES = ["decrease_key", "lazy"]

EVENTS = {
    "cycles": "cycles",
    "instructions": "instructions",
    "branches": "branches",
    "branch_misses": "branch-misses",
    "L1_loads": "L1-dcache-loads",
    "L1_misses": "L1-dcache-load-misses",
    "LLC_loads": "LLC-loads",
    "LLC_misses": "LLC-load-misses",
}
REQUIRED_EVENTS = ("cycles", "instructions", "branches", "branch_misses")
OPTIONAL_EVENTS = ("L1_loads", "L1_misses", "LLC_loads", "LLC_misses")


def listed_event_names(listing):
    names = set()
    for line in listing.splitlines():
        event_part = line.split("[", 1)[0]
        for name in event_part.split(" OR "):
            name = name.strip().lower()
            if name:
                names.add(name)
    return names


def discover_events(perf):
    try:
        proc = subprocess.run(
            [perf, "list"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [], f"unable to inspect perf events: {exc}"

    names = listed_event_names(proc.stdout)
    available = [
        key for key, event in EVENTS.items()
        if event.lower() in names
    ]
    missing = [key for key in EVENTS if key not in available]
    return available, (
        f"unsupported events omitted: {', '.join(missing)}" if missing else ""
    )


def run_perf_stat(perf, taskset, binary_path, config, mode, events, iters=1, core_id=0):
    """
    Executes binary under `taskset -c <core>` and `perf stat -x,`.
    Returns dict of counter values.
    """
    events_str = ",".join(EVENTS[key] for key in events)
    command = [perf, "stat", "-x,", "-e", events_str, binary_path, config, mode, str(iters)]
    cmd = [taskset, "-c", str(core_id)] + command if taskset else command

    try:
        proc = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=120
        )
    except subprocess.TimeoutExpired:
        return {}, "perf timed out"

    if proc.returncode != 0:
        detail = proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else "unknown error"
        return {}, f"perf failed ({detail})"

    # Parse CSV output from stderr (perf stat -x, writes to stderr)
    stats = {}
    for line in proc.stderr.splitlines():
        parts = line.strip().split(",")
        if len(parts) >= 3:
            val_str, _, event_name = parts[0], parts[1], parts[2]
            for key, event in EVENTS.items():
                if event == event_name or event in event_name:
                    try:
                        stats[key] = float(val_str)
                    except ValueError:
                        pass
                    break

    return stats, ""


def main():
    parser = argparse.ArgumentParser(description="Experiment 2: Microarchitectural Hardware Profiling")
    parser.add_argument("-b", "--bin-dir", default="bin", help="Directory containing perf binaries")
    parser.add_argument("-o", "--output", default="data/out/perf/hardware_counters.csv", help="Output CSV path")
    parser.add_argument("-c", "--core", type=int, default=0, help="CPU Core to pin execution (default 0)")
    args = parser.parse_args()

    if platform.system() != "Linux":
        parser.error("perf profiling is only supported on Linux")

    perf = shutil.which("perf")
    if not perf:
        parser.error("perf was not found; install Linux perf or omit the perf benchmark")

    taskset = shutil.which("taskset")
    available_events, event_note = discover_events(perf)
    events = [key for key in REQUIRED_EVENTS + OPTIONAL_EVENTS if key in available_events]
    if not events:
        parser.error("perf reported no usable events")
    if not taskset:
        event_note = "; ".join(
            part for part in (event_note, "taskset unavailable; CPU pinning disabled") if part
        )

    script_dir = os.path.dirname(os.path.abspath(__file__))
    proj_root = os.path.abspath(os.path.join(script_dir, "../../.."))

    bin_dir = args.bin_dir if os.path.isabs(args.bin_dir) else os.path.join(proj_root, args.bin_dir)
    output_path = args.output if os.path.isabs(args.output) else os.path.join(proj_root, args.output)
    metadata_path = os.path.join(proj_root, "build", "test", "graphs.json")
    with open(metadata_path, encoding="utf-8") as metadata_file:
        configs = json.load(metadata_file)["graphs"]
    variants = sorted(
        name for name in os.listdir(bin_dir)
        if os.path.isfile(os.path.join(bin_dir, name))
        and os.access(os.path.join(bin_dir, name), os.X_OK)
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print("=" * 80)
    print(" Experiment 2: Microarchitectural Profiling (perf stat)")
    print(f" CPU Core Pinned: {args.core}")
    print(f"     Configurations are read from the generated graph metadata.")
    print("=" * 80)

    results = []

    for config in configs:
        for mode in MODES:
            for variant in variants:
                bin_name = variant
                binary_path = os.path.join(bin_dir, bin_name)

                if not os.path.exists(binary_path):
                    print(f"[SKIP] Binary not found: {binary_path}")
                    continue

                iters = 1
                sys.stdout.write(f"[*] Running {variant:<15} [{config:<6} | {mode:<12}] (iters={iters}) ... ")
                sys.stdout.flush()

                stats, run_note = run_perf_stat(
                    perf, taskset, binary_path, config, mode, events, iters=iters, core_id=args.core
                )
                note = "; ".join(part for part in (event_note, run_note) if part)
                if not stats:
                    print(f"UNAVAILABLE ({note})")
                else:
                    print("OK")

                l1_loads = stats.get("L1_loads", 0)
                l1_misses = stats.get("L1_misses", 0)
                llc_loads = stats.get("LLC_loads", 0)
                llc_misses = stats.get("LLC_misses", 0)
                branches = stats.get("branches", 0)
                branch_misses = stats.get("branch_misses", 0)
                cycles = stats.get("cycles", 0)
                instructions = stats.get("instructions", 0)

                l1_miss_rate = (l1_misses / l1_loads * 100.0) if l1_loads > 0 else 0.0
                llc_miss_rate = (llc_misses / llc_loads * 100.0) if llc_loads > 0 else 0.0
                branch_miss_rate = (branch_misses / branches * 100.0) if branches > 0 else 0.0
                ipc = (instructions / cycles) if cycles > 0 else 0.0

                results.append({
                    "variant": variant,
                    "config": config,
                    "mode": mode,
                    "L1_loads": int(l1_loads),
                    "L1_misses": int(l1_misses),
                    "L1_miss_rate_pct": f"{l1_miss_rate:.2f}",
                    "LLC_loads": int(llc_loads),
                    "LLC_misses": int(llc_misses),
                    "LLC_miss_rate_pct": f"{llc_miss_rate:.2f}",
                    "branches": int(branches),
                    "branch_misses": int(branch_misses),
                    "branch_miss_rate_pct": f"{branch_miss_rate:.2f}",
                    "cycles": int(cycles),
                    "instructions": int(instructions),
                    "IPC": f"{ipc:.2f}",
                    "note": note,
                })

    # Write output CSV
    fieldnames = [
        "variant", "config", "mode",
        "L1_loads", "L1_misses", "L1_miss_rate_pct",
        "LLC_loads", "LLC_misses", "LLC_miss_rate_pct",
        "branches", "branch_misses", "branch_miss_rate_pct",
        "cycles", "instructions", "IPC", "note"
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print("\n" + "=" * 80)
    print(f"[SUCCESS] Hardware counter results saved to: {output_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
