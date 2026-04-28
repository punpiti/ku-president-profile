#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SITE_DIR="${1:-${PUBLIC_SITE_BUILD_DIR:-${REPO_ROOT}/.public-site-build}}"

if [[ ! -d "${SITE_DIR}" ]]; then
  echo "error: deploy directory not found: ${SITE_DIR}" >&2
  exit 1
fi

if [[ ! -f "${SITE_DIR}/index.html" ]]; then
  echo "error: missing ${SITE_DIR}/index.html" >&2
  exit 1
fi

path_hits="$(
  find "${SITE_DIR}" \
    \( -path '*/question-bank/*' \
    -o -path '*/presentation-narrator/*' \
    -o -path '*/qna/*' \
    -o -path '*/sources/*' \
    -o -path '*/selection/*' \
    -o -path '*/print/*' \
    -o -name '*question_bank_priority_queue*' \
    -o -name '*presentation_narrator_a4*' \
    -o -name '*.md' \
    -o -name '*.bak' \
    -o -name '.codex' \) -print
)"

if [[ -n "${path_hits}" ]]; then
  echo "error: deploy directory contains blocked paths:" >&2
  echo "${path_hits}" >&2
  exit 1
fi

if rg -n \
  'vision/(question-bank|presentation-narrator|sources)|qna_raw|selection/(application|reference|profiles)|question_bank_priority_queue|presentation_narrator_a4|Version To Actually Say|Answer I Will Actually Give' \
  "${SITE_DIR}" >/tmp/public_deploy_safety_hits.txt; then
  echo "error: deploy directory contains blocked private/workspace references:" >&2
  cat /tmp/public_deploy_safety_hits.txt >&2
  exit 1
fi

echo "Public deploy safety check passed: ${SITE_DIR}"
