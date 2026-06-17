#!/bin/bash
# Runs a command inside the canonical spec environment (Ubuntu + pinned graphviz).
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
image="graphviz2drawio-spec-env"

docker build --platform linux/amd64 -t "$image" -f "$repo_root/scripts/Dockerfile" "$repo_root"

# Match the host UID/GID so bind-mounted output files stay writable locally.
exec docker run --rm --platform linux/amd64 --user "$(id -u):$(id -g)" -v "$repo_root:/work" -w /work "$image" "$@"
