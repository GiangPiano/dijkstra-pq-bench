#!/usr/bin/env python3
"""
Experiment 3 Plotter (plot2.py)
Reads data/out/memory/memory_footprint.csv and generates publication-grade
vector SVG charts, Markdown tables, and LaTeX tables for the report.
"""

import argparse
import csv
import html
import math
import os
import sys

VARIANT_COLORS = {
    "binary": "#2563EB",         # Royal Blue
    "pairing": "#16A34A",        # Emerald Green
    "fibonacci": "#9333EA",      # Vibrant Purple
    "brodal-okasaki": "#EA580C", # Deep Orange
    "stub": "#6B7280",           # Gray
}
DEFAULT_COLORS = ["#2563EB", "#16A34A", "#9333EA", "#EA580C"]


def esc(val):
    """Escapes string for safe XML/SVG embedding."""
    return html.escape(str(val), quote=True)


def get_color(variant, idx=0):
    return VARIANT_COLORS.get(variant, DEFAULT_COLORS[idx % len(DEFAULT_COLORS)])


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
    Renders grouped bar chart for metric_key across (sparse, dense) and modes.
    """
    width = 760
    height = 460
    pad_left = 90
    pad_right = 40
    pad_top = 70
    pad_bottom = 90

    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom

    group_keys = [
        ("sparse", "decrease_key", "Sparse (d=4)\nDecrease-Key"),
        ("sparse", "lazy", "Sparse (d=4)\nLazy"),
        ("dense", "decrease_key", "Dense (d=128)\nDecrease-Key"),
        ("dense", "lazy", "Dense (d=128)\nLazy"),
    ]

    variants = ["binary", "pairing", "fibonacci", "brodal-okasaki"]

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

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
               f'width="{width}" height="{height}" style="background-color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif;">')

    svg.append('<defs>')
    svg.append('  <style>')
    svg.append('    .axis { stroke: #CBD5E1; stroke-width: 1; }')
    svg.append('    .grid { stroke: #F1F5F9; stroke-width: 1; stroke-dasharray: 4,4; }')
    svg.append('    .tick-label { font-size: 11px; fill: #64748B; }')
    svg.append('    .axis-title { font-size: 12px; font-weight: 600; fill: #334155; }')
    svg.append('    .chart-title { font-size: 16px; font-weight: 700; fill: #0F172A; }')
    svg.append('    .chart-subtitle { font-size: 12px; fill: #64748B; }')
    svg.append('    .bar-label { font-size: 9px; font-weight: 600; fill: #1E293B; text-anchor: middle; }')
    svg.append('    .legend-text { font-size: 12px; fill: #334155; font-weight: 500; dominant-baseline: central; }')
    svg.append('  </style>')
    svg.append('</defs>')

    svg.append(f'<text x="{pad_left}" y="32" class="chart-title">{esc(title)}</text>')
    svg.append(f'<text x="{pad_left}" y="50" class="chart-subtitle">{esc(subtitle)}</text>')

    # Y-axis Grid & Ticks
    for val in ticks:
        if log_scale:
            if val <= 1:
                y = pad_top + plot_h
            else:
                y = pad_top + plot_h - (math.log10(val) / max_log) * plot_h
            tick_str = f"10^{int(math.log10(val))}" if val > 1 else "1"
        else:
            y = pad_top + plot_h - (val / max_val) * plot_h
            tick_str = val_formatter(val)

        svg.append(f'<line x1="{pad_left}" y1="{y:.1f}" x2="{width - pad_right}" y2="{y:.1f}" class="grid" />')
        svg.append(f'<text x="{pad_left - 10}" y="{y + 4:.1f}" class="tick-label" text-anchor="end">{esc(tick_str)}</text>')

    # Axes
    svg.append(f'<line x1="{pad_left}" y1="{pad_top}" x2="{pad_left}" y2="{height - pad_bottom}" class="axis" />')
    svg.append(f'<line x1="{pad_left}" y1="{height - pad_bottom}" x2="{width - pad_right}" y2="{height - pad_bottom}" class="axis" />')
    svg.append(f'<text x="-{(pad_top + plot_h / 2):.1f}" y="20" class="axis-title" text-anchor="middle" transform="rotate(-90)">{esc(y_axis_label)}</text>')

    # Grouped Bars
    num_groups = len(group_keys)
    group_width = plot_w / num_groups
    num_vars = len(variants)
    bar_width = min(28.0, (group_width * 0.78) / max(num_vars, 1))

    for g_idx, (cfg, m, label) in enumerate(group_keys):
        g_center = pad_left + g_idx * group_width + group_width / 2

        # Multi-line label under x-axis
        lines = label.split("\n")
        svg.append(f'<text x="{g_center:.1f}" y="{height - pad_bottom + 18}" class="axis-title" font-size="11px" text-anchor="middle">{esc(lines[0])}</text>')
        if len(lines) > 1:
            svg.append(f'<text x="{g_center:.1f}" y="{height - pad_bottom + 32}" class="tick-label" font-weight="600" text-anchor="middle">{esc(lines[1])}</text>')

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
                svg.append(f'<text x="{x + bar_width / 2:.1f}" y="{height - pad_bottom - 8}" class="bar-label" fill="#94A3B8">N/A</text>')

    # Legend Below X-Axis
    leg_y = height - pad_bottom + 62
    item_spacing = 145
    total_w = len(variants) * item_spacing
    start_lx = max(pad_left, (width - total_w) / 2)
    for v_idx, v in enumerate(variants):
        lx = start_lx + v_idx * item_spacing
        color = get_color(v, v_idx)
        svg.append(f'<rect x="{lx:.1f}" y="{leg_y - 7:.1f}" width="14" height="14" fill="{color}" rx="3" ry="3" />')
        svg.append(f'<text x="{lx + 20:.1f}" y="{leg_y:.1f}" class="legend-text">{esc(v)}</text>')

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
        out_md_path=os.path.join(output_dir, "memory_summary_table.md"),
        out_tex_path=os.path.join(output_dir, "memory_summary_table.tex")
    )

    print(f"\n[SUCCESS] Experiment 3 plots and tables generated in {output_dir}")


if __name__ == "__main__":
    main()
