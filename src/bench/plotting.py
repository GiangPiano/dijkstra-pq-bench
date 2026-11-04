"""Shared SVG plotting styles and layout helpers for benchmark figures."""

import html
import math


VARIANT_COLORS = {
    "binary": "#2563EB",
    "pairing": "#16A34A",
    "fibonacci": "#9333EA",
    "brodal-okasaki": "#EA580C",
    "stub": "#6B7280",
}
DEFAULT_COLORS = ["#0891B2", "#DC2626", "#7C3AED", "#CA8A04"]


def esc(value):
    """Escape text before embedding it in SVG/XML."""
    return html.escape(str(value), quote=True)


def get_color(variant, idx=0):
    """Return a stable color for a heap variant across every benchmark."""
    return VARIANT_COLORS.get(variant, DEFAULT_COLORS[idx % len(DEFAULT_COLORS)])


def wrap_label(text, max_chars, max_lines=3):
    """Wrap a category label at word boundaries for centered SVG text."""
    words = text.replace("_", " ").split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and len(candidate) > max_chars and len(lines) < max_lines - 1:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)

    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = f"{lines[-1][:max_chars - 1].rstrip()}…"
    return lines


def chart_layout(group_count, base_width=760, height=520, min_group_width=105,
                 pad_left=90, pad_right=40, pad_top=70, pad_bottom=145):
    """Return a readable canvas and plot geometry for a grouped bar chart."""
    width = max(base_width, pad_left + pad_right + group_count * min_group_width)
    plot_width = width - pad_left - pad_right
    plot_height = height - pad_top - pad_bottom
    return {
        "width": width,
        "height": height,
        "pad_left": pad_left,
        "pad_right": pad_right,
        "pad_top": pad_top,
        "pad_bottom": pad_bottom,
        "plot_width": plot_width,
        "plot_height": plot_height,
        "group_width": plot_width / max(group_count, 1),
    }


def svg_open(layout, extra_styles=""):
    """Start an SVG with the shared typography and visual styling."""
    width = layout["width"]
    height = layout["height"]
    style = """    .axis { stroke: #CBD5E1; stroke-width: 1; }
    .grid { stroke: #F1F5F9; stroke-width: 1; stroke-dasharray: 4,4; }
    .baseline { stroke: #EF4444; stroke-width: 1.5; stroke-dasharray: 3,3; }
    .tick-label { font-size: 11px; fill: #64748B; }
    .axis-title { font-size: 12px; font-weight: 600; fill: #334155; }
    .chart-title { font-size: 16px; font-weight: 700; fill: #0F172A; }
    .chart-subtitle { font-size: 12px; fill: #64748B; }
    .bar-label { font-size: 9px; font-weight: 600; fill: #1E293B; text-anchor: middle; }
    .legend-text { font-size: 12px; fill: #334155; font-weight: 500; dominant-baseline: central; }"""
    if extra_styles:
        style += f"\n{extra_styles}"
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" style="background-color: #ffffff; '
        f'font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif;">',
        "<defs>",
        "  <style>",
        style,
        "  </style>",
        "</defs>",
    ]


def draw_axes(svg, layout, ticks, max_value, y_formatter, y_axis_label,
              log_scale=False, baseline=None):
    """Draw shared grid, axes, ticks, and optional baseline."""
    left = layout["pad_left"]
    top = layout["pad_top"]
    plot_height = layout["plot_height"]
    width = layout["width"]
    bottom = top + plot_height
    right = width - layout["pad_right"]

    for value in ticks:
        if log_scale:
            y = bottom if value <= 1 else bottom - (math.log10(value) / max_value) * plot_height
            tick_text = f"10^{int(math.log10(value))}" if value > 1 else "1"
        else:
            y = bottom - (value / max_value) * plot_height
            tick_text = y_formatter(value)
        svg.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" class="grid" />')
        svg.append(f'<text x="{left - 10}" y="{y + 4:.1f}" class="tick-label" text-anchor="end">{esc(tick_text)}</text>')

    svg.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" class="axis" />')
    svg.append(f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" class="axis" />')
    svg.append(
        f'<text x="-{(top + plot_height / 2):.1f}" y="20" class="axis-title" '
        f'text-anchor="middle" transform="rotate(-90)">{esc(y_axis_label)}</text>'
    )
    if baseline is not None:
        y = bottom - (baseline / max_value) * plot_height
        svg.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" class="baseline" />')


def draw_category_label(svg, x, y, text, group_width, max_lines=3, font_size=10):
    """Draw a centered, bounded multi-line category label."""
    max_chars = max(10, int(group_width / 7))
    lines = wrap_label(text, max_chars, max_lines=max_lines)
    for index, line in enumerate(lines):
        css_class = "axis-title" if index == 0 else "tick-label"
        svg.append(
            f'<text x="{x:.1f}" y="{y + index * 14}" class="{css_class}" '
            f'font-size="{font_size}px" text-anchor="middle">{esc(line)}</text>'
        )


def draw_legend(svg, variants, layout, item_spacing=145):
    """Draw a centered legend in the dedicated bottom row."""
    y = layout["height"] - 28
    total_width = len(variants) * item_spacing
    start_x = max(layout["pad_left"], (layout["width"] - total_width) / 2)
    for index, variant in enumerate(variants):
        x = start_x + index * item_spacing
        color = get_color(variant, index)
        svg.append(f'<rect x="{x:.1f}" y="{y - 7:.1f}" width="14" height="14" fill="{color}" rx="3" ry="3" />')
        svg.append(f'<text x="{x + 20:.1f}" y="{y:.1f}" class="legend-text">{esc(variant)}</text>')
