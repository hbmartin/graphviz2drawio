#!/bin/bash
set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"

source "$script_dir/drawio_export.sh"

# Renders a graphviz file two ways for visual comparison:
#   1. graphviz's own PNG render (dot)
#   2. graphviz2drawio conversion rendered to PNG via the draw.io CLI

usage() {
    echo "Usage: $0 <graphviz_file> [output_directory]"
    echo "  output_directory defaults to tmp_render/"
    return 1
}

if [[ "$#" -lt 1 || "$#" -gt 2 ]]; then
    usage
    exit 1
fi

input_file="$1"
output_dir="${2:-tmp_render}"
output_dir="${output_dir%/}"

if [[ ! -f "$input_file" ]]; then
    echo "Error: input file not found: $input_file" >&2
    exit 1
fi

case "$input_file" in
    *.xml)
        echo "Error: $input_file looks like a draw.io XML, but this script takes a graphviz source (.gv.txt, .gv, .dot)." >&2
        echo "To render existing spec XMLs, use: ./scripts/render_specs.sh" >&2
        exit 1
        ;;
    *)
        ;;
esac

if ! command -v dot > /dev/null 2>&1; then
    echo "Error: graphviz (dot) not found. Install with: brew install graphviz" >&2
    exit 1
fi

# Strip directory and any of the usual graphviz extensions for output naming
base=$(basename "$input_file")
base="${base%.gv.txt}"
base="${base%.gv}"
base="${base%.dot}"

mkdir -p "$output_dir"
graphviz_png="$output_dir/${base}_graphviz.png"
drawio_xml="$output_dir/${base}.xml"
drawio_png="$output_dir/${base}_drawio.png"

if ! dot -Tpng "$input_file" -o "$graphviz_png"; then
    echo "Error: graphviz could not render $input_file — is it a valid dot file?" >&2
    exit 1
fi
echo "Rendered: $input_file -> $graphviz_png (graphviz)"

# Run graphviz2drawio in the project environment regardless of cwd
if ! uv run --project "$repo_root" python -m graphviz2drawio "$input_file" -o "$drawio_xml" > /dev/null; then
    echo "Error: graphviz2drawio conversion failed for $input_file" >&2
    exit 1
fi
render_drawio_png "$drawio_xml" "$drawio_png" "$input_file (graphviz2drawio + draw.io)"

echo ""
echo "Compare:"
echo "  open $graphviz_png $drawio_png"
