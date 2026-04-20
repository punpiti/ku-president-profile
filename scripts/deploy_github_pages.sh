#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/deploy_github_pages.sh [--push]

Behavior:
  - verifies this checkout is ready for GitHub Pages deployment from docs/
  - prints the repo and Pages URLs inferred from git remote
  - with --push, pushes the current branch to origin

Notes:
  - this script does not assume a specific machine name or filesystem path
  - it writes no machine-specific state into the repository
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SITE_DIR="${REPO_ROOT}/docs"
PUSH_CHANGES=0

for arg in "$@"; do
  case "${arg}" in
    --push)
      PUSH_CHANGES=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown argument: ${arg}" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ ! -d "${REPO_ROOT}/.git" ]]; then
  echo "error: ${REPO_ROOT} is not a git repository" >&2
  exit 1
fi

if [[ ! -f "${SITE_DIR}/index.html" ]]; then
  echo "error: missing ${SITE_DIR}/index.html" >&2
  exit 1
fi

if ! git -C "${REPO_ROOT}" remote get-url origin >/dev/null 2>&1; then
  echo "error: git remote 'origin' is not configured" >&2
  exit 1
fi

REMOTE_URL="$(git -C "${REPO_ROOT}" remote get-url origin)"
BRANCH_NAME="$(git -C "${REPO_ROOT}" branch --show-current)"
PAGES_PATH="/"

if [[ "${REMOTE_URL}" =~ github\.com[:/]([^/]+)/([^/.]+)(\.git)?$ ]]; then
  OWNER="${BASH_REMATCH[1]}"
  REPO_NAME="${BASH_REMATCH[2]}"
else
  echo "error: origin does not look like a GitHub repository: ${REMOTE_URL}" >&2
  exit 1
fi

PAGES_URL="https://${OWNER}.github.io/${REPO_NAME}/"
REPO_WEB_URL="https://github.com/${OWNER}/${REPO_NAME}"

echo "Repository root: ${REPO_ROOT}"
echo "Site directory: ${SITE_DIR}"
echo "Branch: ${BRANCH_NAME}"
echo "GitHub repo: ${REPO_WEB_URL}"
echo "GitHub Pages: ${PAGES_URL}"

if [[ -n "$(git -C "${REPO_ROOT}" status --short docs scripts)" ]]; then
  echo
  echo "warning: docs/ or scripts/ has uncommitted changes"
  git -C "${REPO_ROOT}" status --short docs scripts
fi

echo
echo "GitHub Pages source is expected to be: branch=${BRANCH_NAME} path=/docs"

if [[ "${PUSH_CHANGES}" -eq 1 ]]; then
  echo
  echo "Pushing ${BRANCH_NAME} to origin..."
  git -C "${REPO_ROOT}" push -u origin "${BRANCH_NAME}"
  echo "Push complete."
else
  echo
  echo "Dry run only. Re-run with --push to publish the current branch."
fi
