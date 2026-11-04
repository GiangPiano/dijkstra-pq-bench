#!/usr/bin/env python3
"""
Experiment 3 Plotter (plot2.py)
Reads data/out/memory/memory_footprint.csv and generates publication-grade
vector SVG charts, Markdown tables, and LaTeX tables for the report.
"""

import argparse
import csv
import math
import os
import sys

BENCH_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BENCH_DIR not in sys.path:
    sys.path.insert(0, BENCH_DIR)

from plotting import (chart_layout, draw_axes, draw_category_label,
                      draw_legend, esc, get_color, svg_open)


def read_memory_csv(csv_path):
    if not os.path.exists(csv_path):
        print(f"[ERROR] CSV not found: {csv_path}", file=sys.stderr)
        return []

    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def generate_bar_svg(title, subtitle, y_axis_label, rows, metric_key, val_formatter, output_path, max_limit=None, log_scale=False):
    """
    Renders grouped bar chart for metric_key across generated configurations and modes.
    """
    configs = sorted({r["config"] for r in rows})
    modes = ["decrease_key", "lazy"]
    group_keys = [
        (config, mode, f"{config}\n{mode.replace('_', ' ').title()}")
        for config in configs
        for mode in modes
        if any(r["config"] == config and r["mode"] == mode for r in rows)
    ]

    variants = sorted({r["variant"] for r in rows})
    layout = chart_layout(len(group_keys), min_group_width=115)
    width = layout["width"]
    height = layout["height"]
    pad_left = layout["pad_left"]
    pad_top = layout["pad_top"]
    plot_h = layout["plot_height"]

    all_vals = []
    lookup = {}
    for r in rows:
        cfg = r["config"]
        m = r["mode"]
        v = r["variant"]
        val_str = r.get(metric_key, "")
        if val_str != "":
            try:
                val = float(val_str)
                lookup[(cfg, m, v)] = val
                if max_limit is None or val <= max_limit:
                    all_vals.append(val)
            except ValueError:
                pass

    if not all_vals:
        return

    if log_scale:
        positive_vals = [v for v in all_vals if v > 0]
        min_log = 0.0
        max_log = math.ceil(math.log10(max(positive_vals))) if positive_vals else 6.0
        if max_log < 1.0:
            max_log = 1.0
        ticks = [10 ** i for i in range(int(max_log) + 1)]
    else:
        max_val = (max(all_vals) * 1.25) if all_vals else 100.0
        if max_limit and max_val > max_limit:
            max_val = max_limit
        num_ticks = 5
        ticks = [i * (max_val / num_ticks) for i in range(num_ticks + 1)]

    svg = svg_open(layout)

    svg.append(f'<text x="{pad_left}" y="32" class="chart-title">{esc(title)}</text>')
    svg.append(f'<text x="{pad_left}" y="50" class="chart-subtitle">{esc(subtitle)}</text>')

    draw_axes(
        svg, layout, ticks, max_log if log_scale else max_val, val_formatter,
        y_axis_label, log_scale=log_scale
    )

    # Grouped Bars
    num_groups = len(group_keys)
    group_width = layout["group_width"]
    num_vars = len(variants)
    bar_width = min(28.0, (group_width * 0.78) / max(num_vars, 1))

    for g_idx, (cfg, m, label) in enumerate(group_keys):
        g_center = pad_left + g_idx * group_width + group_width / 2

        draw_category_label(svg, g_center, height - layout["pad_bottom"] + 18,
                            label.replace("\n", " "), group_width)

        start_x = g_center - (num_vars * bar_width) / 2

        for v_idx, v in enumerate(variants):
            x = start_x + v_idx * bar_width
            color = get_color(v, v_idx)

            key = (cfg, m, v)
            if key in lookup:
                val = lookup[key]
                if log_scale:
                    if val <= 1:
                        bar_h = 2.0
                    else:
                        clamped_log = min(math.log10(val), max_log)
                        bar_h = (clamped_log / max_log) * plot_h
                else:
                    clamped_val = min(val, max_val)
                    bar_h = (clamped_val / max_val) * plot_h

                y = pad_top + plot_h - bar_h

                svg.append(f'<rect x="{x + 2:.1f}" y="{y:.1f}" width="{bar_width - 4:.1f}" height="{bar_h:.1f}" '
                           f'fill="{color}" rx="3" ry="3"><title>{esc(v)} ({esc(cfg)}, {esc(m)}): {esc(val_formatter(val))}</title></rect>')

                label_text = val_formatter(val)
                svg.append(f'<text x="{x + bar_width / 2:.1f}" y="{max(pad_top + 10, y - 4):.1f}" class="bar-label">{esc(label_text)}</text>')
            else:
                svg.append(f'<text x="{x + bar_width / 2:.1f}" y="{height - layout["pad_bottom"] - 8}" class="bar-label" fill="#94A3B8">N/A</text>')

    draw_legend(svg, variants, layout)

    svg.append('</svg>')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"[PLOT] Generated {output_path}")


def generate_tables(rows, out_md_path, out_tex_path):
    """Generates Markdown and LaTeX summary tables."""
    # 1. Markdown Table
    md = []
    md.append("# Experiment 3: Memory Footprint & Allocator Pressure\n")
    md.append("| Variant | Config | Mode | Peak Heap (KiB) | Peak RSS (MiB) | Malloc Calls | Free Calls | Total Alloc (KiB) | Bytes/Vertex |")
    md.append("|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|")

    for r in rows:
        v = r["variant"]
        cfg = r["config"]
        m = r["mode"]
        pk_heap = f"{float(r['peak_heap_kib']):,.1f}" if r["peak_heap_kib"] else "N/A"
        pk_rss = f"{float(r['peak_rss_mib']):,.1f}" if r["peak_rss_mib"] else "N/A"
        m_calls = f"{int(r['malloc_count']):,}" if r["malloc_count"] else "N/A"
        f_calls = f"{int(r['free_count']):,}" if r["free_count"] else "N/A"
        tot_alloc = f"{int(r['total_allocated_bytes']) / 1024.0:,.1f}" if r["total_allocated_bytes"] else "N/A"
        bpv = f"{float(r['bytes_per_vertex']):.1f}" if r["bytes_per_vertex"] else "N/A"

        md.append(f"| {v} | {cfg} | {m} | {pk_heap} | {pk_rss} | {m_calls} | {f_calls} | {tot_alloc} | {bpv} |")

    with open(out_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print(f"[TABLE] Generated {out_md_path}")

    # 2. LaTeX Table
    tex = []
    tex.append("% Auto-generated by src/bench/bench2/plot2.py")
    tex.append("\\begin{table}[H]")
    tex.append("  \\centering")
    tex.append("  \\small")
    tex.append("  \\caption{Memory Footprint and Dynamic Allocator Pressure ($N=50{,}000$)}")
    tex.append("  \\label{tab:memory_footprint}")
    tex.append("  \\begin{tabular}{lllrrrrr}")
    tex.append("    \\toprule")
    tex.append("    \\textbf{Variant} & \\textbf{Config} & \\textbf{Mode} & \\textbf{Peak Heap (KiB)} & \\textbf{Peak RSS (MiB)} & \\textbf{Mallocs} & \\textbf{Frees} & \\textbf{B/Vertex} \\\\")
    tex.append("    \\midrule")

    curr_cfg = None
    for r in rows:
        cfg = r["config"]
        if curr_cfg != cfg:
            if curr_cfg is not None:
                tex.append("    \\addlinespace")
            curr_cfg = cfg

        v = r["variant"]
        m = "Decr-Key" if r["mode"] == "decrease_key" else "Lazy"
        pk_heap = f"{float(r['peak_heap_kib']):,.1f}" if r["peak_heap_kib"] else "---"
        pk_rss = f"{float(r['peak_rss_mib']):,.1f}" if r["peak_rss_mib"] else "---"
        m_calls = f"{int(r['malloc_count']):,}" if r["malloc_count"] else "---"
        f_calls = f"{int(r['free_count']):,}" if r["free_count"] else "---"
        bpv = f"{float(r['bytes_per_vertex']):.1f}" if r["bytes_per_vertex"] else "---"

        tex.append(f"    {v} & {cfg} & {m} & {pk_heap} & {pk_rss} & {m_calls} & {f_calls} & {bpv} \\\\")

    tex.append("    \\bottomrule")
    tex.append("  \\end{tabular}")
    tex.append("\\end{table}")

    with open(out_tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(tex) + "\n")
    print(f"[TABLE] Generated {out_tex_path}")


def main():
    parser = argparse.ArgumentParser(description="Experiment 3 Plotter (plot2.py)")
    parser.add_argument("-i", "--input", default="data/out/memory/memory_footprint.csv", help="Input CSV")
    parser.add_argument("-o", "--output-dir", default="report/figures/memory", help="Output directory")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    proj_root = os.path.abspath(os.path.join(script_dir, "../../.."))

    input_path = args.input if os.path.isabs(args.input) else os.path.join(proj_root, args.input)
    output_dir = args.output_dir if os.path.isabs(args.output_dir) else os.path.join(proj_root, args.output_dir)

    os.makedirs(output_dir, exist_ok=True)

    rows = read_memory_csv(input_path)
    if not rows:
        print("[ERROR] No data in CSV. Run `make mem-run` first.", file=sys.stderr)
        sys.exit(1)

    # 1. Peak Heap Memory Allocation Plot
    generate_bar_svg(
        title="Peak Heap Memory Allocation (KiB) across Priority Queues",
        subtitle="Maximum live heap bytes held simultaneously during Dijkstra execution (lower is better)",
        y_axis_label="Peak Heap Allocation (KiB)",
        rows=rows,
        metric_key="peak_heap_kib",
        val_formatter=lambda x: f"{x:,.0f}K" if x >= 1000 else f"{x:.0f}K",
        output_path=os.path.join(output_dir, "peak_heap_memory.svg"),
        max_limit=None
    )

    # 2. Allocator Pressure (Malloc Calls) - Log Scale
    generate_bar_svg(
        title="Dynamic Allocator Pressure (Total malloc calls)",
        subtitle="Heap allocations invoked during search — High churn induces fragmentation and allocator lock contention",
        y_axis_label="Total malloc() Calls (log scale)",
        rows=rows,
        metric_key="malloc_count",
        val_formatter=lambda x: f"{x/1e6:.1f}M" if x >= 1e6 else (f"{x/1e3:.0f}k" if x >= 1e3 else f"{x:.0f}"),
        output_path=os.path.join(output_dir, "allocator_pressure.svg"),
        max_limit=None,
        log_scale=True
    )

    # 3. Peak Resident Set Size (RSS in MiB)
    generate_bar_svg(
        title="Peak Resident Set Size (RSS in MiB)",
        subtitle="Physical memory pages committed by OS kernel — Includes graph CSR, dist array & priority queue",
        y_axis_label="Peak RSS (MiB)",
        rows=rows,
        metric_key="peak_rss_mib",
        val_formatter=lambda x: f"{x:.1f} MB",
        output_path=os.path.join(output_dir, "peak_rss_footprint.svg"),
        max_limit=None
    )

    # 4. Tables
    generate_tables(
        rows=rows,
        out_md_path=os.path.join(output_dir, "mem.md"),
        out_tex_path=os.path.join(output_dir, "mem.tex")
    )

    print(f"\n[SUCCESS] Experiment 3 plots and tables generated in {output_dir}")


if __name__ == "__main__":
    main()
