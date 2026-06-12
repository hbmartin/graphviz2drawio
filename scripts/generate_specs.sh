#!/bin/bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
exec "$repo_root/generate_specs.sh" "$@"
