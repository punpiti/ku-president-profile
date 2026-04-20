#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
HOST="${HOST:-127.0.0.1}"
DEFAULT_TARGET="site"
DEFAULT_PORT="${PORT:-8000}"

TARGET_ARG="${1:-}"
PORT_ARG="${2:-}"

if [[ -z "${TARGET_ARG}" ]]; then
  TARGET="${DEFAULT_TARGET}"
  PORT="${DEFAULT_PORT}"
elif [[ "${TARGET_ARG}" =~ ^[0-9]+$ ]]; then
  TARGET="${DEFAULT_TARGET}"
  PORT="${TARGET_ARG}"
else
  TARGET="${TARGET_ARG}"
  PORT="${PORT_ARG:-${DEFAULT_PORT}}"
fi

case "${TARGET}" in
  site)
    SITE_DIR="${REPO_ROOT}/docs"
    ;;
  qna|question_bank)
    SITE_DIR="${REPO_ROOT}/vision/qna/question_bank"
    ;;
  /*)
    SITE_DIR="${TARGET}"
    ;;
  *)
    SITE_DIR="${REPO_ROOT}/${TARGET}"
    ;;
esac

if [[ ! -d "${SITE_DIR}" ]]; then
  echo "error: site directory not found: ${SITE_DIR}" >&2
  exit 1
fi

if [[ ! -f "${SITE_DIR}/index.html" ]]; then
  echo "error: missing ${SITE_DIR}/index.html" >&2
  exit 1
fi

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "error: python or python3 is required to run the local dev server" >&2
  exit 1
fi

echo "Serving ${SITE_DIR}"
echo "URL: http://${HOST}:${PORT}/"
echo "Press Ctrl+C to stop"

cd "${SITE_DIR}"
exec "${PYTHON_BIN}" -m http.server "${PORT}" --bind "${HOST}"
