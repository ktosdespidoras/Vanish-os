#!/usr/bin/env bash
# Vanish-OS ISO Build Pipeline — Powered by Arch Releng Base
set -e

echo "=== BUILDING VANISH-OS ISO (ZEN KERNEL) ==="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
WORK_DIR="/tmp/vanish-work"
OUT_DIR="$ROOT_DIR/out"
CUSTOM_PROFILE="/tmp/vanish-profile"

# Check root
if [ "$EUID" -ne 0 ]; then
  echo "[ERROR] mkarchiso requires root privileges. Run with sudo."
  exit 1
fi

# Ensure keyring and mirrors are operational
echo "[INIT] Setting up pacman keys and mirrors..."
pacman-key --init || true
pacman-key --populate archlinux || true

mkdir -p /etc/pacman.d
echo 'Server = https://geo.mirror.pkgbuild.com/$repo/os/$arch' > /etc/pacman.d/mirrorlist

# Ensure archiso is installed
if ! command -v mkarchiso &> /dev/null; then
    echo "[SETUP] Installing archiso..."
    pacman -Sy --noconfirm archiso
fi

echo "[BASE] Cloning official Arch Linux releng profile..."
rm -rf "$CUSTOM_PROFILE"
cp -r /usr/share/archiso/configs/releng "$CUSTOM_PROFILE"

echo "[CUSTOMIZE] Applying Vanish-OS branding and Zen kernel..."

# 1. Update profiledef.sh metadata
sed -i 's/iso_name="archlinux"/iso_name="vanish-os"/' "$CUSTOM_PROFILE/profiledef.sh"
sed -i 's/iso_label="ARCH_[0-9]*/iso_label="VANISH_$(date +%Y%m)"/' "$CUSTOM_PROFILE/profiledef.sh"

# Add vanish-installer permissions
cat << 'EOF' >> "$CUSTOM_PROFILE/profiledef.sh"
file_permissions+=(
  ["/usr/local/bin/vanish-installer"]="0:0:755"
)
EOF

# 2. Update packages.x86_64: Replace standard linux with linux-zen and add Vanish stack
sed -i 's/^linux$/linux-zen/' "$CUSTOM_PROFILE/packages.x86_64"
cat << 'EOF' >> "$CUSTOM_PROFILE/packages.x86_64"
linux-zen-headers
python
python-pyqt6
plymouth
xorg-server
xorg-xinit
openbox
kitty
mesa
vulkan-intel
vulkan-radeon
pipewire
wireplumber
EOF

# 3. Inject Vanish-Installer & Plymouth branding into airootfs
echo "[PREP] Injecting Vanish-Installer & Plymouth Theme..."
mkdir -p "$CUSTOM_PROFILE/airootfs/usr/local/bin"
mkdir -p "$CUSTOM_PROFILE/airootfs/opt/vanish-installer"
mkdir -p "$CUSTOM_PROFILE/airootfs/usr/share/plymouth/themes/vanish"

cp -r "$ROOT_DIR/installer/"* "$CUSTOM_PROFILE/airootfs/opt/vanish-installer/"
cp -r "$ROOT_DIR/branding/plymouth/"* "$CUSTOM_PROFILE/airootfs/usr/share/plymouth/themes/vanish/"

# Create launch wrapper
cat << 'EOF' > "$CUSTOM_PROFILE/airootfs/usr/local/bin/vanish-installer"
#!/usr/bin/env bash
cd /opt/vanish-installer
python3 main.py
EOF
chmod +x "$CUSTOM_PROFILE/airootfs/usr/local/bin/vanish-installer"

# Setup Openbox live desktop autostart
mkdir -p "$CUSTOM_PROFILE/airootfs/root/.config/openbox"
cat << 'EOF' > "$CUSTOM_PROFILE/airootfs/root/.config/openbox/autostart"
xset -dpms s off &
vanish-installer &
EOF

# Ensure X11 starts on TTY1 autologin
cat << 'EOF' >> "$CUSTOM_PROFILE/airootfs/root/.bash_profile"
if [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then
    startx
fi
EOF

cat << 'EOF' > "$CUSTOM_PROFILE/airootfs/root/.xinitrc"
exec openbox-session
EOF

# Build ISO
mkdir -p "$OUT_DIR"
rm -rf "$WORK_DIR"

echo "[BUILD] Executing mkarchiso..."
mkarchiso -v -w "$WORK_DIR" -o "$OUT_DIR" "$CUSTOM_PROFILE"

echo "=== BUILD SUCCESSFUL ==="
echo "ISO output available at: $OUT_DIR"
ls -lh "$OUT_DIR"
