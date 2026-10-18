#!/bin/sh
# /board/annonos-target/post-build.sh
# AnnonOS Post-Build Hardening Script.
# Enforces strict file permissions, locks cryptographic directories,
# and hooks the secure bootloader into the init chain.

TARGET_DIR=$1

echo "[PostBuild]: Enforcing AnnonOS security and file permissions..."

# Ensure core directories exist
mkdir -p ${TARGET_DIR}/opt/annonos/core/security/keys
mkdir -p ${TARGET_DIR}/opt/annonos/data
mkdir -p ${TARGET_DIR}/opt/annonos/www

# Lock down cryptographic key storage and sensitive database paths
chmod 700 ${TARGET_DIR}/opt/annonos/core/security/keys
chmod 755 ${TARGET_DIR}/opt/annonos/core/
chmod +x ${TARGET_DIR}/opt/annonos/boot/annon_secure_boot.sh
chmod +x ${TARGET_DIR}/opt/annonos/boot/framebuffer_splash.py
chmod +x ${TARGET_DIR}/opt/annonos/core/accessibility/startup_greeting.py

# Configure immutable SquashFS mount points and initial init hook
ln -sf /opt/annonos/boot/annon_secure_boot.sh ${TARGET_DIR}/sbin/annon-init

echo "[PostBuild]: Rootfs hardening and file system overlay successfully applied."
