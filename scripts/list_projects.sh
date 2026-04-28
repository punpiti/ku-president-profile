#!/usr/bin/env bash

set -euo pipefail

cat <<'EOF'
Projects in this repo

- vision
  self-contained vision workspace
  local: bash scripts/run_local.sh vision

- public website
  source from vision/public-site/, deploy artifact in .public-site-build/
  local: bash scripts/run_local.sh public
  deploy: bash scripts/deploy_github_pages.sh

- selection
  application/reference/profile materials
  entry: selection/README.md

- research-award-insights
  separate project at ../research-award-insights
  local: cd ../research-award-insights && bash run_local.sh
  deploy check: cd ../research-award-insights && bash deploy_github_pages.sh
EOF
