#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <source_directory> <specs_directory>"
    exit 1
fi

# Assign arguments to variables
source_dir="$1"
specs_dir="$2"

# Ensure source_dir doesn't end with a slash
source_dir="${source_dir%/}"

# Find all .gv.txt files in the source directory and its subdirectories
find "$source_dir" -type f -name "*.gv.txt" | while read -r file; do
    # Get the relative path of the file from the source directory
    rel_path="${file#$source_dir/}"

    # Create the output filename, preserving the directory structure
    output_file="$specs_dir/${rel_path%.gv.txt}.xml"

    # Create the directory structure if it doesn't exist
    mkdir -p "$(dirname "$output_file")"

    # Run the command
    python3 -m graphviz2drawio "$file" -o "$output_file"

    echo "Processed: $file -> $output_file"
done

echo "All .gv.txt files have been processed."
