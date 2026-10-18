# Excerpt from /opt/annonos/boot/annon_secure_boot.sh

# 2. Trigger Role-Specific Visual Boot Animation
echo "[SecureBoot]: Detecting device persona and rendering dedicated splash sequence..."
python3 /opt/annonos/boot/framebuffer_splash.py

# 3. Broadcast Audible Accessibility Greeting (Runs for both, reminding commands)
echo "[SecureBoot]: Broadcasting accessibility greeting..."
python3 /opt/annonos/core/accessibility/startup_greeting.py

# 4. Hand over execution to kernel init
exec /sbin/init
