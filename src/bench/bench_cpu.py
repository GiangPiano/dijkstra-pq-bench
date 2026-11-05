#!/usr/bin/env python3
"""
Print the CPU number the benchmarks should be pinned to, or nothing if
pinning is not supported here (e.g. macOS).

Choice, restricted to CPUs this process is allowed to run on:
  1. Intel hybrid CPUs (Alder Lake, Meteor Lake, ...): the performance cores
     listed in /sys/devices/cpu_core/cpus. E-cores have smaller L1/L2 caches
     and the low-power E-cores on Meteor Lake have no L3 at all, so where a
     run lands would otherwise change which cache level a graph fits in.
  2. Other asymmetric CPUs (ARM big.LITTLE): the CPUs with the highest
     /sys/devices/system/cpu/cpuN/cpu_capacity.
  3. Everything else: any allowed CPU.
The physical core holding CPU 0 (including its hyperthread sibling) is
avoided when there is a choice, because CPU 0 usually services more
interrupts and housekeeping work than the others.
"""

import glob
import os
import re


def parse_cpu_list(text):
    """Parse a kernel CPU list such as '0-3,8,10-11'."""
    cpus = set()
    for part in text.strip().split(","):
        if not part:
            continue
        lo, _, hi = part.partition("-")
        cpus.update(range(int(lo), int(hi or lo) + 1))
    return cpus


def read(path):
    try:
        with open(path, encoding="ascii") as f:
            return f.read()
    except OSError:
        return None


def performance_cpus(allowed):
    hybrid = read("/sys/devices/cpu_core/cpus")
    if hybrid:
        cores = parse_cpu_list(hybrid) & allowed
        if cores:
            return cores

    capacity = {}
    for path in glob.glob("/sys/devices/system/cpu/cpu[0-9]*/cpu_capacity"):
        value = read(path)
        cpu = int(re.search(r"cpu(\d+)/cpu_capacity$", path).group(1))
        if value and cpu in allowed:
            capacity[cpu] = int(value)
    if capacity and len(set(capacity.values())) > 1:
        best = max(capacity.values())
        return {cpu for cpu, cap in capacity.items() if cap == best}

    return allowed


def main():
    if not hasattr(os, "sched_getaffinity"):
        return  # not Linux: run unpinned
    allowed = os.sched_getaffinity(0)
    candidates = performance_cpus(allowed) or allowed
    cpu0_core = parse_cpu_list(
        read("/sys/devices/system/cpu/cpu0/topology/thread_siblings_list") or "0")
    preferred = candidates - cpu0_core or candidates
    print(min(preferred))


if __name__ == "__main__":
    main()
