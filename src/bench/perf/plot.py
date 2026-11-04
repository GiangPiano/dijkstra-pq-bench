#!/usr/bin/env python3
"""
Experiment 2 Plotter (plot1.py)
Reads data/out/perf/hardware_counters.csv and generates publication-grade
vector SVG charts, Markdown tables, and LaTeX tables for the report.
"""

import argparse
import csv
import os
import sys

BENCH_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BENCH_DIR not in sys.path:
    sys.path.insert(0, BENCH_DIR)

from plotting import (chart_layout, draw_axes, draw_category_label,
                      draw_legend, esc, get_color, svg_open)


def read_perf_csv(csv_path):
    if not os.path.exists(csv_path):
        print(f"[ERROR] CSV not found: {csv_path}", file=sys.stderr)
        return []

    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def generate_bar_svg(title, subtitle, y_axis_label, rows, metric_key, val_formatter, output_path, max_limit=None):
    """
    Renders grouped bar chart for metric_key across generated configurations and modes.
    """
    # Identify groups from the generated benchmark data.
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

    # Collect max value for y-axis scaling
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

    max_val = (max(all_vals) * 1.25) if all_vals else 100.0
    if max_limit and max_val > max_limit:
        max_val = max_limit

    num_ticks = 5
    ticks = [i * (max_val / num_ticks) for i in range(num_ticks + 1)]

    svg = svg_open(layout)

    svg.append(f'<text x="{pad_left}" y="32" class="chart-title">{esc(title)}</text>')
    svg.append(f'<text x="{pad_left}" y="50" class="chart-subtitle">{esc(subtitle)}</text>')

    draw_axes(svg, layout, ticks, max_val, val_formatter, y_axis_label)

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
                clamped_val = min(val, max_val)
                bar_h = (clamped_val / max_val) * plot_h
                y = pad_top + plot_h - bar_h

                svg.append(f'<rect x="{x + 2:.1f}" y="{y:.1f}" width="{bar_width - 4:.1f}" height="{bar_h:.1f}" '
                           f'fill="{color}" rx="3" ry="3"><title>{esc(v)} ({esc(cfg)}, {esc(m)}): {esc(val_formatter(val))}</title></rect>')

                label_text = val_formatter(val)
                if val > max_val:
                    label_text = f">{val_formatter(max_val)}"
                svg.append(f'<text x="{x + bar_width / 2:.1f}" y="{max(pad_top + 10, y - 4):.1f}" class="bar-label">{esc(label_text)}</text>')
            else:
                svg.append(f'<text x="{x + bar_width / 2:.1f}" y="{height - layout["pad_bottom"] - 8}" class="bar-label" fill="#94A3B8">N/A</text>')

    draw_legend(svg, variants, layout)

    svg.append('</svg>')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"[PLOT] Generated {output_path}")


def generate_tables(rows, out_md_path, out_tex_path):
    """Generates Markdown and LaTeX booktabs summary tables."""
    # 1. Markdown Table
    md = []
    md.append("# Experiment 2: Microarchitectural Profiling (perf stat)\n")
    md.append("| Variant | Config | Mode | L1-D Miss (%) | LLC Miss (%) | Branch Miss (%) | IPC | Instructions | Cycles |")
    md.append("|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|")

    for r in rows:
        v = r["variant"]
        cfg = r["config"]
        m = r["mode"]
        l1 = f"{r['L1_miss_rate_pct']}%" if r['L1_miss_rate_pct'] else "N/A"
        llc = f"{r['LLC_miss_rate_pct']}%" if r['LLC_miss_rate_pct'] else "N/A"
        br = f"{r['branch_miss_rate_pct']}%" if r['branch_miss_rate_pct'] else "N/A"
        ipc = r["IPC"] if r["IPC"] else "N/A"
        ins = f"{int(r['instructions']):,}" if r["instructions"] else "N/A"
        cyc = f"{int(r['cycles']):,}" if r["cycles"] else "N/A"

        md.append(f"| {v} | {cfg} | {m} | {l1} | {llc} | {br} | {ipc} | {ins} | {cyc} |")

    with open(out_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print(f"[TABLE] Generated {out_md_path}")

    # 2. LaTeX Table
    tex = []
    tex.append("% Auto-generated by src/bench/plot1.py")
    tex.append("\\begin{table}[H]")
    tex.append("  \\centering")
    tex.append("  \\small")
    tex.append("  \\caption{Microarchitectural Hardware Counters from \\texttt{perf stat} (P-core 0, Fixed $N=50{,}000$)}")
    tex.append("  \\label{tab:hardware_counters}")
    tex.append("  \\begin{tabular}{lllrrrr}")
    tex.append("    \\toprule")
    tex.append("    \\textbf{Variant} & \\textbf{Config} & \\textbf{Mode} & \\textbf{L1 Miss (\\%)} & \\textbf{LLC Miss (\\%)} & \\textbf{Branch Miss (\\%)} & \\textbf{IPC} \\\\")
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
        l1 = f"{r['L1_miss_rate_pct']}\\%" if r['L1_miss_rate_pct'] else "---"
        llc = f"{r['LLC_miss_rate_pct']}\\%" if r['LLC_miss_rate_pct'] else "---"
        br = f"{r['branch_miss_rate_pct']}\\%" if r['branch_miss_rate_pct'] else "---"
        ipc = r["IPC"] if r["IPC"] else "---"

        tex.append(f"    {v} & {cfg} & {m} & {l1} & {llc} & {br} & {ipc} \\\\")

    tex.append("    \\bottomrule")
    tex.append("  \\end{tabular}")
    tex.append("\\end{table}")

    with open(out_tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(tex) + "\n")
    print(f"[TABLE] Generated {out_tex_path}")


def main():
    parser = argparse.ArgumentParser(description="Experiment 2 Plotter (plot1.py)")
    parser.add_argument("-i", "--input", default="data/out/perf/hardware_counters.csv", help="Input CSV")
    parser.add_argument("-o", "--output-dir", default="report/figures/perf", help="Output directory")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    proj_root = os.path.abspath(os.path.join(script_dir, "../../.."))

    input_path = args.input if os.path.isabs(args.input) else os.path.join(proj_root, args.input)
    output_dir = args.output_dir if os.path.isabs(args.output_dir) else os.path.join(proj_root, args.output_dir)

    os.makedirs(output_dir, exist_ok=True)

    rows = read_perf_csv(input_path)
    if not rows:
        print("[ERROR] No data in CSV. Run `make perf-run` first.", file=sys.stderr)
        sys.exit(1)

    # 1. L1 Cache Miss Rate Plot
    generate_bar_svg(
        title="L1-D Cache Miss Rate (%) across Priority Queues",
        subtitle="L1-misses / L1-loads (lower is better) — Physical manifestation of pointer indirection",
        y_axis_label="L1-D Miss Rate (%)",
        rows=rows,
        metric_key="L1_miss_rate_pct",
        val_formatter=lambda x: f"{x:.1f}%",
        output_path=os.path.join(output_dir, "l1_cache_miss_rate.svg"),
        max_limit=30.0
    )

    # 2. IPC (Instructions Per Cycle) Plot
    generate_bar_svg(
        title="Instructions Per Cycle (IPC) Comparison",
        subtitle="instructions / cycles (higher is better) — Measures CPU execution efficiency & stall avoidance",
        y_axis_label="IPC",
        rows=rows,
        metric_key="IPC",
        val_formatter=lambda x: f"{x:.2f}",
        output_path=os.path.join(output_dir, "ipc_comparison.svg"),
        max_limit=2.5
    )

    # 3. Tables
    generate_tables(
        rows=rows,
        out_md_path=os.path.join(output_dir, "perf.md"),
        out_tex_path=os.path.join(output_dir, "perf.tex")
    )

    print(f"\n[SUCCESS] Experiment 2 plots and tables generated in {output_dir}")


if __name__ == "__main__":
    main()
