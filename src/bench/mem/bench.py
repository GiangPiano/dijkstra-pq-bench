#!/usr/bin/env python3
"""
Experiment 3: Memory Footprint & Allocator Pressure Runner
Orchestrates memory profiling across priority queue variants.
Captures peak heap allocation, total allocator calls, memory leaks, and OS Peak RSS.
"""

import argparse
import csv
import os
import subprocess
import sys

VARIANTS = ["binary", "pairing", "fibonacci", "brodal-okasaki"]
CONFIGS = ["sparse", "dense"]
MODES = ["decrease_key", "lazy"]

N_VERTICES = 50000


def run_mem_prof(binary_path, config, mode, timeout_s=120):
    """
    Executes binary and parses CSV output line.
    """
    cmd = [binary_path, config, mode]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout_s)
    except subprocess.TimeoutExpired:
        print(f" [TIMEOUT after {timeout_s}s]", file=sys.stderr)
        return None

    if proc.returncode != 0:
        print(f" [ERROR code {proc.returncode}] {proc.stderr.strip()}", file=sys.stderr)
        return None

    # Parse stdout CSV line
    for line in proc.stdout.splitlines():
        parts = line.strip().split(",")
        if len(parts) >= 10:
            return {
                "config": parts[0],
                "mode": parts[1],
                "peak_heap_bytes": int(parts[2]),
                "total_allocated_bytes": int(parts[3]),
                "malloc_count": int(parts[4]),
                "free_count": int(parts[5]),
                "realloc_count": int(parts[6]),
                "leaked_bytes": int(parts[7]),
                "peak_rss_kib": int(parts[8]),
                "elapsed_ns": int(parts[9]),
            }
    return None


def main():
    parser = argparse.ArgumentParser(description="Experiment 3: Memory Footprint & Allocator Pressure")
    parser.add_argument("-b", "--bin-dir", default="bin", help="Directory containing mem binaries")
    parser.add_argument("-o", "--output", default="data/out/memory/memory_footprint.csv", help="Output CSV path")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    proj_root = os.path.abspath(os.path.join(script_dir, "../../.."))

    bin_dir = args.bin_dir if os.path.isabs(args.bin_dir) else os.path.join(proj_root, args.bin_dir)
    output_path = args.output if os.path.isabs(args.output) else os.path.join(proj_root, args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print("=" * 88)
    print(" Experiment 3: Memory Footprint & Allocator Pressure")
    print(" Configurations: Sparse (N=50,000, d=4), Dense (N=50,000, d=128)")
    print("=" * 88)

    results = []

    for config in CONFIGS:
        for mode in MODES:
            for variant in VARIANTS:
                bin_name = variant
                binary_path = os.path.join(bin_dir, bin_name)

                if not os.path.exists(binary_path):
                    print(f"[SKIP] Binary not found: {binary_path}")
                    continue

                # Theoretical bound skip: Brodal-Okasaki dense decrease_key has O(M*N) runtime
                if variant == "brodal-okasaki" and config == "dense" and mode == "decrease_key":
                    print(f"[-] {variant:<15} | {config:<7} | {mode:<12} -> SKIPPED (O(M*N) Functional Bound)")
                    results.append({
                        "variant": variant,
                        "config": config,
                        "mode": mode,
                        "peak_heap_bytes": "",
                        "peak_heap_kib": "",
                        "peak_heap_mib": "",
                        "total_allocated_bytes": "",
                        "malloc_count": "",
                        "free_count": "",
                        "realloc_count": "",
                        "leaked_bytes": "",
                        "peak_rss_kib": "",
                        "peak_rss_mib": "",
                        "elapsed_ms": "",
                        "bytes_per_vertex": "",
                    })
                    continue

                print(f"[*] Profiling: {variant:<15} | {config:<7} | {mode:<12} ...", end="", flush=True)

                stats = run_mem_prof(binary_path, config, mode)
                if stats is None:
                    print(" FAILED")
                    continue

                peak_kib = stats["peak_heap_bytes"] / 1024.0
                peak_mib = stats["peak_heap_bytes"] / (1024.0 * 1024.0)
                rss_mib = stats["peak_rss_kib"] / 1024.0
                elapsed_ms = stats["elapsed_ns"] / 1000000.0
                bpv = stats["peak_heap_bytes"] / float(N_VERTICES)

                print(f" Peak Heap: {peak_kib:>9.1f} KiB | RSS: {rss_mib:>6.1f} MiB | "
                      f"Mallocs: {stats['malloc_count']:>9,d} | Time: {elapsed_ms:>7.1f} ms")

                results.append({
                    "variant": variant,
                    "config": config,
                    "mode": mode,
                    "peak_heap_bytes": stats["peak_heap_bytes"],
                    "peak_heap_kib": f"{peak_kib:.2f}",
                    "peak_heap_mib": f"{peak_mib:.2f}",
                    "total_allocated_bytes": stats["total_allocated_bytes"],
                    "malloc_count": stats["malloc_count"],
                    "free_count": stats["free_count"],
                    "realloc_count": stats["realloc_count"],
                    "leaked_bytes": stats["leaked_bytes"],
                    "peak_rss_kib": stats["peak_rss_kib"],
                    "peak_rss_mib": f"{rss_mib:.2f}",
                    "elapsed_ms": f"{elapsed_ms:.2f}",
                    "bytes_per_vertex": f"{bpv:.1f}",
                })

    # Write CSV
    fieldnames = [
        "variant", "config", "mode",
        "peak_heap_bytes", "peak_heap_kib", "peak_heap_mib",
        "total_allocated_bytes", "malloc_count", "free_count", "realloc_count",
        "leaked_bytes", "peak_rss_kib", "peak_rss_mib", "elapsed_ms", "bytes_per_vertex"
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    print("\n" + "=" * 88)
    print(f"[SUCCESS] Memory profiling complete. Results saved to: {output_path}")
    print("=" * 88)


if __name__ == "__main__":
    main()
