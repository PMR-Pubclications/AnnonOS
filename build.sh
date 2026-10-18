#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BR_DIR="${REPO_ROOT}/buildroot"
DEFCONFIG="${ANNONOS_DEFCONFIG:-annonos_iso_defconfig}"

if [[ ! -d "${BR_DIR}" ]]; then
  echo "ERROR: buildroot directory not found at ${BR_DIR}" >&2
  exit 1
fi

cd "${BR_DIR}"

if [[ ! -f Makefile ]]; then
  echo "ERROR: ${BR_DIR} does not contain a Buildroot source tree (no Makefile)" >&2
  exit 1
fi

make distclean
make "${DEFCONFIG}"
make -j"$(nproc)"

echo
echo "Build complete (${DEFCONFIG}). Images are in: ${BR_DIR}/output/images/"
ls -lah "${BR_DIR}/output/images/"
