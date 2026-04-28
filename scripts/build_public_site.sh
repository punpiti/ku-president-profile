#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SOURCE_DIR="${REPO_ROOT}/vision/public-site"
TARGET_DIR="${PUBLIC_SITE_BUILD_DIR:-${REPO_ROOT}/.public-site-build}"

if [[ ! -d "${SOURCE_DIR}" ]]; then
  echo "error: public site source not found: ${SOURCE_DIR}" >&2
  exit 1
fi

if [[ ! -f "${SOURCE_DIR}/index.html" ]]; then
  echo "error: missing ${SOURCE_DIR}/index.html" >&2
  exit 1
fi

mkdir -p "${TARGET_DIR}"

rsync -a --delete \
  --include='*/' \
  --include='*.html' \
  --include='*.css' \
  --include='*.js' \
  --include='*.json' \
  --include='*.xml' \
  --include='*.txt' \
  --include='*.ico' \
  --include='*.png' \
  --include='*.jpg' \
  --include='*.jpeg' \
  --include='*.JPG' \
  --include='*.JPEG' \
  --include='*.svg' \
  --include='*.webp' \
  --include='*.pdf' \
  --include='*.download' \
  --exclude='.codex' \
  --exclude='*.bak' \
  --exclude='README.md' \
  --exclude='ARCHIVE_PAGE_TEMPLATE.md' \
  --exclude='*' \
"${SOURCE_DIR}/" "${TARGET_DIR}/"

"${SCRIPT_DIR}/check_public_deploy_safety.sh" "${TARGET_DIR}"
