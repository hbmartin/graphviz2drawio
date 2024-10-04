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

    find "$src_dir" -type f -name "*.gv.txt" -print0 | while IFS= read -r -d $'\0' file; do
        rel_path="${file#$src_dir/}"
        output_file="$out_dir/${rel_path%.gv.txt}.xml"
        mkdir -p "$(dirname "$output_file")"
        python3 -m graphviz2drawio "$file" -o "$output_file"
        echo "Processed: $file -> $output_file"
    done
}

# Function to compare files ignoring unstable IDs
compare_files() {
    local file1="$1"
    local file2="$2"

    # Use sed to replace id="..." with a placeholder
    sed_command='s/id="[^"]*"/id="PLACEHOLDER"/g'

    # Compare the files after replacing IDs
    diff <(sed "$sed_command" "$file1") <(sed "$sed_command" "$file2")
}

# Process files from source_dir to output_dir
echo "Processing files from $source_dir to $output_dir"
process_files "$source_dir" "$output_dir"

# Compare output_dir with specs_dir
echo "Comparing results in $output_dir with $specs_dir"
diff_found=false

# Recursive function to compare directories
compare_dirs() {
    local dir1="$1"
    local dir2="$2"

    for file in "$dir1"/*; do
        local rel_path="${file#$dir1/}"
        local file2="$dir2/$rel_path"

        if [ -d "$file" ]; then
            # If it's a directory, recurse
            compare_dirs "$file" "$file2"
        elif [ -f "$file" ]; then
            # If it's a file, compare
            if [ ! -f "$file2" ]; then
                echo "File missing in specs directory: $rel_path"
                diff_found=true
            else
                diff_output=$(compare_files "$file" "$file2")
                if [ -n "$diff_output" ]; then
                    echo "Differences found in file: $rel_path"
                    echo "$diff_output"
                    diff_found=true
                fi
            fi
        fi
    done

    # Check for extra files in specs_dir
    for file in "$dir2"/*; do
        local rel_path="${file#$dir2/}"
        local file1="$dir1/$rel_path"

        if [ ! -e "$file1" ]; then
            echo "Extra file in specs directory: $rel_path"
            diff_found=true
        fi
    done
}

# Start the comparison
compare_dirs "$output_dir" "$specs_dir"

if [ "$diff_found" = false ]; then
    echo "No differences found (ignoring unstable IDs). Test passed."
    exit 0
else
    echo "Differences found (ignoring unstable IDs). Test failed."
    exit 1
fi
