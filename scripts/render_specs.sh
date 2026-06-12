#!/bin/bash

# Renders spec XMLs to PNG via the draw.io CLI for visual verification,
# alongside a graphviz reference render of the original source.
# By default only specs modified in git are rendered (including their
# HEAD version for before/after comparison); pass --all to render everything.

usage() {
    echo "Usage: $0 <source_directory> <specs_directory> <output_directory> [--all]"
    exit 1
}

if [ "$#" -lt 3 ]; then
    usage
fi

source_dir="${1%/}"
specs_dir="${2%/}"
output_dir="${3%/}"
render_all=false
[ "$4" = "--all" ] && render_all=true

# Locate the draw.io CLI
if command -v drawio > /dev/null 2>&1; then
    drawio="drawio"
elif [ -x "/Applications/draw.io.app/Contents/MacOS/draw.io" ]; then
    drawio="/Applications/draw.io.app/Contents/MacOS/draw.io"
else
    echo "Error: draw.io CLI not found. Install with: brew install --cask drawio"
    exit 1
fi

if ! command -v dot > /dev/null 2>&1; then
    echo "Error: graphviz (dot) not found. Install with: brew install graphviz"
    exit 1
fi

# Select spec files: changed-in-git by default, all with --all
if [ "$render_all" = true ]; then
    spec_files=$(find "$specs_dir" -type f -name "*.xml")
else
    spec_files=$(git diff --name-only HEAD -- "$specs_dir" | grep '\.xml$')
    if [ -z "$spec_files" ]; then
        echo "No modified specs found in $specs_dir (use --all to render everything)."
        exit 0
    fi
fi

count=0
echo "$spec_files" | while read -r spec; do
    rel_path="${spec#$specs_dir/}"
    base="${rel_path%.xml}"
    out_base="$output_dir/$base"
    mkdir -p "$(dirname "$out_base")"

    # Render the current spec
    "$drawio" -x -f png -o "${out_base}_new.png" "$spec" > /dev/null 2>&1
    echo "Rendered: $spec -> ${out_base}_new.png"

    # Render the HEAD version when the spec has uncommitted changes
    if ! git diff --quiet HEAD -- "$spec" 2> /dev/null; then
        old_xml="${out_base}_old.xml"
        if git show "HEAD:$spec" > "$old_xml" 2> /dev/null; then
            "$drawio" -x -f png -o "${out_base}_old.png" "$old_xml" > /dev/null 2>&1
            rm -f "$old_xml"
            echo "Rendered: HEAD:$spec -> ${out_base}_old.png"
        fi
    fi

    # Render the graphviz reference from the original source
    src_file="$source_dir/$base.gv.txt"
    if [ -f "$src_file" ]; then
        dot -Tpng "$src_file" -o "${out_base}_reference.png" 2> /dev/null
        echo "Rendered: $src_file -> ${out_base}_reference.png"
    else
        echo "Warning: no source found for $spec (expected $src_file)"
    fi
done

echo "Done. Compare *_new.png against *_old.png and *_reference.png in $output_dir"
