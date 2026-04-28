#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/deploy_github_pages.sh [--push]

Behavior:
  - builds vision/public-site/ into a local deploy artifact directory
  - verifies the deploy artifact before GitHub Pages deployment
  - prints the repo and Pages URLs inferred from git remote
  - with --push, publishes the verified artifact to the gh-pages branch,
    points GitHub Pages to branch=gh-pages path=/, and pushes the source branch

Notes:
  - this script does not assume a specific machine name or filesystem path
  - it writes no machine-specific state into the repository
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BUILD_DIR="${PUBLIC_SITE_BUILD_DIR:-${REPO_ROOT}/.public-site-build}"
PAGES_BRANCH="${PAGES_BRANCH:-gh-pages}"
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

if [[ ! -f "${BUILD_DIR}/index.html" ]]; then
  echo "public deploy artifact not found; building..."
fi

"${SCRIPT_DIR}/build_public_site.sh"

if ! git -C "${REPO_ROOT}" remote get-url origin >/dev/null 2>&1; then
  echo "error: git remote 'origin' is not configured" >&2
  exit 1
fi

REMOTE_URL="$(git -C "${REPO_ROOT}" remote get-url origin)"
BRANCH_NAME="$(git -C "${REPO_ROOT}" branch --show-current)"

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
echo "Source branch: ${BRANCH_NAME}"
echo "Build directory: ${BUILD_DIR}"
echo "Deploy branch: ${PAGES_BRANCH}"
echo "GitHub repo: ${REPO_WEB_URL}"
echo "GitHub Pages: ${PAGES_URL}"

if [[ -n "$(git -C "${REPO_ROOT}" status --short vision/public-site scripts)" ]]; then
  echo
  echo "warning: public site source or scripts have uncommitted changes"
  git -C "${REPO_ROOT}" status --short vision/public-site scripts
fi

echo
echo "GitHub Pages source is expected to be: branch=${PAGES_BRANCH} path=/"

if [[ "${PUSH_CHANGES}" -eq 1 ]]; then
  if [[ -n "$(git -C "${REPO_ROOT}" status --porcelain)" ]]; then
    echo "error: working tree has uncommitted changes; commit before publishing" >&2
    exit 1
  fi

  WORKTREE_DIR="$(mktemp -d)"
  cleanup() {
    git -C "${REPO_ROOT}" worktree remove --force "${WORKTREE_DIR}" >/dev/null 2>&1 || true
  }
  trap cleanup EXIT

  echo
  echo "Preparing ${PAGES_BRANCH} worktree..."
  if git -C "${REPO_ROOT}" ls-remote --exit-code --heads origin "${PAGES_BRANCH}" >/dev/null 2>&1; then
    git -C "${REPO_ROOT}" worktree add -B "${PAGES_BRANCH}" "${WORKTREE_DIR}" "origin/${PAGES_BRANCH}"
  else
    git -C "${REPO_ROOT}" worktree add --detach "${WORKTREE_DIR}"
    git -C "${WORKTREE_DIR}" switch --orphan "${PAGES_BRANCH}"
  fi

  git -C "${WORKTREE_DIR}" rm -r --ignore-unmatch . >/dev/null
  rsync -a "${BUILD_DIR}/" "${WORKTREE_DIR}/"
  touch "${WORKTREE_DIR}/.nojekyll"
  git -C "${WORKTREE_DIR}" add -A

  if git -C "${WORKTREE_DIR}" diff --cached --quiet; then
    echo "No deploy changes to publish."
  else
    git -C "${WORKTREE_DIR}" commit -m "Publish public site"
    git -C "${WORKTREE_DIR}" push -u origin "${PAGES_BRANCH}"
    echo "Publish complete."
  fi

  if command -v gh >/dev/null 2>&1; then
    echo
    echo "Configuring GitHub Pages source to ${PAGES_BRANCH} / ..."
    gh api --method PUT "repos/${OWNER}/${REPO_NAME}/pages" \
      -f "source[branch]=${PAGES_BRANCH}" \
      -f "source[path]=/" >/dev/null
    echo "GitHub Pages source configured."
  else
    echo
    echo "warning: gh CLI not found; configure GitHub Pages source manually to branch=${PAGES_BRANCH} path=/" >&2
  fi

  echo
  echo "Pushing source branch ${BRANCH_NAME} to origin..."
  git -C "${REPO_ROOT}" push -u origin "${BRANCH_NAME}"
  echo "Source branch push complete."
else
  echo
  echo "Dry run only. Re-run with --push to publish the verified artifact."
fi
