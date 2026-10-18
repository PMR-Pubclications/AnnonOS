#!/bin/sh
# /opt/annonos/core/kernel/mount_ephemeral.sh
# Ensures temporary storage folders run entirely in RAM (tmpfs) on the read-only SquashFS image.

mount -t tmpfs -o size=64M tmpfs /tmp
mount -t tmpfs -o size=32M tmpfs /var/log
echo "[AnnonOS] Ephemeral volatile memory overlays mounted successfully."
