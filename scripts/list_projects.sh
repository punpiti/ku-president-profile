#!/usr/bin/env bash

set -euo pipefail

cat <<'EOF'
Projects in this repo

- vision
  self-contained vision workspace
  local: bash scripts/run_local.sh vision

- public website
  GitHub Pages site from docs/
  local: bash scripts/run_local.sh public
  deploy: bash scripts/deploy_github_pages.sh

- selection
  application/reference/profile materials
  entry: selection/README.md

- research_award
  standalone GitHub Pages site
  local: bash scripts/run_local.sh award
EOF
