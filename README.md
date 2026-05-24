<!--
  DATracker — Discord Activity Tracker
  Большой README для GitHub
-->

<div align="center">
  <img src="https://i.pinimg.com/736x/4d/59/00/4d5900af12101d5b283621a85db5bd75.jpg" width="120" height="120" style="border-radius: 24px;">
  <h1>🎯 DATracker</h1>
  <h3>Discord Activity Tracker — твой статус. Автоматически.</h3>
  <p>Кроссплатформенное приложение, которое показывает в Discord, чем ты занят на компьютере: игры, код, музыка, сайты и даже системная нагрузка.</p>
  
  <p>
    <a href="#-установка"><img src="https://img.shields.io/badge/Windows-10%2F11-0078D4?style=for-the-badge&logo=windows&logoColor=white"></a>
    <a href="#-установка"><img src="https://img.shields.io/badge/macOS-12%2B-000000?style=for-the-badge&logo=apple&logoColor=white"></a>
    <a href="#-установка"><img src="https://img.shields.io/badge/Linux-X11%2FWayland-FCC624?style=for-the-badge&logo=linux&logoColor=black"></a>
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

## 📋 Оглавление

- [📖 О проекте](#-о-проекте)
- [✨ Возможности](#-возможности)
- [🖼️ Скриншоты](#️-скриншоты)
- [⚙️ Установка](#️-установка)
  - [Windows](#windows)
  - [macOS](#macos)
  - [Linux](#linux)
- [🚀 Настройка](#-настройка)
- [🔧 Сборка из исходников](#-сборка-из-исходников)
- [🛡️ Конфиденциальность](#️-конфиденциальность)
- [🤝 Вклад в проект](#-вклад-в-проект)
- [📄 Лицензия](#-лицензия)
- [💬 Контакты](#-контакты)

---

## 📖 О проекте

**DATracker** (Discord Activity Tracker) — это легковесное приложение, которое бесшумно работает в фоновом режиме и автоматически обновляет твой **Rich Presence** в Discord. Никаких ручных переключений — просто делай свои дела, а DATracker сам расскажет друзьям, чем ты занят.

Проект полностью **открытый** (MIT лицензия), не собирает и не отправляет твои данные, а все настройки хранятся локально.

---

## ✨ Возможности

| Категория | Что умеет |
|-----------|------------|
| 🎮 **Игры** | Steam, Epic Games, Battle.net, Minecraft, Valorant, League of Legends, Roblox и сотни других (автоопределение по процессу) |
| 💻 **Редакторы кода** | VS Code, IntelliJ IDEA, PyCharm, Sublime Text, Vim, Neovim — показывает проект, активный файл и язык |
| 🎵 **Музыка** | Spotify, YouTube Music, Apple Music (через расширение), локальные плееры (AIMP, Foobar2000, MusicBee) |
| 🌐 **Браузер** | Chrome, Firefox, Edge, Brave — опциональное отображение текущего сайта и заголовка вкладки |
| 📊 **Система** | Мониторинг CPU, RAM, GPU, FPS (через游戏), температура (опционально) |
| 🎨 **Кастомные статусы** | Можно вручную задать статус или комбинировать с автоопределением |
| 🔒 **Приватность** | Полный контроль над каждой категорией. Можно отключить любое отслеживание. |

---

## 🖼️ Скриншоты

<div align="center">
  <table>
    <tr>
      <td align="center"><b>Статус VS Code</b><br><img src="https://i.pinimg.com/736x/72/31/6c/72316c2c42f1bd7fae53246e871d7de6.jpg" width="200"></td>
      <td align="center"><b>Игра Cyberpunk 2077</b><br><img src="https://i.pinimg.com/1200x/d7/a6/15/d7a61596eeb0e3e00ea5ef077592ff37.jpg" width="200"></td>
      <td align="center"><b>Музыка Spotify</b><br><img src="https://i.pinimg.com/736x/59/59/8a/59598a97635ea0abc50365b99434a883.jpg" width="200"></td>
    </tr>
    <tr>
      <td align="center"><b>Системная нагрузка</b><br><img src="https://i.pinimg.com/736x/d1/f5/df/d1f5dfe71d4f0eb78ed16b5d9f0240d9.jpg" width="200"></td>
      <td align="center"><b>Браузерная активность</b><br><img src="https://i.pinimg.com/736x/af/68/d4/af68d40f6983c0e3a15a935fec786ccb.jpg" width="200"></td>
      <td align="center"><b>Главное окно настроек</b><br><img src="https://via.placeholder.com/200x120?text=Настройки+GUI" width="200"></td>
    </tr>
  </table>
</div>

---

## ⚙️ Установка

### Windows
1. Скачай последний установщик `DATracker-Setup-x64.exe` из [раздела релизов](https://github.com/yourusername/DATracker/releases).
2. Запусти установку (может потребоваться разрешение администратора).
3. После установки DATracker запустится автоматически и появится в трее (системный лоток).
4. Перейди в Discord → Настройки → Активность — убедись, что DATracker отображается.

### macOS
1. Скачай `DATracker.dmg`.
2. Перетащи приложение в папку `Программы`.
3. Запусти DATracker (при первом запуске разреши доступ к специальным возможностям, если нужно отслеживать активные окна).
4. Приложение появится в строке меню (иконка вверху).

### Linux
**Поддерживаемые форматы:** `.deb`, `.AppImage`, `.rpm`

```bash
# Ubuntu / Debian
sudo dpkg -i datracker_1.2.0_amd64.deb

# Arch Linux (AUR)
yay -S datracker-bin

# AppImage (для любых дистрибутивов)
chmod +x DATracker-1.2.0.AppImage
./DATracker-1.2.0.AppImage
