#!/bin/bash
set -euo pipefail

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <source_directory> <specs_directory>"
    exit 1
fi

# Assign arguments to variables
source_dir="${1%/}"
specs_dir="${2%/}"

generate_spec() {
    local source_file="$1"
    local output_file="$2"

    if [ ! -f "$source_file" ]; then
        echo "Source file missing for spec: $source_file" >&2
        return 1
    fi

    # Create the directory structure if it doesn't exist
    mkdir -p "$(dirname "$output_file")"

    # Run the command
    python3 -m graphviz2drawio "$source_file" -o "$output_file"

    echo "Processed: $source_file -> $output_file"
}

mkdir -p "$specs_dir"

specs_found=false
while IFS= read -r -d "" spec_file; do
    specs_found=true
    rel_path="${spec_file#$specs_dir/}"
    source_file="$source_dir/${rel_path%.xml}.gv.txt"
    generate_spec "$source_file" "$spec_file"
done < <(find "$specs_dir" -type f -name "*.xml" -print0)

if [ "$specs_found" = false ]; then
    # Bootstrap an empty specs directory by processing every source graph.
    while IFS= read -r -d "" file; do
        rel_path="${file#$source_dir/}"
        output_file="$specs_dir/${rel_path%.gv.txt}.xml"
        generate_spec "$file" "$output_file"
    done < <(find "$source_dir" -type f -name "*.gv.txt" -print0)
fi

echo "All spec files have been processed."
