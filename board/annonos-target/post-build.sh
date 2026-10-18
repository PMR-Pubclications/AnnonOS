#!/bin/sh
# /board/annonos-target/post-build.sh
# AnnonOS Post-Build Hardening Script.
# Enforces strict file permissions, locks cryptographic directories,
# and hooks the secure bootloader into the init chain.

set -eu

TARGET_DIR="$1"

echo "[PostBuild]: Enforcing AnnonOS security and file permissions..."

# Ensure core directories exist
mkdir -p "${TARGET_DIR}/opt/annonos/core/security/keys"
mkdir -p "${TARGET_DIR}/opt/annonos/data"
mkdir -p "${TARGET_DIR}/opt/annonos/www"
mkdir -p "${TARGET_DIR}/sbin"

# Lock down cryptographic key storage and sensitive database paths
chmod 700 "${TARGET_DIR}/opt/annonos/core/security/keys"
chmod 755 "${TARGET_DIR}/opt/annonos/core/"
for f in boot/annon_secure_boot.sh boot/framebuffer_splash.py core/accessibility/startup_greeting.py; do
    if [ -f "${TARGET_DIR}/opt/annonos/${f}" ]; then
        chmod +x "${TARGET_DIR}/opt/annonos/${f}"
    fi
done

# Configure immutable SquashFS mount points and initial init hook
ln -sf /opt/annonos/boot/annon_secure_boot.sh "${TARGET_DIR}/sbin/annon-init"

echo "[PostBuild]: Rootfs hardening and file system overlay successfully applied."
