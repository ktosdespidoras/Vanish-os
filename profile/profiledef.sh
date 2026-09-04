#!/usr/bin/env bash
# Vanish-OS Archiso Profile Definition

iso_name="vanish-os"
iso_label="VANISH_$(date +%Y%m)"
iso_publisher="Vanish-OS <https://github.com/vanish-os>"
iso_application="Vanish-OS Live & Installer System"
iso_version="$(date +%Y.%m.%d)"
install_dir="arch"
buildmodes=('iso')
bootmodes=('bios.syslinux.mbr' 'bios.syslinux.eltorito'
           'uefi-ia32.systemd-boot.esp' 'uefi-x64.systemd-boot.esp'
           'uefi-ia32.systemd-boot.eltorito' 'uefi-x64.systemd-boot.eltorito')
arch="x86_64"
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
airootfs_image_tool_options=('-comp' 'zstd')
file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/root"]="0:0:750"
  ["/usr/local/bin/vanish-installer"]="0:0:755"
)
