#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  bash scripts/run_local.sh <project> [port]
  PORT=9000 HOST=0.0.0.0 bash scripts/run_local.sh <project>

Projects:
  public   public website source from vision/public-site/
  vision   vision workspace from vision/

Aliases:
  public-site, site -> public
  public-build, deploy-artifact -> local deploy artifact in .public-site-build/
  vision-qna, qna -> vision
  question-bank, question_bank -> vision/question-bank
  presentation-narrator, presentation_narrator -> vision/presentation-narrator

Examples:
  bash scripts/run_local.sh public
  bash scripts/run_local.sh vision 9000
EOF
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
HOST="${HOST:-127.0.0.1}"
DEFAULT_PORT="${PORT:-8000}"

TARGET_ARG="${1:-}"
PORT_ARG="${2:-}"

if [[ -z "${TARGET_ARG}" ]]; then
  usage
  exit 0
elif [[ "${TARGET_ARG}" == "-h" || "${TARGET_ARG}" == "--help" ]]; then
  usage
  exit 0
elif [[ "${TARGET_ARG}" =~ ^[0-9]+$ ]]; then
  echo "error: missing project name before port: ${TARGET_ARG}" >&2
  echo >&2
  usage >&2
  exit 1
else
  TARGET="${TARGET_ARG}"
  PORT="${PORT_ARG:-${DEFAULT_PORT}}"
fi

case "${TARGET}" in
  site|public|public-site)
    SITE_DIR="${REPO_ROOT}/vision/public-site"
    ;;
  public-build|deploy-artifact)
    SITE_DIR="${PUBLIC_SITE_BUILD_DIR:-${REPO_ROOT}/.public-site-build}"
    ;;
  vision|vision-qna|qna)
    SITE_DIR="${REPO_ROOT}/vision"
    ;;
  question-bank|question_bank)
    SITE_DIR="${REPO_ROOT}/vision/question-bank"
    ;;
  presentation-narrator|presentation_narrator)
    SITE_DIR="${REPO_ROOT}/vision/presentation-narrator"
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
