#!/usr/bin/env python3
"""
Experiment 2 Plotter
Reads the perf hardware counter CSV and generates vector SVG charts, a
Markdown table, and a LaTeX table for the report.

Figures
-------
Rates (kept for continuity with earlier drafts of the report):
  l1_cache_miss_rate.svg      L1-D misses / L1-D loads
  ipc_comparison.svg          instructions / cycles

Absolute counts, normalised per vertex of the input graph:
  instructions_per_vertex.svg   how much work each heap does
  cycles_vs_instructions.svg    log-log scatter splitting the cycle cost into
                                work (x) and execution efficiency (IPC lines)
  l1_misses_per_vertex.svg      L1-D misses (count, not rate)
  branch_misses_per_vertex.svg  branch mispredictions (count, not rate)
  llc_misses_per_vertex.svg     last-level cache misses; a check that the
                                working set stays on chip

Why per vertex: the seven graphs range from 1,000 to 50,176 vertices, so raw
per-run counts mostly show graph size. Dividing by n puts every graph on one
axis while keeping the quantity proportional to cost (cycles lost), unlike a
rate whose denominator differs from heap to heap.
"""

import argparse
import csv
import json
import math
import os
import re
import sys

BENCH_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BENCH_DIR not in sys.path:
    sys.path.insert(0, BENCH_DIR)

from plotting import (chart_layout, draw_axes, draw_category_label,
                      draw_legend, esc, get_color, svg_open)

MODES = ["decrease_key", "lazy"]
COUNTERS = ["instructions", "cycles", "branches", "branch_misses",
            "L1_loads", "L1_misses", "LLC_loads", "LLC_misses"]


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


def read_vertex_counts(metadata_path):
    """Map graph name -> vertex count from the generated graphs.json."""
    try:
        with open(metadata_path, encoding="utf-8") as f:
            metadata = json.load(f)["metadata"]
    except (OSError, KeyError, ValueError) as exc:
        print(f"[WARN] Could not read graph metadata ({exc}); "
              "per-vertex figures will be skipped.", file=sys.stderr)
        return {}

    counts = {}
    for name, meta in metadata.items():
        if "n" in meta:
            counts[name] = int(meta["n"])
        elif "rows" in meta and "cols" in meta:
            counts[name] = int(meta["rows"]) * int(meta["cols"])
        elif "layers" in meta and "width" in meta:
            counts[name] = int(meta["layers"]) * int(meta["width"])
    return counts


def omitted_events(row):
    """Counter keys that bench.py reported as unsupported for this row."""
    match = re.search(r"unsupported events omitted: ([\w, ]+)", row.get("note", ""))
    return {key.strip() for key in match.group(1).split(",")} if match else set()


def add_per_vertex_metrics(rows, vertex_counts):
    """
    Adds '<counter>_per_vertex' fields to each row. A field is left empty when
    the counter was not collected, so the charts show N/A instead of a zero
    bar that looks like a measurement.
    """
    for r in rows:
        n = vertex_counts.get(r["config"])
        missing = omitted_events(r)
        run_failed = _as_float(r.get("cycles")) in (None, 0.0)
        for key in COUNTERS:
            value = _as_float(r.get(key))
            usable = n and not run_failed and key not in missing and value is not None
            r[f"{key}_per_vertex"] = f"{value / n:.6g}" if usable else ""


def _as_float(text):
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def fmt_si(value):
    """Compact number formatter: 950, 1.2k, 3.4M."""
    for threshold, suffix in ((1e9, "G"), (1e6, "M"), (1e3, "k")):
        if abs(value) >= threshold:
            return f"{value / threshold:.3g}{suffix}"
    if abs(value) >= 10 or value == 0:
        return f"{value:.0f}"
    return f"{value:.2g}"


def generate_bar_svg(title, subtitle, y_axis_label, rows, metric_key, val_formatter, output_path, max_limit=None):
    """
    Renders grouped bar chart for metric_key across generated configurations and modes.
    """
    # Identify groups from the generated benchmark data.
    configs = sorted({r["config"] for r in rows})
    group_keys = [
        (config, mode, f"{config}\n{mode.replace('_', ' ').title()}")
        for config in configs
        for mode in MODES
        if any(r["config"] == config and r["mode"] == mode for r in rows)
    ]

    variants = sorted({r["variant"] for r in rows})
    layout = chart_layout(len(group_keys), min_group_width=115)
    height = layout["height"]
    pad_left = layout["pad_left"]
    pad_top = layout["pad_top"]
    plot_h = layout["plot_height"]

    # Collect max value for y-axis scaling
    all_vals = []
    lookup = {}
    for r in rows:
        val = _as_float(r.get(metric_key, ""))
        if val is None:
            continue
        lookup[(r["config"], r["mode"], r["variant"])] = val
        if max_limit is None or val <= max_limit:
            all_vals.append(val)

    if not all_vals:
        print(f"[SKIP] No data for {os.path.basename(output_path)}")
        return

    max_val = (max(all_vals) * 1.25) if max(all_vals) > 0 else 1.0
    if max_limit and max_val > max_limit:
        max_val = max_limit

    num_ticks = 5
    ticks = [i * (max_val / num_ticks) for i in range(num_ticks + 1)]

    svg = svg_open(layout)

    svg.append(f'<text x="{pad_left}" y="32" class="chart-title">{esc(title)}</text>')
    svg.append(f'<text x="{pad_left}" y="50" class="chart-subtitle">{esc(subtitle)}</text>')

    draw_axes(svg, layout, ticks, max_val, val_formatter, y_axis_label)

    # Grouped Bars
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


def _log_ticks(lo_exp, hi_exp):
    """Tick values at 1, 2 and 5 times each power of ten inside the range."""
    ticks = []
    for exp in range(lo_exp, hi_exp + 1):
        for mult in (1, 2, 5):
            value = mult * 10 ** exp
            if 10 ** lo_exp <= value <= 10 ** hi_exp:
                ticks.append(value)
    return ticks


def generate_scatter_svg(rows, output_path):
    """
    Log-log scatter of cycles per vertex against instructions per vertex.

    cycles = instructions / IPC, so on log axes every point sits on the
    diagonal for its IPC. Moving right means more work; moving off a diagonal
    means the same work executed more or less efficiently. This answers in one
    picture whether a heap is slow because it does more, or because it stalls.
    """
    points = []
    for r in rows:
        x = _as_float(r.get("instructions_per_vertex"))
        y = _as_float(r.get("cycles_per_vertex"))
        if x and y and x > 0 and y > 0:
            points.append((x, y, r))
    if not points:
        print(f"[SKIP] No data for {os.path.basename(output_path)}")
        return

    width, height = 820, 600
    pad_left, pad_right, pad_top, pad_bottom = 90, 60, 70, 120
    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom
    left, top = pad_left, pad_top
    right, bottom = left + plot_w, top + plot_h

    lx = [math.log10(p[0]) for p in points]
    ly = [math.log10(p[1]) for p in points]
    x_lo, x_hi = math.floor(min(lx)), math.ceil(max(lx))
    y_lo, y_hi = math.floor(min(ly)), math.ceil(max(ly))
    x_hi += x_hi == x_lo
    y_hi += y_hi == y_lo

    def px(value):
        return left + (math.log10(value) - x_lo) / (x_hi - x_lo) * plot_w

    def py(value):
        return bottom - (math.log10(value) - y_lo) / (y_hi - y_lo) * plot_h

    layout = {"width": width, "height": height, "pad_left": pad_left}
    svg = svg_open(layout, extra_styles=(
        "    .ipc-line { stroke: #94A3B8; stroke-width: 1; stroke-dasharray: 5,4; }\n"
        "    .ipc-label { font-size: 10px; fill: #64748B; }"))

    svg.append(f'<text x="{left}" y="32" class="chart-title">Cycles vs Instructions per Vertex</text>')
    svg.append(f'<text x="{left}" y="50" class="chart-subtitle">'
               'Right = more work; above a dashed line = lower IPC. Both axes log scale.</text>')

    # Grid and tick labels
    for value in _log_ticks(x_lo, x_hi):
        x = px(value)
        svg.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom}" class="grid" />')
        svg.append(f'<text x="{x:.1f}" y="{bottom + 16}" class="tick-label" text-anchor="middle">{esc(fmt_si(value))}</text>')
    for value in _log_ticks(y_lo, y_hi):
        y = py(value)
        svg.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" class="grid" />')
        svg.append(f'<text x="{left - 10}" y="{y + 4:.1f}" class="tick-label" text-anchor="end">{esc(fmt_si(value))}</text>')
    svg.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" class="axis" />')
    svg.append(f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" class="axis" />')
    svg.append(f'<text x="{(left + right) / 2:.1f}" y="{bottom + 38}" class="axis-title" '
               'text-anchor="middle">Instructions per vertex</text>')
    svg.append(f'<text x="-{(top + plot_h / 2):.1f}" y="20" class="axis-title" '
               'text-anchor="middle" transform="rotate(-90)">Cycles per vertex</text>')

    # Constant-IPC reference lines: log(cycles) = log(instructions) - log(IPC)
    for ipc in (0.5, 1, 2, 4):
        shift = math.log10(ipc)
        a = max(x_lo, y_lo + shift)
        b = min(x_hi, y_hi + shift)
        if a >= b:
            continue
        x1, y1 = px(10 ** a), py(10 ** (a - shift))
        x2, y2 = px(10 ** b), py(10 ** (b - shift))
        svg.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" class="ipc-line" />')
        svg.append(f'<text x="{x2 - 4:.1f}" y="{y2 + 12:.1f}" class="ipc-label" text-anchor="end">IPC {ipc:g}</text>')

    # Points: colour = heap, filled = decrease-key, hollow = lazy
    variants = sorted({p[2]["variant"] for p in points})
    for x, y, r in points:
        color = get_color(r["variant"], variants.index(r["variant"]))
        fill = color if r["mode"] == "decrease_key" else "#FFFFFF"
        tip = (f'{r["variant"]} ({r["config"]}, {r["mode"]}): '
               f'{fmt_si(x)} instr, {fmt_si(y)} cycles per vertex, IPC {x / y:.2f}')
        svg.append(f'<circle cx="{px(x):.1f}" cy="{py(y):.1f}" r="5.5" fill="{fill}" '
                   f'stroke="{color}" stroke-width="2"><title>{esc(tip)}</title></circle>')

    # Legend: marker meaning, then heap colours
    legend_y = height - 58
    mid = width / 2
    svg.append(f'<circle cx="{mid - 120:.1f}" cy="{legend_y}" r="5.5" fill="#475569" stroke="#475569" stroke-width="2" />')
    svg.append(f'<text x="{mid - 108:.1f}" y="{legend_y}" class="legend-text">decrease-key</text>')
    svg.append(f'<circle cx="{mid + 20:.1f}" cy="{legend_y}" r="5.5" fill="#FFFFFF" stroke="#475569" stroke-width="2" />')
    svg.append(f'<text x="{mid + 32:.1f}" y="{legend_y}" class="legend-text">lazy</text>')
    draw_legend(svg, variants, {"width": width, "height": height, "pad_left": pad_left})

    svg.append('</svg>')
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"[PLOT] Generated {output_path}")


def generate_tables(rows, out_md_path, out_tex_path):
    """Generates Markdown and LaTeX booktabs summary tables."""
    have_per_vertex = any(r.get("instructions_per_vertex") for r in rows)

    def pv(r, key):
        value = _as_float(r.get(f"{key}_per_vertex"))
        return fmt_si(value) if value is not None else "N/A"

    # 1. Markdown Table
    md = []
    md.append("# Experiment 2: Microarchitectural Profiling (perf stat)\n")
    md.append("Counts are per Dijkstra run; per-vertex columns divide by the graph's vertex count.\n")
    header = "| Variant | Config | Mode | L1-D Miss (%) | LLC Miss (%) | Branch Miss (%) | IPC | Instructions | Cycles |"
    align = "|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|"
    if have_per_vertex:
        header += " Instr/vertex | L1 misses/vertex | Branch misses/vertex | LLC misses/vertex |"
        align += ":---:|:---:|:---:|:---:|"
    md.append(header)
    md.append(align)

    for r in rows:
        v = r["variant"]
        cfg = r["config"]
        m = r["mode"]
        l1 = f"{r['L1_miss_rate_pct']}%" if r['L1_miss_rate_pct'] else "N/A"
        llc = f"{r['LLC_miss_rate_pct']}%" if r['LLC_miss_rate_pct'] else "N/A"
        br = f"{r['branch_miss_rate_pct']}%" if r['branch_miss_rate_pct'] else "N/A"
        ipc = r["IPC"] if r["IPC"] else "N/A"
        ins = f"{int(float(r['instructions'])):,}" if r["instructions"] else "N/A"
        cyc = f"{int(float(r['cycles'])):,}" if r["cycles"] else "N/A"

        line = f"| {v} | {cfg} | {m} | {l1} | {llc} | {br} | {ipc} | {ins} | {cyc} |"
        if have_per_vertex:
            line += (f" {pv(r, 'instructions')} | {pv(r, 'L1_misses')} |"
                     f" {pv(r, 'branch_misses')} | {pv(r, 'LLC_misses')} |")
        md.append(line)

    with open(out_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print(f"[TABLE] Generated {out_md_path}")

    # 2. LaTeX Table
    tex = []
    tex.append("% Auto-generated by src/bench/perf/plot.py")
    tex.append("\\begin{table}[H]")
    tex.append("  \\centering")
    tex.append("  \\small")
    tex.append("  \\caption{Hardware counters from \\texttt{perf stat}, per Dijkstra run (pinned to one core)}")
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
        cfg_tex = cfg.replace("_", "\\_")

        tex.append(f"    {v} & {cfg_tex} & {m} & {l1} & {llc} & {br} & {ipc} \\\\")

    tex.append("    \\bottomrule")
    tex.append("  \\end{tabular}")
    tex.append("\\end{table}")

    with open(out_tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(tex) + "\n")
    print(f"[TABLE] Generated {out_tex_path}")


def main():
    parser = argparse.ArgumentParser(description="Experiment 2 Plotter")
    parser.add_argument("-i", "--input", default="data/out/perf/hardware_counters.csv", help="Input CSV")
    parser.add_argument("-o", "--output-dir", default="report/figures/perf", help="Output directory")
    parser.add_argument("-m", "--metadata", default="build/test/graphs.json",
                        help="Graph metadata JSON (for vertex counts)")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    proj_root = os.path.abspath(os.path.join(script_dir, "../../.."))

    def resolve(path):
        return path if os.path.isabs(path) else os.path.join(proj_root, path)

    input_path = resolve(args.input)
    output_dir = resolve(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    rows = read_perf_csv(input_path)
    if not rows:
        print("[ERROR] No data in CSV. Run `make perf-run` first.", file=sys.stderr)
        sys.exit(1)

    add_per_vertex_metrics(rows, read_vertex_counts(resolve(args.metadata)))

    def out(name):
        return os.path.join(output_dir, name)

    # 1. L1 Cache Miss Rate Plot (rate; see l1_misses_per_vertex for the count)
    generate_bar_svg(
        title="L1-D Cache Miss Rate (%) across Priority Queues",
        subtitle="L1 misses / L1 loads. The denominator differs per heap; compare with L1 misses per vertex.",
        y_axis_label="L1-D Miss Rate (%)",
        rows=rows,
        metric_key="L1_miss_rate_pct",
        val_formatter=lambda x: f"{x:.1f}%",
        output_path=out("l1_cache_miss_rate.svg"),
        max_limit=30.0
    )

    # 2. IPC (Instructions Per Cycle) Plot
    generate_bar_svg(
        title="Instructions Per Cycle (IPC) Comparison",
        subtitle="instructions / cycles (higher is better): how efficiently the CPU executes each heap's work",
        y_axis_label="IPC",
        rows=rows,
        metric_key="IPC",
        val_formatter=lambda x: f"{x:.2f}",
        output_path=out("ipc_comparison.svg"),
        max_limit=2.5
    )

    # 3. Work done: instructions per vertex
    generate_bar_svg(
        title="Instructions Retired per Vertex",
        subtitle="Total work per Dijkstra run divided by vertex count (lower is better)",
        y_axis_label="Instructions per vertex",
        rows=rows,
        metric_key="instructions_per_vertex",
        val_formatter=fmt_si,
        output_path=out("instructions_per_vertex.svg"),
    )

    # 4. Work vs efficiency decomposition
    generate_scatter_svg(rows, out("cycles_vs_instructions.svg"))

    # 5. Memory and control-flow costs as counts, not rates
    generate_bar_svg(
        title="L1-D Cache Misses per Vertex",
        subtitle="Absolute misses per Dijkstra run divided by vertex count (lower is better)",
        y_axis_label="L1-D misses per vertex",
        rows=rows,
        metric_key="L1_misses_per_vertex",
        val_formatter=fmt_si,
        output_path=out("l1_misses_per_vertex.svg"),
    )
    generate_bar_svg(
        title="Branch Mispredictions per Vertex",
        subtitle="Each misprediction flushes the pipeline (roughly 15 to 20 cycles on modern cores)",
        y_axis_label="Branch misses per vertex",
        rows=rows,
        metric_key="branch_misses_per_vertex",
        val_formatter=fmt_si,
        output_path=out("branch_misses_per_vertex.svg"),
    )
    generate_bar_svg(
        title="Last-Level Cache Misses per Vertex",
        subtitle="Loads that went to DRAM. Near zero means the working set fits on chip.",
        y_axis_label="LLC misses per vertex",
        rows=rows,
        metric_key="LLC_misses_per_vertex",
        val_formatter=fmt_si,
        output_path=out("llc_misses_per_vertex.svg"),
    )

    # 6. Tables
    generate_tables(
        rows=rows,
        out_md_path=out("perf.md"),
        out_tex_path=out("perf.tex")
    )

    print(f"\n[SUCCESS] Experiment 2 plots and tables generated in {output_dir}")


if __name__ == "__main__":
    main()
