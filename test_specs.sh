#!/bin/bash

# Function to display usage information
usage() {
    echo "Usage: $0 <source_directory> <specs_directory> <output_directory>"
    exit 1
}

# Check if the correct number of arguments is provided
if [ "$#" -ne 3 ]; then
    usage
fi

# Assign arguments to variables
source_dir="${1%/}"
specs_dir="${2%/}"
output_dir="${3%/}"

# Function to process files
process_files() {
    local src_dir="$1"
    local out_dir="$2"

    find "$src_dir" -type f -name "*.gv.txt" | while read -r file; do
        rel_path="${file#$src_dir/}"
        output_file="$out_dir/${rel_path%.gv.txt}.xml"
        mkdir -p "$(dirname "$output_file")"
        python3 -m graphviz2drawio "$file" -o "$output_file"
        echo "Processed: $file -> $output_file"
    done
}

# Process files from source_dir to output_dir
echo "Processing files from $source_dir to $output_dir"
process_files "$source_dir" "$output_dir"

# Compare output_dir with specs_dir
echo "Comparing results in $output_dir with $specs_dir"
diff_output=$(diff -r "$output_dir" "$specs_dir")

if [ -z "$diff_output" ]; then
    echo "No differences found. Test passed."
    exit 0
else
    echo "Differences found. Test failed."
    echo "Differences:"
    echo "$diff_output"
    exit 1
fi
