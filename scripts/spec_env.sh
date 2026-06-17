#!/bin/bash
# Runs a command inside the canonical spec environment (Ubuntu + pinned graphviz).
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
image="graphviz2drawio-spec-env"

docker build --platform linux/amd64 -t "$image" -f "$repo_root/scripts/Dockerfile" "$repo_root"

# Linux hosts may see root-owned files in bind-mounted output directories.
exec docker run --rm --platform linux/amd64 -v "$repo_root:/work" -w /work "$image" "$@"
