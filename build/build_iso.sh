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

# Ensure archiso and python are installed
if ! command -v mkarchiso &> /dev/null; then
    echo "[SETUP] Installing archiso..."
    pacman -Sy --noconfirm archiso python
fi

echo "[BASE] Cloning official Arch Linux releng profile..."
rm -rf "$CUSTOM_PROFILE"
cp -r /usr/share/archiso/configs/releng "$CUSTOM_PROFILE"

echo "[CUSTOMIZE] Applying Vanish-OS branding and Zen kernel..."

# Bulletproof customization via Python (avoids sed regex escaping bugs)
python3 - << 'PYEOF'
profiledef_path = "/tmp/vanish-profile/profiledef.sh"
with open(profiledef_path, "r") as f:
    content = f.read()

# Replace ISO Name and Application
content = content.replace('iso_name="archlinux"', 'iso_name="vanish-os"')
content = content.replace('iso_publisher="Arch Linux <https://archlinux.org>"', 'iso_publisher="Vanish-OS <https://github.com/ktosdespidoras/Vanish-os>"')
content = content.replace('iso_application="Arch Linux Live/Rescue medium"', 'iso_application="Vanish-OS Live & Installer"')

# Inject file permission safely
target_perm = '["/etc/shadow"]="0:0:400"'
new_perm = '["/etc/shadow"]="0:0:400"\n  ["/usr/local/bin/vanish-installer"]="0:0:755"'
content = content.replace(target_perm, new_perm)

with open(profiledef_path, "w") as f:
    f.write(content)

# Update packages list: replace linux with linux-zen
packages_path = "/tmp/vanish-profile/packages.x86_64"
with open(packages_path, "r") as f:
    pkgs = f.read().splitlines()

new_pkgs = []
for p in pkgs:
    if p.strip() == "linux":
        new_pkgs.append("linux-zen")
        new_pkgs.append("linux-zen-headers")
    else:
        new_pkgs.append(p)

# Append Vanish stack
vanish_stack = [
    "python",
    "python-pyqt6",
    "plymouth",
    "xorg-server",
    "xorg-xinit",
    "openbox",
    "kitty",
    "mesa",
    "vulkan-intel",
    "vulkan-radeon",
    "pipewire",
    "wireplumber"
]
for vp in vanish_stack:
    if vp not in new_pkgs:
        new_pkgs.append(vp)

with open(packages_path, "w") as f:
    f.write("\n".join(new_pkgs) + "\n")

print("[PYTHON HOOK] Successfully patched profiledef.sh and packages.x86_64!")
PYEOF

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
