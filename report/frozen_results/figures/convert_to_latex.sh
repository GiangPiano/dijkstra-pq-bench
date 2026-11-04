#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'EOF'
Usage: report/frozen_results/convert_to_png.sh [--dry-run] [--dpi <dpi>]

Convert frozen SVG figures to PNG assets using Inkscape. The input groups are
report/frozen_results/{runtime,perf,mem}; output is written to
report/frozen_results/report_charts/{runtime,perf,mem}.

Options:
  --dpi <dpi>    Target resolution in DPI (default: 300)
  --dry-run      Print operations without creating files
  -h, --help     Show this help message
EOF
}

dry_run=false
dpi=300

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)
            dry_run=true
            shift
            ;;
        --dpi)
            if [[ -z "${2:-}" || ! "$2" =~ ^[0-9]+$ ]]; then
                printf 'error: --dpi requires a positive integer argument\n\n' >&2
                usage >&2
                exit 2
            fi
            dpi="$2"
            shift 2
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            printf 'error: unknown option: %s\n\n' "$1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
report_dir="$(cd -- "$script_dir/.." && pwd)"
input_root="$script_dir"
output_root="$input_root/report_charts"

if [[ ! -d "$input_root" ]]; then
    printf 'error: frozen results directory is missing: %s\n' "$input_root" >&2
    exit 1
fi

if ! $dry_run && ! command -v inkscape >/dev/null 2>&1; then
    printf 'error: Inkscape is required to convert SVG figures; install it and retry.\n' >&2
    exit 127
fi

groups=(runtime perf mem)
for group in "${groups[@]}"; do
    input_dir="$input_root/$group"
    if [[ ! -d "$input_dir" ]]; then
        printf 'error: missing frozen results group: %s\n' "$input_dir" >&2
        exit 1
    fi

    mapfile -d '' svgs < <(find "$input_dir" -maxdepth 1 -type f -name '*.svg' -print0 | sort -z)
    if ((${#svgs[@]} == 0)); then
        printf 'error: no SVG figures found in %s\n' "$input_dir" >&2
        exit 1
    fi

    output_dir="$output_root/$group"
    if ! $dry_run; then
        mkdir -p "$output_dir"
    fi

    for svg in "${svgs[@]}"; do
        filename="$(basename "$svg" .svg)"
        png="$output_dir/$filename.png"
        printf '%s -> %s (DPI: %s)\n' "$svg" "$png" "$dpi"
        if ! $dry_run; then
            inkscape "$svg" \
                --export-type=png \
                --export-dpi="$dpi" \
                --export-filename="$png"
        fi
    done
done