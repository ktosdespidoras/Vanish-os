#!/usr/bin/env python3
"""
Vanish-OS Installation Engine
Executes disk partitioning, pacstrap, chroot setup, chaotic-aur configuration,
paru/yay deployment, desktop environment installation, and hardware/Wayland tuning.
"""

import os
import subprocess
import time
from typing import Dict, List, Callable

class InstallEngine:
    def __init__(self, config: Dict, log_callback: Callable[[str], None], progress_callback: Callable[[int], None]):
        self.config = config
        self.log = log_callback
        self.progress = progress_callback
        self.dry_run = os.environ.get("VANISH_DRY_RUN", "0") == "1" or not os.path.exists("/sys/firmware/efi")

    def run_cmd(self, cmd: List[str], chroot: bool = False) -> bool:
        cmd_str = " ".join(cmd)
        if chroot:
            cmd = ["arch-chroot", "/mnt"] + cmd
            cmd_str = f"arch-chroot /mnt {' '.join(cmd[2:])}"

        self.log(f"[RUN] {cmd_str}")

        if self.dry_run:
            time.sleep(0.4)
            return True

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            for line in process.stdout:
                self.log(line.strip())
            process.wait()
            return process.returncode == 0
        except Exception as e:
            self.log(f"[ERROR] Command failed: {e}")
            return False

    def write_file(self, path: str, content: str):
        self.log(f"[WRITE] {path}")
        if self.dry_run:
            return
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def execute(self) -> bool:
        try:
            self.log("=== VANISH-OS DEPLOYMENT INITIALIZED ===")
            if self.dry_run:
                self.log("[NOTICE] Running in DRY RUN / Virtual Mode (No real disk modifications).")

            # Step 1: Disk Partitioning (0% -> 15%)
            self.progress(5)
            self.log("Partitioning target drive...")
            disk = self.config.get("disk", "/dev/sda")
            if not self.partition_disk(disk):
                return False

            # Step 2: Pacstrap Base System with linux-zen (15% -> 40%)
            self.progress(15)
            self.log("Installing base system with linux-zen kernel...")
            base_packages = [
                "base", "base-devel", "linux-zen", "linux-zen-headers",
                "linux-firmware", "networkmanager", "sudo", "git",
                "curl", "wget", "nano", "fastfetch", "plymouth"
            ]
            # Add detected hardware drivers
            drivers = self.config.get("drivers", [])
            base_packages.extend(drivers)

            if not self.run_cmd(["pacstrap", "-K", "/mnt"] + base_packages):
                return False

            # Step 3: FSTAB Generation & System Basics (40% -> 50%)
            self.progress(40)
            self.log("Generating fstab and setting system locale...")
            self.run_cmd(["genfstab", "-U", "/mnt"], chroot=False)

            # Locale & Clock
            self.write_file("/mnt/etc/locale.gen", "en_US.UTF-8 UTF-8\nru_RU.UTF-8 UTF-8\n")
            self.run_cmd(["locale-gen"], chroot=True)
            self.write_file("/mnt/etc/locale.conf", "LANG=en_US.UTF-8\n")
            self.write_file("/mnt/etc/vconsole.conf", "KEYMAP=us\n")
            self.run_cmd(["ln", "-sf", "/usr/share/zoneinfo/UTC", "/mnt/etc/localtime"])
            self.run_cmd(["hwclock", "--systohc"], chroot=True)

            # Step 4: Hostname & Users (50% -> 60%)
            self.progress(50)
            hostname = self.config.get("hostname", "vanish-box")
            username = self.config.get("username", "user")
            password = self.config.get("password", "")

            self.write_file("/mnt/etc/hostname", f"{hostname}\n")
            self.write_file("/mnt/etc/hosts", f"127.0.0.1 localhost\n::1 localhost\n127.0.1.1 {hostname}.localdomain {hostname}\n")

            # Root without password (as requested)
            self.run_cmd(["passwd", "-d", "root"], chroot=True)

            # Create User
            if username:
                self.run_cmd(["useradd", "-m", "-G", "wheel,audio,video,storage,optical", "-s", "/bin/bash", username], chroot=True)
                if password:
                    self.run_cmd(["sh", "-c", f"echo '{username}:{password}' | chpasswd"], chroot=True)
                else:
                    self.run_cmd(["passwd", "-d", username], chroot=True)

                # Wheel sudo without password
                self.write_file("/mnt/etc/sudoers.d/10-vanish", "%wheel ALL=(ALL:ALL) NOPASSWD: ALL\n")

            # Step 5: Chaotic-AUR, Paru, Yay & Flatpak (60% -> 75%)
            self.progress(60)
            self.log("Setting up Chaotic-AUR repository, paru, yay, and Flatpak...")
            self.configure_chaotic_aur()

            # Step 6: Desktop Environment & Extra Software (75% -> 85%)
            self.progress(75)
            de = self.config.get("desktop", "hyprland")
            self.log(f"Deploying Desktop Environment: {de.upper()}...")
            self.install_desktop(de)

            # Custom selected software (Browsers, Shell, Dev, Gaming)
            extra_pkgs = self.config.get("extra_packages", [])
            if extra_pkgs:
                self.log(f"Installing user selected tools: {', '.join(extra_pkgs)}")
                self.run_cmd(["pacman", "-S", "--noconfirm", "--needed"] + extra_pkgs, chroot=True)

            # Step 7: Hardware & Wayland Crash Shield Configuration (85% -> 92%)
            self.progress(85)
            self.log("Hardening Wayland & NVIDIA power management...")
            self.apply_wayland_nvidia_shield()

            # Step 8: Bootloader & Plymouth Theme (92% -> 100%)
            self.progress(92)
            self.log("Configuring bootloader and Vanish Plymouth splash...")
            self.configure_bootloader()

            # Enable NetworkManager
            self.run_cmd(["systemctl", "enable", "NetworkManager"], chroot=True)

            self.progress(100)
            self.log("=== VANISH-OS INSTALLATION COMPLETE! YOU MAY NOW REBOOT. ===")
            return True

        except Exception as e:
            self.log(f"[FATAL] Deployment failed: {e}")
            return False

    def partition_disk(self, disk: str) -> bool:
        self.log(f"Partitioning {disk} (GPT, 512M EFI FAT32, Root Ext4)...")
        # Wipe partition table
        self.run_cmd(["parted", "-s", disk, "mklabel", "gpt"])
        # EFI partition (512MB)
        self.run_cmd(["parted", "-s", disk, "mkpart", "ESP", "fat32", "1MiB", "513MiB"])
        self.run_cmd(["parted", "-s", disk, "set", "1", "esp", "on"])
        # Root partition (rest of disk)
        self.run_cmd(["parted", "-s", disk, "mkpart", "primary", "ext4", "513MiB", "100%"])

        part_p = "p" if ("nvme" in disk or "mmcblk" in disk) else ""
        p1 = f"{disk}{part_p}1"
        p2 = f"{disk}{part_p}2"

        self.run_cmd(["mkfs.fat", "-F32", p1])
        self.run_cmd(["mkfs.ext4", "-F", p2])

        self.run_cmd(["mount", p2, "/mnt"])
        os.makedirs("/mnt/boot", exist_ok=True)
        self.run_cmd(["mount", p1, "/mnt/boot"])
        return True

    def configure_chaotic_aur(self):
        # Enable multilib
        pacman_conf_path = "/mnt/etc/pacman.conf"
        if not self.dry_run and os.path.exists(pacman_conf_path):
            with open(pacman_conf_path, "r") as f:
                content = f.read()

            if "[multilib]" not in content:
                content += "\n[multilib]\nInclude = /etc/pacman.d/mirrorlist\n"

            # Add chaotic-aur repo
            chaotic_block = """
[chaotic-aur]
Include = /etc/pacman.d/chaotic-mirrorlist
"""
            if "[chaotic-aur]" not in content:
                content += chaotic_block

            with open(pacman_conf_path, "w") as f:
                f.write(content)

        # Keys and mirrorlist for chaotic-aur
        self.run_cmd(["pacman-key", "--recv-key", "3056513887B78AEB", "--keyserver", "keyserver.ubuntu.com"], chroot=True)
        self.run_cmd(["pacman-key", "--lsign-key", "3056513887B78AEB"], chroot=True)
        self.run_cmd(["pacman", "-U", "--noconfirm", "https://cdn-mirror.chaotic.cx/chaotic-aur/chaotic-keyring.pkg.tar.zst"], chroot=True)
        self.run_cmd(["pacman", "-U", "--noconfirm", "https://cdn-mirror.chaotic.cx/chaotic-aur/chaotic-mirrorlist.pkg.tar.zst"], chroot=True)

        # Install yay and paru directly from chaotic-aur (pre-compiled binary!)
        self.run_cmd(["pacman", "-Sy", "--noconfirm", "paru", "yay", "flatpak"], chroot=True)

    def install_desktop(self, de: str):
        de_pkgs = {
            "hyprland": [
                "hyprland", "waybar", "kitty", "rofi-wayland", "dunst",
                "swaybg", "grim", "slurp", "wl-clipboard", "polkit-kde-agent",
                "thunar", "tumbler", "ffmpegthumbnailer"
            ],
            "kde": [
                "plasma-meta", "kde-applications-meta", "sddm", "dolphin", "konsole"
            ],
            "gnome": [
                "gnome", "gnome-extra", "gdm"
            ],
            "xfce": [
                "xfce4", "xfce4-goodies", "lightdm", "lightdm-gtk-greeter", "thunar"
            ]
        }

        pkgs = de_pkgs.get(de, de_pkgs["hyprland"])
        self.run_cmd(["pacman", "-S", "--noconfirm", "--needed"] + pkgs, chroot=True)

        # Display manager enablement
        if de == "kde":
            self.run_cmd(["systemctl", "enable", "sddm"], chroot=True)
        elif de == "gnome":
            self.run_cmd(["systemctl", "enable", "gdm"], chroot=True)
        elif de == "xfce":
            self.run_cmd(["systemctl", "enable", "lightdm"], chroot=True)

    def apply_wayland_nvidia_shield(self):
        # Write /etc/environment Wayland shield variables
        env_vars = self.config.get("wayland_env_vars", {})
        env_content = "\n# Vanish-OS Wayland Stability Shield\n"
        for k, v in env_vars.items():
            env_content += f"{k}={v}\n"

        env_file = "/mnt/etc/environment"
        if not self.dry_run and os.path.exists(env_file):
            with open(env_file, "a") as f:
                f.write(env_content)
        else:
            self.write_file(env_file, env_content)

        # If NVIDIA is present, enable systemd VRAM preservation services
        has_nvidia = self.config.get("has_nvidia", False)
        if has_nvidia:
            self.run_cmd(["systemctl", "enable", "nvidia-suspend.service"], chroot=True)
            self.run_cmd(["systemctl", "enable", "nvidia-hibernate.service"], chroot=True)
            self.run_cmd(["systemctl", "enable", "nvidia-resume.service"], chroot=True)

    def configure_bootloader(self):
        # Configure Plymouth hooks in mkinitcpio.conf
        mkinit_path = "/mnt/etc/mkinitcpio.conf"
        if not self.dry_run and os.path.exists(mkinit_path):
            with open(mkinit_path, "r") as f:
                lines = f.readlines()
            new_lines = []
            for line in lines:
                if line.strip().startswith("HOOKS="):
                    new_lines.append('HOOKS=(base udev plymouth autodetect modconf block filesystems keyboard fsck)\n')
                else:
                    new_lines.append(line)
            with open(mkinit_path, "w") as f:
                f.writelines(new_lines)

        self.run_cmd(["mkinitcpio", "-P"], chroot=True)

        # Install systemd-boot
        self.run_cmd(["bootctl", "--path=/boot", "install"], chroot=True)

        kernel_params = self.config.get("kernel_params", [])
        params_str = " ".join(kernel_params) + " quiet splash rw"

        entry_content = f"""title   Vanish-OS (Zen Kernel)
linux   /vmlinuz-linux-zen
initrd  /initramfs-linux-zen.img
options root=PARTLABEL=primary {params_str}
"""
        self.write_file("/mnt/boot/loader/entries/vanish.conf", entry_content)
        self.write_file("/mnt/boot/loader/loader.conf", "default vanish.conf\ntimeout 3\nconsole-mode max\n")
