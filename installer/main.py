#!/usr/bin/env python3
"""
Vanish-OS — Minimalist Dark GUI Installer
Powered by PySide6 / PyQt6 with Hardware Diagnostics, Dynamic DE Selector, and Anti-Crash Wayland Shield.
"""

import sys
import os

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QStackedWidget, QRadioButton, QButtonGroup,
        QCheckBox, QComboBox, QLineEdit, QProgressBar, QPlainTextEdit,
        QFrame, QScrollArea
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal as Signal
except ImportError:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QStackedWidget, QRadioButton, QButtonGroup,
        QCheckBox, QComboBox, QLineEdit, QProgressBar, QPlainTextEdit,
        QFrame, QScrollArea
    )
    from PySide6.QtCore import Qt, QThread, Signal

from styles import DARK_THEME
from detector import HardwareDetector, HardwareProfile
from engine import InstallEngine

class WorkerThread(QThread):
    log_signal = Signal(str)
    progress_signal = Signal(int)
    done_signal = Signal(bool)

    def __init__(self, config: dict):
        super().__init__()
        self.config = config

    def run(self):
        engine = InstallEngine(
            self.config,
            log_callback=lambda msg: self.log_signal.emit(msg),
            progress_callback=lambda p: self.progress_signal.emit(p)
        )
        success = engine.execute()
        self.done_signal.emit(success)

class VanishInstallerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vanish-OS Installer")
        self.resize(960, 640)
        self.setStyleSheet(DARK_THEME)

        self.detector = HardwareDetector()
        self.profile = self.detector.analyze()

        self.current_page = 0
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left Navigation Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(24, 28, 24, 28)
        side_layout.setSpacing(16)

        logo_title = QLabel("VANISH-OS")
        logo_title.setObjectName("title")
        side_layout.addWidget(logo_title)

        kernel_badge = QLabel("LINUX-ZEN 6.x")
        kernel_badge.setObjectName("badge_info")
        side_layout.addWidget(kernel_badge)

        side_layout.addSpacing(20)

        # Step labels
        self.step_labels = [
            QLabel("1. Hardware Shield"),
            QLabel("2. Desktop Choice"),
            QLabel("3. Software & Tools"),
            QLabel("4. Disk & Storage"),
            QLabel("5. Identity & Access"),
            QLabel("6. Installation")
        ]
        for idx, lbl in enumerate(self.step_labels):
            lbl.setStyleSheet("color: #71717a; font-weight: 600; font-size: 13px;")
            side_layout.addWidget(lbl)

        side_layout.addStretch()

        status_lbl = QLabel("SYSTEM: READY")
        status_lbl.setObjectName("badge_success")
        side_layout.addWidget(status_lbl)

        main_layout.addWidget(sidebar)

        # Right Content Area
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(36, 32, 36, 32)
        content_layout.setSpacing(20)

        # Stacked Pages
        self.pages = QStackedWidget()
        self.page_hardware = self.create_page_hardware()
        self.page_desktop = self.create_page_desktop()
        self.page_software = self.create_page_software()
        self.page_disk = self.create_page_disk()
        self.page_identity = self.create_page_identity()
        self.page_install = self.create_page_install()

        self.pages.addWidget(self.page_hardware)
        self.pages.addWidget(self.page_desktop)
        self.pages.addWidget(self.page_software)
        self.pages.addWidget(self.page_disk)
        self.pages.addWidget(self.page_identity)
        self.pages.addWidget(self.page_install)

        content_layout.addWidget(self.pages)

        # Bottom Controls
        bottom_bar = QHBoxLayout()
        self.btn_back = QPushButton("← Back")
        self.btn_back.clicked.connect(self.go_back)
        self.btn_back.setEnabled(False)

        self.btn_next = QPushButton("Next Step →")
        self.btn_next.setObjectName("btn_primary")
        self.btn_next.clicked.connect(self.go_next)

        bottom_bar.addWidget(self.btn_back)
        bottom_bar.addStretch()
        bottom_bar.addWidget(self.btn_next)

        content_layout.addLayout(bottom_bar)
        main_layout.addWidget(content_frame)

        self.update_sidebar()

    # --- Page 1: Hardware & Shield ---
    def create_page_hardware(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(14)

        title = QLabel("Hardware Diagnostics & Wayland Shield")
        title.setObjectName("section_title")
        subtitle = QLabel("Vanish-OS audits your system to prevent GPU freezes, broken DRM modes, and Wayland session crashes.")
        subtitle.setObjectName("subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Card: Detected Spec
        card_spec = QFrame()
        card_spec.setObjectName("card")
        spec_layout = QVBoxLayout(card_spec)

        lbl_cpu = QLabel(f"<b>CPU:</b> {self.profile.cpu_model}")
        lbl_ram = QLabel(f"<b>RAM:</b> {self.profile.ram_gb} GB")
        spec_layout.addWidget(lbl_cpu)
        spec_layout.addWidget(lbl_ram)

        for g in self.profile.gpus:
            lbl_gpu = QLabel(f"<b>GPU:</b> {g.model} <font color='#8b5cf6'>[{g.vendor.upper()}]</font>")
            spec_layout.addWidget(lbl_gpu)

        layout.addWidget(card_spec)

        # Card: Driver & Wayland Immunity Shield
        card_plan = QFrame()
        card_plan.setObjectName("card")
        plan_layout = QVBoxLayout(card_plan)

        if self.profile.is_hybrid_optimus:
            badge = QLabel("HYBRID INTEL/AMD + NVIDIA SHIELD: ACTIVE")
            badge.setObjectName("badge_warning")
            plan_layout.addWidget(badge)
            desc = QLabel(
                "Intel/AMD iGPU combined with NVIDIA dGPU detected.\n"
                "• Automatically installing: nvidia-dkms, egl-wayland, vulkan-intel/mesa, supergfxctl\n"
                "• Bootloader parameters: nvidia-drm.modeset=1 nvidia_drm.fbdev=1\n"
                "• VRAM preservation systemd services enabled to eliminate sleep/wake Wayland crashes."
            )
            desc.setStyleSheet("color: #fbbf24; font-size: 13px; line-height: 1.4;")
            plan_layout.addWidget(desc)
        else:
            badge = QLabel("STANDARD GRAPHICS PIPELINE")
            badge.setObjectName("badge_success")
            plan_layout.addWidget(badge)
            desc = QLabel(f"Configuring optimal display stack: {', '.join(self.profile.recommended_drivers[:5])}...")
            desc.setStyleSheet("color: #a1a1aa;")
            plan_layout.addWidget(desc)

        layout.addWidget(card_plan)
        layout.addStretch()
        return page

    # --- Page 2: Desktop Choice ---
    def create_page_desktop(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(14)

        title = QLabel("Select Desktop Environment")
        title.setObjectName("section_title")
        subtitle = QLabel("Choose the interface that will boot on your Vanish-OS install.")
        subtitle.setObjectName("subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        self.de_group = QButtonGroup()

        desktops = [
            ("hyprland", "Hyprland (Wayland Rice)", "Tiling window manager, GPU animations, Waybar panel, Kitty terminal, high-fps smooth feel."),
            ("kde", "KDE Plasma 6 (Modern Desktop)", "Modern, customizable desktop with Wayland support, Dolphin file manager, polished UI."),
            ("gnome", "GNOME 46 (Fluid Simplicity)", "Clean gesture-driven workflow, distraction-free interface, rock-solid Wayland compositor."),
            ("xfce", "XFCE 4 (Ultra Lightweight)", "Classic lightweight X11 desktop. Boots in 300MB RAM, zero lag, extreme reliability.")
        ]

        for idx, (de_id, de_title, de_desc) in enumerate(desktops):
            card = QFrame()
            card.setObjectName("card")
            c_layout = QVBoxLayout(card)

            radio = QRadioButton(de_title)
            if idx == 0:
                radio.setChecked(True)
            self.de_group.addButton(radio, idx)

            desc = QLabel(de_desc)
            desc.setStyleSheet("color: #a1a1aa; font-size: 12px; margin-left: 28px;")

            c_layout.addWidget(radio)
            c_layout.addWidget(desc)
            layout.addWidget(card)

        layout.addStretch()
        return page

    # --- Page 3: Software & Browsers ---
    def create_page_software(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(14)

        title = QLabel("Software Ecosystem & Default Tools")
        title.setObjectName("section_title")
        subtitle = QLabel("Select your preferred browser, shell, and extra software suites.")
        subtitle.setObjectName("subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        card_b = QFrame()
        card_b.setObjectName("card")
        b_layout = QVBoxLayout(card_b)
        b_layout.addWidget(QLabel("<b>Primary Web Browser:</b>"))
        self.combo_browser = QComboBox()
        self.combo_browser.addItems(["Brave Browser", "Firefox", "Librewolf", "Chromium", "None"])
        b_layout.addWidget(self.combo_browser)
        layout.addWidget(card_b)

        card_s = QFrame()
        card_s.setObjectName("card")
        s_layout = QVBoxLayout(card_s)
        s_layout.addWidget(QLabel("<b>Terminal Shell & Prompt:</b>"))
        self.combo_shell = QComboBox()
        self.combo_shell.addItems(["Zsh + Starship Prompt (Fast & Sleek)", "Fish (Friendly Interactive Shell)", "Standard Bash"])
        s_layout.addWidget(self.combo_shell)
        layout.addWidget(card_s)

        card_e = QFrame()
        card_e.setObjectName("card")
        e_layout = QVBoxLayout(card_e)
        e_layout.addWidget(QLabel("<b>Additional Toolkits:</b>"))

        self.cb_dev = QCheckBox("Developer Suite (VSCodium, Neovim, Git, Docker, GCC)")
        self.cb_dev.setChecked(True)
        self.cb_gaming = QCheckBox("Gaming Suite (Steam, Lutris, Wine-Staging, GameMode)")
        self.cb_gaming.setChecked(True)
        self.cb_aur = QCheckBox("Auto-install Paru & Yay from Chaotic-AUR")
        self.cb_aur.setChecked(True)
        self.cb_aur.setEnabled(False)

        e_layout.addWidget(self.cb_dev)
        e_layout.addWidget(self.cb_gaming)
        e_layout.addWidget(self.cb_aur)
        layout.addWidget(card_e)

        layout.addStretch()
        return page

    # --- Page 4: Disk & Storage ---
    def create_page_disk(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(14)

        title = QLabel("Target Drive & Partitioning")
        title.setObjectName("section_title")
        subtitle = QLabel("Select the storage drive to install Vanish-OS.")
        subtitle.setObjectName("subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        card = QFrame()
        card.setObjectName("card")
        c_layout = QVBoxLayout(card)

        c_layout.addWidget(QLabel("<b>Select Drive:</b>"))
        self.combo_disk = QComboBox()
        self.combo_disk.addItems(["/dev/nvme0n1 — 512 GB NVMe SSD", "/dev/sda — 1000 GB SATA SSD", "/dev/vda — 64 GB Virtual Disk"])
        c_layout.addWidget(self.combo_disk)

        warn_badge = QLabel("AUTOMATIC PARTITIONING: ENTIRE DRIVE WILL BE WIPED (GPT + EFI + EXT4)")
        warn_badge.setObjectName("badge_warning")
        c_layout.addWidget(warn_badge)

        layout.addWidget(card)
        layout.addStretch()
        return page

    # --- Page 5: Identity & Access ---
    def create_page_identity(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(14)

        title = QLabel("Identity & Access Privileges")
        title.setObjectName("section_title")
        subtitle = QLabel("Configure root access and standard user account.")
        subtitle.setObjectName("subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        card = QFrame()
        card.setObjectName("card")
        c_layout = QVBoxLayout(card)

        c_layout.addWidget(QLabel("<b>Computer Hostname:</b>"))
        self.inp_hostname = QLineEdit("vanish-box")
        c_layout.addWidget(self.inp_hostname)

        c_layout.addWidget(QLabel("<b>Standard Username:</b>"))
        self.inp_user = QLineEdit("vanish")
        c_layout.addWidget(self.inp_user)

        c_layout.addWidget(QLabel("<b>User Password (Optional):</b>"))
        self.inp_pass = QLineEdit()
        self.inp_pass.setEchoMode(QLineEdit.EchoMode.Password)
        c_layout.addWidget(self.inp_pass)

        lbl_root = QLabel("Root User: Configured without password as requested.")
        lbl_root.setStyleSheet("color: #34d399; font-size: 12px;")
        c_layout.addWidget(lbl_root)

        layout.addWidget(card)
        layout.addStretch()
        return page

    # --- Page 6: Live Installation ---
    def create_page_install(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(14)

        title = QLabel("Installing Vanish-OS")
        title.setObjectName("section_title")
        self.lbl_install_status = QLabel("Ready to deploy Vanish-OS with Zen kernel.")
        self.lbl_install_status.setObjectName("subtitle")
        layout.addWidget(title)
        layout.addWidget(self.lbl_install_status)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.log_view = QPlainTextEdit()
        self.log_view.setObjectName("log_view")
        self.log_view.setReadOnly(True)
        layout.addWidget(self.log_view)

        return page

    # Navigation logic
    def update_sidebar(self):
        for idx, lbl in enumerate(self.step_labels):
            if idx == self.current_page:
                lbl.setStyleSheet("color: #8b5cf6; font-weight: 800; font-size: 13px;")
            elif idx < self.current_page:
                lbl.setStyleSheet("color: #34d399; font-weight: 600; font-size: 13px;")
            else:
                lbl.setStyleSheet("color: #71717a; font-weight: 500; font-size: 13px;")

    def go_back(self):
        if self.current_page > 0 and self.current_page < 5:
            self.current_page -= 1
            self.pages.setCurrentIndex(self.current_page)
            self.btn_back.setEnabled(self.current_page > 0)
            self.btn_next.setText("Next Step →")
            self.update_sidebar()

    def go_next(self):
        if self.current_page < 4:
            self.current_page += 1
            self.pages.setCurrentIndex(self.current_page)
            self.btn_back.setEnabled(True)
            if self.current_page == 4:
                self.btn_next.setText("Deploy Vanish-OS ⚡")
                self.btn_next.setObjectName("btn_accent")
            self.update_sidebar()
        elif self.current_page == 4:
            self.current_page = 5
            self.pages.setCurrentIndex(5)
            self.btn_back.setEnabled(False)
            self.btn_next.setEnabled(False)
            self.btn_next.setText("Installing...")
            self.update_sidebar()
            self.start_installation()

    def start_installation(self):
        de_map = {0: "hyprland", 1: "kde", 2: "gnome", 3: "xfce"}
        de_choice = de_map.get(self.de_group.checkedId(), "hyprland")

        browser_map = {
            "Brave Browser": "brave-bin",
            "Firefox": "firefox",
            "Librewolf": "librewolf-bin",
            "Chromium": "chromium",
            "None": None
        }
        b_pkg = browser_map.get(self.combo_browser.currentText())

        extra_pkgs = []
        if b_pkg:
            extra_pkgs.append(b_pkg)

        if self.cb_dev.isChecked():
            extra_pkgs.extend(["vscodium-bin", "neovim", "docker", "docker-compose"])
        if self.cb_gaming.isChecked():
            extra_pkgs.extend(["steam", "lutris", "wine-staging", "gamemode", "lib32-gamemode"])

        raw_disk = self.combo_disk.currentText().split()[0]

        config = {
            "disk": raw_disk,
            "desktop": de_choice,
            "hostname": self.inp_hostname.text().strip() or "vanish-box",
            "username": self.inp_user.text().strip() or "vanish",
            "password": self.inp_pass.text(),
            "drivers": self.profile.recommended_drivers,
            "kernel_params": self.profile.kernel_params,
            "wayland_env_vars": self.profile.wayland_env_vars,
            "has_nvidia": self.profile.has_nvidia,
            "extra_packages": extra_pkgs
        }

        self.worker = WorkerThread(config)
        self.worker.log_signal.connect(self.log_view.appendPlainText)
        self.worker.progress_signal.connect(self.progress_bar.setValue)
        self.worker.done_signal.connect(self.on_install_done)
        self.worker.start()

    def on_install_done(self, success: bool):
        if success:
            self.lbl_install_status.setText("Vanish-OS installed successfully! You may now reboot.")
            self.btn_next.setText("Reboot Now")
            self.btn_next.setEnabled(True)
            self.btn_next.setObjectName("btn_primary")
            self.btn_next.clicked.disconnect()
            self.btn_next.clicked.connect(self.reboot_system)
        else:
            self.lbl_install_status.setText("Installation encountered an error. Check logs above.")
            self.btn_next.setText("Exit")
            self.btn_next.setEnabled(True)
            self.btn_next.clicked.disconnect()
            self.btn_next.clicked.connect(self.close)

    def reboot_system(self):
        if not os.environ.get("VANISH_DRY_RUN"):
            os.system("systemctl reboot")
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = VanishInstallerWindow()
    win.show()
    sys.exit(app.exec())
