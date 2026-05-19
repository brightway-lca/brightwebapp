#!/usr/bin/env bash
set -euo pipefail

JOURNAL="${JOURNAL:-jose}"
PAPER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

docker run --rm \
    --volume "${PAPER_DIR}:/data" \
    --user "$(id -u):$(id -g)" \
    --env "JOURNAL=${JOURNAL}" \
    openjournals/inara

echo "Rendered: ${PAPER_DIR}/paper.pdf"
