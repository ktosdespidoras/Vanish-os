#!/usr/bin/env bash
# Vanish-OS ISO Build Pipeline
set -e

echo "=== BUILDING VANISH-OS ISO (ZEN KERNEL) ==="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
PROFILE_DIR="$ROOT_DIR/profile"
WORK_DIR="/tmp/vanish-work"
OUT_DIR="$ROOT_DIR/out"

# Verify root
if [ "$EUID" -ne 0 ]; then
  echo "[ERROR] mkarchiso requires root privileges. Run with sudo."
  exit 1
fi

# Ensure archiso is installed
if ! command -v mkarchiso &> /dev/null; then
    echo "[SETUP] Installing archiso..."
    pacman -Sy --noconfirm archiso
fi

# Copy installer into airootfs overlay
echo "[PREP] Injecting Vanish-Installer into live image..."
mkdir -p "$PROFILE_DIR/airootfs/usr/local/bin"
mkdir -p "$PROFILE_DIR/airootfs/opt/vanish-installer"
mkdir -p "$PROFILE_DIR/airootfs/usr/share/plymouth/themes/vanish"

# Copy installer source
cp -r "$ROOT_DIR/installer/"* "$PROFILE_DIR/airootfs/opt/vanish-installer/"
# Copy Plymouth theme
cp -r "$ROOT_DIR/branding/plymouth/"* "$PROFILE_DIR/airootfs/usr/share/plymouth/themes/vanish/"

# Create launch wrapper
cat << 'EOF' > "$PROFILE_DIR/airootfs/usr/local/bin/vanish-installer"
#!/usr/bin/env bash
cd /opt/vanish-installer
python3 main.py
EOF
chmod +x "$PROFILE_DIR/airootfs/usr/local/bin/vanish-installer"

# Autostart X11 + Openbox + Installer for live root
mkdir -p "$PROFILE_DIR/airootfs/root/.config/openbox"
cat << 'EOF' > "$PROFILE_DIR/airootfs/root/.config/openbox/autostart"
xset -dpms s off &
vanish-installer &
EOF

mkdir -p "$PROFILE_DIR/airootfs/etc/systemd/system/getty@tty1.service.d"
cat << 'EOF' > "$PROFILE_DIR/airootfs/etc/systemd/system/getty@tty1.service.d/autologin.conf"
[Service]
ExecStart=
ExecStart=-/sbin/agetty -o '-p -f -- \\u' --noclear --autologin root %I $TERM
EOF

# Build ISO
mkdir -p "$OUT_DIR"
rm -rf "$WORK_DIR"

echo "[BUILD] Executing mkarchiso..."
mkarchiso -v -w "$WORK_DIR" -o "$OUT_DIR" "$PROFILE_DIR"

echo "=== BUILD SUCCESSFUL ==="
echo "ISO output available at: $OUT_DIR"
ls -lh "$OUT_DIR"
