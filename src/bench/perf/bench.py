#!/usr/bin/env python3
"""
Experiment 2: Microarchitectural Profiling Runner (perf stat)
Orchestrates hardware performance counter collection across heap variants.
Captures L1 data cache misses, LLC misses, branch mispredictions, and IPC.
"""

import argparse
import csv
import os
import re
import subprocess
import sys

VARIANTS = ["binary", "pairing", "fibonacci", "brodal-okasaki"]
CONFIGS = ["sparse", "dense"]
MODES = ["decrease_key", "lazy"]

# P-core hardware events
EVENTS = [
    "cpu_core/L1-dcache-loads/",
    "cpu_core/L1-dcache-load-misses/",
    "cpu_core/LLC-loads/",
    "cpu_core/LLC-load-misses/",
    "cpu_core/branch-instructions/",
    "cpu_core/branch-misses/",
    "cpu_core/cycles/",
    "cpu_core/instructions/",
]


def run_perf_stat(binary_path, config, mode, iters=1, core_id=0):
    """
    Executes binary under `taskset -c <core>` and `perf stat -x,`.
    Returns dict of counter values.
    """
    events_str = ",".join(EVENTS)
    cmd = [
        "taskset", "-c", str(core_id),
        "perf", "stat", "-x,",
        "-e", events_str,
        binary_path, config, mode, str(iters)
    ]

    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        print(f" [TIMEOUT]", file=sys.stderr)
        return None

    if proc.returncode != 0:
        print(f" [ERROR: code {proc.returncode}] {proc.stderr.strip()}", file=sys.stderr)
        return None

    # Parse CSV output from stderr (perf stat -x, writes to stderr)
    stats = {}
    for line in proc.stderr.splitlines():
        parts = line.strip().split(",")
        if len(parts) >= 3:
            val_str, _, event_name = parts[0], parts[1], parts[2]
            # Match event name
            clean_event = event_name.replace("cpu_core/", "").replace("/u", "").replace("/", "")
            try:
                stats[clean_event] = float(val_str)
            except ValueError:
                pass

    return stats


def main():
    parser = argparse.ArgumentParser(description="Experiment 2: Microarchitectural Hardware Profiling")
    parser.add_argument("-b", "--bin-dir", default="bin", help="Directory containing perf binaries")
    parser.add_argument("-o", "--output", default="data/out/perf/hardware_counters.csv", help="Output CSV path")
    parser.add_argument("-c", "--core", type=int, default=0, help="CPU Core to pin execution (default 0)")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    proj_root = os.path.abspath(os.path.join(script_dir, "../../.."))

    bin_dir = args.bin_dir if os.path.isabs(args.bin_dir) else os.path.join(proj_root, args.bin_dir)
    output_path = args.output if os.path.isabs(args.output) else os.path.join(proj_root, args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print("=" * 80)
    print(" Experiment 2: Microarchitectural Profiling (perf stat)")
    print(f" CPU Core Pinned: {args.core}")
    print(f" Configs: Sparse (N=50,000, d=4), Dense (N=50,000, d=128)")
    print("=" * 80)

    results = []

    for config in CONFIGS:
        for mode in MODES:
            for variant in VARIANTS:
                bin_name = variant
                binary_path = os.path.join(bin_dir, bin_name)

                if not os.path.exists(binary_path):
                    print(f"[SKIP] Binary not found: {binary_path}")
                    continue

                # Skip dense decrease_key for brodal-okasaki (O(M*N) search would take ~30 mins)
                if variant == "brodal-okasaki" and config == "dense" and mode == "decrease_key":
                    print(f"[*] Running {variant:<15} [{config:<6} | {mode:<12}] ... SKIPPED (O(M*N) Functional Bound)")
                    results.append({
                        "variant": variant,
                        "config": config,
                        "mode": mode,
                        "L1_loads": "",
                        "L1_misses": "",
                        "L1_miss_rate_pct": "",
                        "LLC_loads": "",
                        "LLC_misses": "",
                        "LLC_miss_rate_pct": "",
                        "branches": "",
                        "branch_misses": "",
                        "branch_miss_rate_pct": "",
                        "cycles": "",
                        "instructions": "",
                        "IPC": "",
                        "note": "Skipped: O(M*N) functional tree search exceeds timeout",
                    })
                    continue

                iters = 2 if config == "sparse" else 1
                sys.stdout.write(f"[*] Running {variant:<15} [{config:<6} | {mode:<12}] (iters={iters}) ... ")
                sys.stdout.flush()

                stats = run_perf_stat(binary_path, config, mode, iters=iters, core_id=args.core)
                if not stats:
                    print("FAILED")
                    continue

                l1_loads = stats.get("L1-dcache-loads", 0)
                l1_misses = stats.get("L1-dcache-load-misses", 0)
                llc_loads = stats.get("LLC-loads", 0)
                llc_misses = stats.get("LLC-load-misses", 0)
                branches = stats.get("branch-instructions", 0)
                branch_misses = stats.get("branch-misses", 0)
                cycles = stats.get("cycles", 0)
                instructions = stats.get("instructions", 0)

                l1_miss_rate = (l1_misses / l1_loads * 100.0) if l1_loads > 0 else 0.0
                llc_miss_rate = (llc_misses / llc_loads * 100.0) if llc_loads > 0 else 0.0
                branch_miss_rate = (branch_misses / branches * 100.0) if branches > 0 else 0.0
                ipc = (instructions / cycles) if cycles > 0 else 0.0

                print(f"OK [L1 Miss: {l1_miss_rate:5.2f}% | LLC Miss: {llc_miss_rate:5.2f}% | IPC: {ipc:4.2f}]")

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
                    "note": "",
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
