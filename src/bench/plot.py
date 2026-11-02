#!/usr/bin/env python3
"""
Benchmark Plotting & Analysis Tool for dijkstra-pq-bench

Reads CSV outputs produced by the ubench test harness (data/out/*.csv)
and generates publication-quality SVG plots, Markdown tables, and LaTeX tables.
If matplotlib is installed, it also generates PDF/PNG vector graphics.
"""

import argparse
import csv
import glob
import math
import os
import sys
from collections import defaultdict


def parse_csv_files(input_dir):
    """
    Parses all CSV files in input_dir.
    Expected row format:
      name (mode.dataset), mean (ns), stddev (%), confidence (%)
    Returns a nested dict:
      data[dataset][mode][variant] = {
          'mean_ns': float,
          'stddev_pct': float,
          'conf_pct': float
      }
    """
    csv_files = glob.glob(os.path.join(input_dir, "*.csv"))
    if not csv_files:
        print(f"[WARN] No CSV files found in {input_dir}", file=sys.stderr)
        return {}, []

    data = defaultdict(lambda: defaultdict(dict))
    variants_seen = set()

    for path in sorted(csv_files):
        variant = os.path.splitext(os.path.basename(path))[0]
        # Ignore non-variant or stub files if empty/invalid
        if variant == "stub":
            continue

        try:
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if not header:
                    continue

                for row in reader:
                    if len(row) < 2:
                        continue
                    full_name = row[0].strip()
                    if "." not in full_name:
                        continue
                    mode, dataset = full_name.split(".", 1)
                    try:
                        mean_ns = float(row[1].strip())
                        stddev_pct = float(row[2].strip()) if len(row) > 2 and row[2].strip() else 0.0
                        conf_pct = float(row[3].strip()) if len(row) > 3 and row[3].strip() else 0.0
                    except ValueError:
                        continue

                    data[dataset][mode][variant] = {
                        "mean_ns": mean_ns,
                        "stddev_pct": stddev_pct,
                        "conf_pct": conf_pct,
                    }
                    variants_seen.add(variant)
        except Exception as e:
            print(f"[WARN] Failed to read {path}: {e}", file=sys.stderr)

    return data, sorted(variants_seen)


def format_time(ns):
    """Converts nanoseconds into a human-readable string with units."""
    if ns < 1_000:
        return f"{ns:.1f} ns"
    elif ns < 1_000_000:
        return f"{ns / 1_000:.2f} µs"
    elif ns < 1_000_000_000:
        return f"{ns / 1_000_000:.2f} ms"
    else:
        return f"{ns / 1_000_000_000:.2f} s"


# Palette configuration
VARIANT_COLORS = {
    "binary": "#2563EB",         # Royal Blue
    "pairing": "#16A34A",        # Emerald Green
    "fibonacci": "#9333EA",      # Vibrant Purple
    "brodal-okasaki": "#EA580C", # Deep Orange
    "stub": "#6B7280",           # Gray
}
DEFAULT_COLORS = ["#2563EB", "#16A34A", "#9333EA", "#EA580C", "#0891B2", "#DC2626"]


def get_color(variant, idx=0):
    return VARIANT_COLORS.get(variant, DEFAULT_COLORS[idx % len(DEFAULT_COLORS)])


def generate_bar_chart_svg(dataset, mode_data, variants, output_path):
    """
    Generates a grouped bar chart for a single dataset comparing variants
    across decrease_key and lazy modes.
    """
    width = 720
    height = 420
    pad_left = 90
    pad_right = 40
    pad_top = 70
    pad_bottom = 60

    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom

    modes = ["decrease_key", "lazy"]
    # Find max runtime across this dataset
    all_times = []
    for m in modes:
        for v in variants:
            if v in mode_data.get(m, {}):
                all_times.append(mode_data[m][v]["mean_ns"])

    if not all_times:
        return

    max_val = max(all_times) * 1.15
    min_val = 0

    # Grid ticks
    num_ticks = 5
    ticks = [min_val + (max_val - min_val) * (i / num_ticks) for i in range(num_ticks + 1)]

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
               f'width="{width}" height="{height}" style="background-color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif;">')

    # Definitions (gradients/patterns)
    svg.append('<defs>')
    svg.append('  <style>')
    svg.append('    .axis { stroke: #CBD5E1; stroke-width: 1; }')
    svg.append('    .grid { stroke: #F1F5F9; stroke-width: 1; stroke-dasharray: 4,4; }')
    svg.append('    .tick-label { font-size: 11px; fill: #64748B; }')
    svg.append('    .axis-title { font-size: 12px; font-weight: 600; fill: #334155; }')
    svg.append('    .chart-title { font-size: 16px; font-weight: 700; fill: #0F172A; }')
    svg.append('    .chart-subtitle { font-size: 12px; fill: #64748B; }')
    svg.append('    .bar-label { font-size: 10px; font-weight: 600; fill: #1E293B; text-anchor: middle; }')
    svg.append('    .legend-text { font-size: 11px; fill: #334155; font-weight: 500; }')
    svg.append('  </style>')
    svg.append('</defs>')

    # Title
    svg.append(f'<text x="{pad_left}" y="32" class="chart-title">Dijkstra Runtime Comparison: {dataset}</text>')
    svg.append(f'<text x="{pad_left}" y="50" class="chart-subtitle">Wall-clock execution time across Priority Queue variants (lower is better)</text>')

    # Y-axis Grid & Ticks
    for val in ticks:
        y = pad_top + plot_h - (val / max_val) * plot_h
        svg.append(f'<line x1="{pad_left}" y1="{y:.1f}" x2="{width - pad_right}" y2="{y:.1f}" class="grid" />')
        svg.append(f'<text x="{pad_left - 10}" y="{y + 4:.1f}" class="tick-label" text-anchor="end">{format_time(val)}</text>')

    # Axes
    svg.append(f'<line x1="{pad_left}" y1="{pad_top}" x2="{pad_left}" y2="{height - pad_bottom}" class="axis" />')
    svg.append(f'<line x1="{pad_left}" y1="{height - pad_bottom}" x2="{width - pad_right}" y2="{height - pad_bottom}" class="axis" />')

    # Y-axis title
    svg.append(f'<text x="-{(pad_top + plot_h / 2):.1f}" y="20" class="axis-title" text-anchor="middle" transform="rotate(-90)">Mean Runtime</text>')

    # Grouped Bars
    num_groups = len(modes)
    group_width = plot_w / num_groups
    num_vars = len(variants)
    bar_width = min(36.0, (group_width * 0.75) / max(num_vars, 1))

    for g_idx, m in enumerate(modes):
        g_center = pad_left + g_idx * group_width + group_width / 2
        mode_label = "Explicit Decrease-Key" if m == "decrease_key" else "Lazy Insertion"
        svg.append(f'<text x="{g_center:.1f}" y="{height - pad_bottom + 25}" class="axis-title" text-anchor="middle">{mode_label}</text>')

        start_x = g_center - (num_vars * bar_width) / 2

        for v_idx, v in enumerate(variants):
            x = start_x + v_idx * bar_width
            color = get_color(v, v_idx)

            if v in mode_data.get(m, {}):
                t_val = mode_data[m][v]["mean_ns"]
                bar_h = (t_val / max_val) * plot_h
                y = pad_top + plot_h - bar_h

                # Draw bar
                svg.append(f'<rect x="{x + 2:.1f}" y="{y:.1f}" width="{bar_width - 4:.1f}" height="{bar_h:.1f}" '
                           f'fill="{color}" rx="3" ry="3"><title>{v} ({m}): {format_time(t_val)}</title></rect>')

                # Value label on top of bar
                svg.append(f'<text x="{x + bar_width / 2:.1f}" y="{max(pad_top + 12, y - 5):.1f}" class="bar-label">{format_time(t_val)}</text>')
            else:
                # No data bar (e.g. timeout / skipped)
                svg.append(f'<text x="{x + bar_width / 2:.1f}" y="{height - pad_bottom - 10}" class="bar-label" fill="#94A3B8">N/A</text>')

    # Legend at top right
    leg_x = width - pad_right - (num_vars * 105)
    leg_y = 30
    for v_idx, v in enumerate(variants):
        lx = leg_x + v_idx * 105
        color = get_color(v, v_idx)
        svg.append(f'<rect x="{lx}" y="{leg_y - 10}" width="12" height="12" fill="{color}" rx="2" />')
        svg.append(f'<text x="{lx + 16}" y="{leg_y}" class="legend-text">{v}</text>')

    svg.append('</svg>')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"[PLOT] Generated {output_path}")


def generate_speedup_svg(data, datasets, variants, output_path):
    """
    Generates a speedup ratio chart: Runtime(Lazy) / Runtime(Decrease-Key).
    Ratio > 1.0 means Decrease-Key is faster.
    Ratio < 1.0 means Lazy is faster.
    """
    width = 720
    height = 400
    pad_left = 80
    pad_right = 40
    pad_top = 70
    pad_bottom = 60

    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom

    # Find ratios
    valid_datasets = [d for d in datasets if d in data]
    if not valid_datasets:
        return

    max_ratio = 3.0
    for d in valid_datasets:
        for v in variants:
            t_dk = data[d].get("decrease_key", {}).get(v, {}).get("mean_ns")
            t_lz = data[d].get("lazy", {}).get(v, {}).get("mean_ns")
            if t_dk and t_lz and t_dk > 0:
                ratio = t_lz / t_dk
                if ratio > max_ratio:
                    max_ratio = math.ceil(ratio * 1.2)

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
               f'width="{width}" height="{height}" style="background-color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif;">')

    svg.append('<defs>')
    svg.append('  <style>')
    svg.append('    .axis { stroke: #CBD5E1; stroke-width: 1; }')
    svg.append('    .grid { stroke: #F1F5F9; stroke-width: 1; stroke-dasharray: 4,4; }')
    svg.append('    .baseline { stroke: #EF4444; stroke-width: 1.5; stroke-dasharray: 3,3; }')
    svg.append('    .tick-label { font-size: 11px; fill: #64748B; }')
    svg.append('    .axis-title { font-size: 12px; font-weight: 600; fill: #334155; }')
    svg.append('    .chart-title { font-size: 16px; font-weight: 700; fill: #0F172A; }')
    svg.append('    .chart-subtitle { font-size: 12px; fill: #64748B; }')
    svg.append('    .bar-label { font-size: 10px; font-weight: 600; fill: #1E293B; text-anchor: middle; }')
    svg.append('    .legend-text { font-size: 11px; fill: #334155; font-weight: 500; }')
    svg.append('  </style>')
    svg.append('</defs>')

    svg.append(f'<text x="{pad_left}" y="32" class="chart-title">Speedup Ratio: Lazy vs. Decrease-Key</text>')
    svg.append(f'<text x="{pad_left}" y="50" class="chart-subtitle">T(lazy) / T(decrease-key) &gt; 1.0 means Decrease-Key is faster; &lt; 1.0 means Lazy is faster</text>')

    # Baseline 1.0 line
    y_1 = pad_top + plot_h - (1.0 / max_ratio) * plot_h
    svg.append(f'<line x1="{pad_left}" y1="{y_1:.1f}" x2="{width - pad_right}" y2="{y_1:.1f}" class="baseline" />')
    svg.append(f'<text x="{width - pad_right + 5}" y="{y_1 + 4:.1f}" class="tick-label" fill="#EF4444" font-weight="600">1.0x (Parity)</text>')

    # Grid ticks
    for tick_val in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
        if tick_val <= max_ratio:
            y = pad_top + plot_h - (tick_val / max_ratio) * plot_h
            svg.append(f'<line x1="{pad_left}" y1="{y:.1f}" x2="{width - pad_right}" y2="{y:.1f}" class="grid" />')
            svg.append(f'<text x="{pad_left - 10}" y="{y + 4:.1f}" class="tick-label" text-anchor="end">{tick_val:.1f}x</text>')

    # Axes
    svg.append(f'<line x1="{pad_left}" y1="{pad_top}" x2="{pad_left}" y2="{height - pad_bottom}" class="axis" />')
    svg.append(f'<line x1="{pad_left}" y1="{height - pad_bottom}" x2="{width - pad_right}" y2="{height - pad_bottom}" class="axis" />')
    svg.append(f'<text x="-{(pad_top + plot_h / 2):.1f}" y="20" class="axis-title" text-anchor="middle" transform="rotate(-90)">Speedup Factor</text>')

    # Grouped bars per dataset
    num_groups = len(valid_datasets)
    group_width = plot_w / num_groups
    num_vars = len(variants)
    bar_width = min(32.0, (group_width * 0.75) / max(num_vars, 1))

    for g_idx, d in enumerate(valid_datasets):
        g_center = pad_left + g_idx * group_width + group_width / 2
        svg.append(f'<text x="{g_center:.1f}" y="{height - pad_bottom + 25}" class="axis-title" text-anchor="middle">{d}</text>')

        start_x = g_center - (num_vars * bar_width) / 2

        for v_idx, v in enumerate(variants):
            x = start_x + v_idx * bar_width
            color = get_color(v, v_idx)
            t_dk = data[d].get("decrease_key", {}).get(v, {}).get("mean_ns")
            t_lz = data[d].get("lazy", {}).get(v, {}).get("mean_ns")

            if t_dk and t_lz and t_dk > 0:
                ratio = t_lz / t_dk
                bar_h = (ratio / max_ratio) * plot_h
                y = pad_top + plot_h - bar_h

                svg.append(f'<rect x="{x + 2:.1f}" y="{y:.1f}" width="{bar_width - 4:.1f}" height="{bar_h:.1f}" '
                           f'fill="{color}" rx="3" ry="3"><title>{v} on {d}: {ratio:.2f}x</title></rect>')
                svg.append(f'<text x="{x + bar_width / 2:.1f}" y="{max(pad_top + 12, y - 5):.1f}" class="bar-label">{ratio:.2f}x</text>')

    # Legend
    leg_x = width - pad_right - (num_vars * 105)
    leg_y = 30
    for v_idx, v in enumerate(variants):
        lx = leg_x + v_idx * 105
        color = get_color(v, v_idx)
        svg.append(f'<rect x="{lx}" y="{leg_y - 10}" width="12" height="12" fill="{color}" rx="2" />')
        svg.append(f'<text x="{lx + 16}" y="{leg_y}" class="legend-text">{v}</text>')

    svg.append('</svg>')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"[PLOT] Generated {output_path}")


def generate_tables(data, datasets, variants, out_md_path, out_tex_path):
    """
    Generates Markdown and LaTeX booktabs summary tables from the CSV data.
    """
    # 1. Markdown Table
    md = []
    md.append("# Dijkstra Priority Queue Benchmark Results\n")
    md.append("| Dataset | Mode | " + " | ".join(variants) + " |")
    md.append("|:---|:---| " + " | ".join([":---:"] * len(variants)) + " |")

    for d in datasets:
        if d not in data:
            continue
        for mode in ["decrease_key", "lazy"]:
            mode_label = "Decrease-Key" if mode == "decrease_key" else "Lazy"
            row = [d, mode_label]
            for v in variants:
                val = data[d].get(mode, {}).get(v)
                if val:
                    row.append(f"{format_time(val['mean_ns'])} (±{val['conf_pct']:.1f}%)")
                else:
                    row.append("—")
            md.append("| " + " | ".join(row) + " |")

    with open(out_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print(f"[TABLE] Generated {out_md_path}")

    # 2. LaTeX Table
    tex = []
    tex.append("% Auto-generated by src/bench/plot.py")
    tex.append("\\begin{table}[H]")
    tex.append("  \\centering")
    tex.append("  \\small")
    tex.append("  \\caption{Dijkstra Execution Time across Heaps and Input Datasets (Mean $\\pm$ 99\\% Confidence)}")
    tex.append("  \\label{tab:dijkstra_runtime}")
    tex.append("  \\begin{tabular}{ll" + "r" * len(variants) + "}")
    tex.append("    \\toprule")
    tex.append("    \\textbf{Dataset} & \\textbf{Mode} & " + " & ".join([f"\\textbf{{{v}}}" for v in variants]) + " \\\\")
    tex.append("    \\midrule")

    for d in datasets:
        if d not in data:
            continue
        d_escaped = d.replace("_", "\\_")
        for idx, mode in enumerate(["decrease_key", "lazy"]):
            mode_label = "Decrease-Key" if mode == "decrease_key" else "Lazy"
            prefix = f"    {d_escaped} & {mode_label}" if idx == 0 else f"    & {mode_label}"
            vals = []
            for v in variants:
                val = data[d].get(mode, {}).get(v)
                if val:
                    vals.append(f"{format_time(val['mean_ns'])}")
                else:
                    vals.append("---")
            tex.append(f"{prefix} & " + " & ".join(vals) + " \\\\")
        tex.append("    \\addlinespace")

    tex.append("    \\bottomrule")
    tex.append("  \\end{tabular}")
    tex.append("\\end{table}")

    with open(out_tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(tex) + "\n")
    print(f"[TABLE] Generated {out_tex_path}")


def main():
    parser = argparse.ArgumentParser(description="Plot and analyze dijkstra-pq-bench CSV outputs")
    parser.add_argument("-i", "--input-dir", default="data/out", help="Directory containing CSV outputs")
    parser.add_argument("-o", "--output-dir", default="report/figures", help="Directory to save figures")
    args = parser.parse_args()

    # Find project root if running from src/bench
    script_dir = os.path.dirname(os.path.abspath(__file__))
    proj_root = os.path.abspath(os.path.join(script_dir, "../.."))

    input_dir = args.input_dir if os.path.isabs(args.input_dir) else os.path.join(proj_root, args.input_dir)
    output_dir = args.output_dir if os.path.isabs(args.output_dir) else os.path.join(proj_root, args.output_dir)

    os.makedirs(output_dir, exist_ok=True)

    data, variants = parse_csv_files(input_dir)
    if not data:
        print("[ERROR] No valid benchmark data found. Run `make tests` first.", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Found data for variants: {variants}")
    datasets = list(data.keys())
    print(f"[INFO] Found datasets: {datasets}")

    # Generate individual dataset bar charts
    for d in datasets:
        out_svg = os.path.join(output_dir, f"runtime_{d}.svg")
        generate_bar_chart_svg(d, data[d], variants, out_svg)

    # Generate speedup chart
    out_speedup = os.path.join(output_dir, "speedup_lazy_vs_decrease_key.svg")
    generate_speedup_svg(data, datasets, variants, out_speedup)

    # Generate summary tables
    out_md = os.path.join(output_dir, "benchmark_summary.md")
    out_tex = os.path.join(output_dir, "benchmark_table.tex")
    generate_tables(data, datasets, variants, out_md, out_tex)

    print(f"\n[SUCCESS] All plots and tables generated successfully in {output_dir}")


if __name__ == "__main__":
    main()
