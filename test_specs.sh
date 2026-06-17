#!/bin/bash
set -euo pipefail

# Function to display usage information
usage() {
    echo "Usage: $0 <source_directory> <output_directory> [mac|linux]"
    exit 1
}

# Check if the correct number of arguments is provided
if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
    usage
fi

# Assign arguments to variables
repo_root="$(cd "$(dirname "$0")" && pwd)"
source_dir="${1%/}"
output_dir="${2%/}"
platform="${3:-${SPEC_PLATFORM:-}}"

detect_platform() {
    if [ -n "$platform" ]; then
        case "$(printf "%s" "$platform" | tr "[:upper:]" "[:lower:]")" in
            mac | macos | darwin)
                echo "mac"
                ;;
            linux)
                echo "linux"
                ;;
            *)
                echo "Unsupported spec platform: $platform" >&2
                echo "Expected: mac or linux" >&2
                exit 1
                ;;
        esac
        return
    fi

    case "$(uname -s)" in
        Darwin)
            echo "mac"
            ;;
        Linux)
            echo "linux"
            ;;
        *)
            echo "Unsupported OS for spec tests: $(uname -s)" >&2
            echo "Set SPEC_PLATFORM to mac or linux to choose a spec output path." >&2
            exit 1
            ;;
    esac
}

spec_platform="$(detect_platform)"
specs_dir="$repo_root/specs/$spec_platform"

if [ ! -d "$source_dir" ]; then
    echo "Source directory does not exist: $source_dir" >&2
    exit 1
fi

if [ ! -d "$specs_dir" ]; then
    echo "Spec directory does not exist for platform '$spec_platform': $specs_dir" >&2
    exit 1
fi

# Function to process files
process_files() {
    local src_dir="$1"
    local out_dir="$2"
    local expected_dir="$3"

    while IFS= read -r -d "" file; do
        rel_path="${file#$expected_dir/}"
        source_file="$src_dir/${rel_path%.xml}.gv.txt"
        output_file="$out_dir/$rel_path"

        if [ ! -f "$source_file" ]; then
            echo "Source file missing for spec: $rel_path" >&2
            return 1
        fi

        mkdir -p "$(dirname "$output_file")"
        if ! python3 -m graphviz2drawio "$source_file" -o "$output_file" >/dev/null; then
            echo "Failed to process: $source_file" >&2
            return 1
        fi
        echo "Processed: $source_file -> $output_file"
    done < <(find "$expected_dir" -type f -name "*.xml" -print0)
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
rm -rf "$output_dir"
mkdir -p "$output_dir"
process_files "$source_dir" "$output_dir" "$specs_dir"

# Compare output_dir with specs_dir
echo "Comparing results in $output_dir with $specs_dir ($spec_platform)"
diff_found=false

while IFS= read -r -d "" file; do
    rel_path="${file#$output_dir/}"
    spec_file="$specs_dir/$rel_path"

    if [ ! -f "$spec_file" ]; then
        echo "File missing in specs directory: $rel_path"
        diff_found=true
        continue
    fi

    if ! diff_output="$(compare_files "$file" "$spec_file")"; then
        echo "Differences found in file: $rel_path"
        echo "$diff_output"
        diff_found=true
    fi
done < <(find "$output_dir" -type f -name "*.xml" -print0)

while IFS= read -r -d "" file; do
    rel_path="${file#$specs_dir/}"
    output_file="$output_dir/$rel_path"

    if [ ! -f "$output_file" ]; then
        echo "Extra file in specs directory: $rel_path"
        diff_found=true
    fi
done < <(find "$specs_dir" -type f -name "*.xml" -print0)

if [ "$diff_found" = false ]; then
    echo "No differences found (ignoring unstable IDs). Test passed."
    exit 0
else
    echo "Differences found (ignoring unstable IDs). Test failed."
    exit 1
fi
