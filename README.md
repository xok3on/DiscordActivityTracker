<!--
  DATracker — Discord Activity Tracker
  English README for GitHub
-->

<div align="center">
  <img src="https://i.pinimg.com/736x/4d/59/00/4d5900af12101d5b283621a85db5bd75.jpg" width="120" height="120" style="border-radius: 24px;">
  <h1>🎯 DATracker</h1>
  <h3>Discord Activity Tracker — your status. Automatically.</h3>
  <p>Cross-platform desktop app that shows what you're doing on your computer in Discord: games, code, music, browsing, and even system stats.</p>
  
  <p>
    <a href="#-installation"><img src="https://img.shields.io/badge/Windows-10%2F11-0078D4?style=for-the-badge&logo=windows&logoColor=white"></a>
    <a href="#-installation"><img src="https://img.shields.io/badge/macOS-12%2B-000000?style=for-the-badge&logo=apple&logoColor=white"></a>
    <a href="#-installation"><img src="https://img.shields.io/badge/Linux-X11%2FWayland-FCC624?style=for-the-badge&logo=linux&logoColor=black"></a>
  </p>
  
  <p>
    <a href="https://github.com/yourusername/DATracker/releases"><img src="https://img.shields.io/github/v/release/yourusername/DATracker?style=flat-square&logo=github&color=5865F2"></a>
    <a href="https://github.com/yourusername/DATracker/blob/main/LICENSE"><img src="https://img.shields.io/github/license/yourusername/DATracker?style=flat-square"></a>
    <a href="https://github.com/yourusername/DATracker/stargazers"><img src="https://img.shields.io/github/stars/yourusername/DATracker?style=flat-square&logo=github"></a>
    <a href="https://github.com/yourusername/DATracker/forks"><img src="https://img.shields.io/github/forks/yourusername/DATracker?style=flat-square&logo=github"></a>
    <a href="https://discord.gg/invite"><img src="https://img.shields.io/discord/123456789?style=flat-square&logo=discord&logoColor=white&color=5865F2"></a>
  </p>
</div>

---

## 📋 Table of Contents

- [📖 About](#-about)
- [✨ Features](#-features)
- [🖼️ Screenshots](#️-screenshots)
- [⚙️ Installation](#️-installation)
  - [Windows](#windows)
  - [macOS](#macos)
  - [Linux](#linux)
- [🚀 Configuration](#-configuration)
- [🔧 Building from Source](#-building-from-source)
- [🛡️ Privacy](#️-privacy)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [💬 Contact](#-contact)

---

## 📖 About

**DATracker** (Discord Activity Tracker) is a lightweight background app that automatically updates your **Rich Presence** in Discord. No manual switching — just go about your business, and DATracker will let your friends know what you're up to.

This project is **fully open source** (MIT license), does not collect or send your data anywhere, and stores all settings locally.

---

## ✨ Features

| Category | What it tracks |
|----------|----------------|
| 🎮 **Games** | Steam, Epic Games, Battle.net, Minecraft, Valorant, League of Legends, Roblox, and hundreds more (auto-detection by process) |
| 💻 **Code Editors** | VS Code, IntelliJ IDEA, PyCharm, Sublime Text, Vim, Neovim — shows project, active file, and language |
| 🎵 **Music** | Spotify, YouTube Music, Apple Music (via extension), local players (AIMP, Foobar2000, MusicBee) |
| 🌐 **Browser** | Chrome, Firefox, Edge, Brave — optional display of current website and tab title |
| 📊 **System** | CPU, RAM, GPU, FPS (via game detection), temperature (optional) |
| 🎨 **Custom Statuses** | Manual override or combine with auto-detection |
| 🔒 **Privacy** | Full control over every category. Disable any tracking at any time. |

---

## 🖼️ Screenshots

<div align="center">
  <table>
    <tr>
      <td align="center"><b>VS Code Status</b><br><img src="https://i.pinimg.com/736x/72/31/6c/72316c2c42f1bd7fae53246e871d7de6.jpg" width="200"></td>
      <td align="center"><b>Cyberpunk 2077 Game</b><br><img src="https://i.pinimg.com/1200x/d7/a6/15/d7a61596eeb0e3e00ea5ef077592ff37.jpg" width="200"></td>
      <td align="center"><b>Spotify Music</b><br><img src="https://i.pinimg.com/736x/59/59/8a/59598a97635ea0abc50365b99434a883.jpg" width="200"></td>
    </tr>
    <tr>
      <td align="center"><b>System Load</b><br><img src="https://i.pinimg.com/736x/d1/f5/df/d1f5dfe71d4f0eb78ed16b5d9f0240d9.jpg" width="200"></td>
      <td align="center"><b>Browser Activity</b><br><img src="https://i.pinimg.com/736x/af/68/d4/af68d40f6983c0e3a15a935fec786ccb.jpg" width="200"></td>
      <td align="center"><b>Settings Window</b><br><img src="https://via.placeholder.com/200x120?text=Settings+GUI" width="200"></td>
    </tr>
  </table>
</div>

---

## ⚙️ Installation

### Windows
1. Download the latest `DATracker-Setup-x64.exe` from the [Releases page](https://github.com/yourusername/DATracker/releases).
2. Run the installer (administrator rights may be required).
3. After installation, DATracker will start automatically and appear in the system tray.
4. Go to Discord → Settings → Activity — make sure DATracker is displayed.

### macOS
1. Download `DATracker.dmg`.
2. Drag the app into the `Applications` folder.
3. Launch DATracker (on first launch, grant accessibility permissions if window tracking is needed).
4. The app will appear in the menu bar (icon at the top).

### Linux
**Supported formats:** `.deb`, `.AppImage`, `.rpm`

```bash
# Ubuntu / Debian
sudo dpkg -i datracker_1.2.0_amd64.deb

# Arch Linux (AUR)
yay -S datracker-bin

# AppImage (for any distribution)
chmod +x DATracker-1.2.0.AppImage
./DATracker-1.2.0.AppImage
Important for Linux: Wayland support may require xdg-desktop-portal. X11 works without additional steps.

🚀 Configuration
After first launch, open the main window (click the tray/menu bar icon). Here are the main settings tabs:

1. General
Launch on system startup

Hide window on startup

Interface language (English/Russian)

2. Activity
Enable/disable categories:

Games

Code Editors

Music

Browser

System Load

3. Details
VS Code: show project name / file / line

Browser: whitelist specific sites (e.g., youtube.com, github.com)

System: update interval (seconds)

4. Discord
App ID (default is standard)

Update status only on activity change

🔧 All settings are stored in ~/.config/datracker/config.json (Linux/macOS) or %APPDATA%\DATracker\config.json (Windows).

🔧 Building from Source
Requirements:

Node.js 18+

npm or yarn

Git

bash
# Clone the repository
git clone https://github.com/yourusername/DATracker.git
cd DATracker

# Install dependencies
npm install

# Build production version
npm run build

# Run in development mode
npm run dev
Project structure:

text
DATracker/
├── src/
│   ├── main/         # Electron main process
│   ├── renderer/     # UI (React/Vue/plain html)
│   ├── detectors/    # Activity detectors (games, code, music)
│   └── discord/      # Rich Presence updater
├── assets/           # Icons, screenshots
└── build/            # Installer build scripts
🛡️ Privacy
DATracker does NOT:

❌ Collect or send your data anywhere.

❌ Include telemetry or analytics.

❌ Track keystrokes, passwords, or screen content.

❌ Require an internet connection to work (other than Discord itself).

What DATracker does — reads window titles and processes (locally) and updates your profile via Discord RPC.
You can verify everything — the source code is fully open.

🤝 Contributing
We welcome all contributions: bug reports, pull requests, feature ideas.

How to help:
Fork the repository.

Create a feature branch (git checkout -b feature/amazing-feature).

Commit your changes (git commit -m 'Add amazing feature').

Push to the branch (git push origin feature/amazing-feature).

Open a Pull Request.

Bug reports
Please use Issues and include:

OS version

Logs (located at ~/.datracker/logs/)

Steps to reproduce

📄 License
Distributed under the MIT License.
Copy, modify, use in commercial projects — just retain the copyright notice.

text
MIT License

Copyright (c) 2026 DATracker Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
...
💬 Contact
Discord server: https://discord.gg/datracker

Telegram: @datracker_news

Email: support@datracker.app

Twitter: @DATrackerApp

<div align="center"> <sub>⭐ Star this repo if you find it useful — it helps development!<br>Made with ❤️ for the Discord community</sub> </div> ```
