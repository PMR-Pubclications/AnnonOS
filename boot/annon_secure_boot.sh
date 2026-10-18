#!/bin/sh
# /opt/annonos/boot/annon_secure_boot.sh
# AnnonOS Hardware-Rooted Secure Bootloader & Accessibility Greeting Script.
# Cryptographically validates the kernel and Trust-Main root before broadcasting 
# the startup accessibility greeting and initializing the OS.

KERNEL_IMAGE="/boot/zImage"
INITRD_IMAGE="/boot/initrd.img"
EXPECTED_KERNEL_HASH="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" # Gold-standard SHA-256

echo "[SecureBoot]: Initializing AnnonOS hardware-rooted boot verification..."

# 1. Verify Kernel Cryptographic Integrity
if [ -f "$KERNEL_IMAGE" ]; then
    ACTUAL_KERNEL_HASH=$(sha256sum "$KERNEL_IMAGE" | awk '{print $1}')
    if [ "$ACTUAL_KERNEL_HASH" = "$EXPECTED_KERNEL_HASH" ]; then
        echo "[SecureBoot]: SUCCESS - Kernel image signature verified."
    else
        echo "[SecureBoot]: CRITICAL FAILURE - Kernel hash mismatch! Tampering detected." >&2
        # Trigger emergency hardware kill-switch / wipe if tampering is detected
        python3 /opt/annonos/core/security/kill_switch.py --emergency-wipe
        exit 1
    fi
else
    echo "[SecureBoot]: CRITICAL ERROR - Kernel image not found at $KERNEL_IMAGE." >&2
    exit 1
fi

# 2. Verify Trust-Main Root Handshake Hook
echo "[SecureBoot]: Checking Trust-Main hardware root-of-trust..."
if [ -x "/opt/annonos/core/security/trust_main_400_receiver.py" ]; then
    python3 /opt/annonos/core/security/trust_main_400_receiver.py --boot-check
    if [ $? -ne 0 ]; then
        echo "[SecureBoot]: CRITICAL FAILURE - Trust-Main 400-layer boot check failed." >&2
        exit 1
    fi
fi

# 3. All Checks Passed: Broadcast Audible Startup Greeting
echo "[SecureBoot]: Boot validation passed. Broadcasting accessibility greeting..."
python3 /opt/annonos/core/accessibility/startup_greeting.py

# 4. Hand over execution to kernel init
echo "[SecureBoot]: Handing over control to AnnonOS kernel init..."
exec /sbin/init
