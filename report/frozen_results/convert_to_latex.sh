#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'EOF'
Usage: report/frozen_results/convert_to_latex.sh [--dry-run]

Convert frozen SVG figures to Inkscape PDF+LaTeX assets. The input groups are
report/frozen_results/{runtime,perf,mem}; output is written to
report/frozen_results/report_charts/{runtime,perf,mem}.
EOF
}

dry_run=false
case "${1:-}" in
    "")
        ;;
    --dry-run)
        dry_run=true
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
        pdf="$output_dir/$filename.pdf"
        printf '%s -> %s and %s_tex\n' "$svg" "$pdf" "$pdf"
        if ! $dry_run; then
            inkscape "$svg" \
                --export-type=pdf \
                --export-latex \
                --export-filename="$pdf"
        fi
    done
done
