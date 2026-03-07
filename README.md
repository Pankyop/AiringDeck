# AiringDeck

Native desktop app to track anime airing schedules with AniList integration.

<p align="center">
  <img src="resources/icons/app.png" alt="AiringDeck Icon" width="192" height="192" />
</p>

![Release](https://img.shields.io/github/v/release/Pankyop/AiringDeck?display_name=tag&style=flat)
![Downloads](https://img.shields.io/github/downloads/Pankyop/AiringDeck/latest/total?style=flat&label=downloads)
![License](https://img.shields.io/badge/license-GPLv3%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows-0078D6)

## 🚀 Features

- ✅ Qt 6.7 native application
- ✅ AniList OAuth authentication
- ✅ Calendar view of airing episodes
- ✅ Episode tracking and notifications
- ✅ Modern QML UI
- ✅ Low memory footprint (~50MB)
- ✅ Windows native .exe
- ✅ No-Tracker mode (privacy-first defaults)

## 🛠️ Tech Stack

- **UI Framework**: Qt 6.7 (PySide6)
- **UI Language**: QML (declarative)
- **Backend**: Python 3.11+
- **Native Acceleration**: CPython C extension (`core._airingdeck_native`)
- **API**: AniList GraphQL
- **Packaging**: PyInstaller
- **Secure Storage**: keyring

## 📦 Development Setup

### Prerequisites
- Python 3.11 or higher
- pip

### Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run Development

```bash
python src/main.py
```

### Update Notifications

The app checks for updates automatically at startup.
When a newer version is available, it shows a notice with:

- user-facing release notes,
- an `Update now` button (downloads and starts the Windows installer directly),
- an arrow button to dismiss the notice.

Optional environment configuration:

```bash
AIRINGDECK_UPDATE_REPOSITORY=Pankyop/AiringDeck
AIRINGDECK_UPDATE_FEED_URL=https://api.github.com/repos/Pankyop/AiringDeck/releases/latest
AIRINGDECK_UPDATE_TAGS_URL=https://api.github.com/repos/Pankyop/AiringDeck/tags
AIRINGDECK_UPDATE_DOWNLOAD_URL=https://github.com/Pankyop/AiringDeck/releases
```

AniList client safety configuration (defaults shown):

```bash
# Disable local persistence of AniList payloads (default: strict mode ON)
AIRINGDECK_ANILIST_CACHE_ENABLED=0

# Conservative pacing to stay below temporary AniList limits
AIRINGDECK_ANILIST_MIN_INTERVAL_SEC=2.1

# Request timeout in seconds
AIRINGDECK_ANILIST_TIMEOUT_SEC=10

# Optional explicit API user-agent
AIRINGDECK_USER_AGENT=AiringDeck/3.5.2 (+https://github.com/Pankyop/AiringDeck)
```

### Build .exe

```bash
python scripts/build_windows.py
```

Output: `dist/AiringDeck.exe`

Build optimized for modern CPUs (default `avx2`, suitable for Intel 10th gen+ and AMD Zen2+/Ryzen 4000+):

```bash
python scripts/build_windows.py --cpu-profile avx2
```

Optional AVX-512 profile (only on machines that support AVX-512):

```bash
python scripts/build_windows.py --cpu-profile avx512
```

Note: the build script also tries to compile the native C extension (`setup.py build_ext --inplace`) before packaging.
If no C/C++ compiler is available, it falls back to pure Python.
To require native compilation:

```bash
python scripts/build_windows.py --cpu-profile avx2 --require-native
```

### Build installer Windows (.exe setup)

Prerequisite: install Inno Setup 6 (`ISCC.exe`).

Full command (build app + installer):

```bash
python scripts/build_windows_installer.py
```

If `dist/AiringDeck.exe` already exists:

```bash
python scripts/build_windows_installer.py --skip-build-exe
```

Output:
- `dist/AiringDeck-Setup-<version>.exe`

Installer behavior:
- installer language selection (EN/IT, default EN),
- dedicated app-language page (EN/IT, default EN),
- app language saved to `HKCU\Software\AiringDeck\AiringDeck\app_language`.

## AniList API Compliance

- AiringDeck is an unofficial client and uses AniList OAuth + GraphQL APIs under AniList terms.
- The app uses user-granted OAuth tokens only (no AniList credential scraping).
- The app reads only data needed for schedule/list features (no bulk dataset extraction).
- Rate-limit handling and conservative request pacing are enabled in code.
- Local AniList payload cache is disabled by default (`AIRINGDECK_ANILIST_CACHE_ENABLED=0`).
- If you plan public/commercial distribution, request written confirmation from AniList for your use case.

## No-Tracker Mode

AiringDeck is designed as a local desktop viewer, not a cloud tracking platform.

- no AiringDeck-owned backend storing user anime history,
- no hidden telemetry by default,
- no long-term AniList payload persistence by default,
- first-run privacy dialog to configure notifications, update checks, and diagnostics.

Reference docs:
- `docs/product_scope_no_tracker.md`
- `docs/privacy_data_policy.md`

## ⚡ Native Optimization

- Text filtering on anime entries uses a C module (`src/core/_airingdeck_native.c`) to reduce Python-loop overhead.
- If the native module is unavailable, the app automatically falls back to pure Python (`src/core/native_accel.py`).
- Integration is transparent: no QML/UI behavior changes.

## 📁 Project Structure

```
airingdeck/
├── src/
│   ├── main.py                 # Entry point
│   ├── core/
│   │   ├── app_controller.py   # Main controller
│   │   ├── anime_model.py      # Qt list model
│   │   └── worker.py           # Async worker wrapper
│   ├── services/
│   │   ├── anilist_service.py  # AniList API
│   │   └── auth_service.py     # OAuth
│   └── ui/
│       └── qml/                # QML UI files
│           ├── BootShell.qml
│           └── components/
├── resources/
│   ├── icons/
│   └── fonts/
├── scripts/
│   └── build_windows.py        # Build script
├── requirements.txt
└── README.md
```

## 🎨 UI Architecture

- **QML**: Declarative UI (similar to React)
- **Python Backend**: Business logic & API calls
- **Qt Signals/Slots**: Communication between QML ↔ Python
- **Property Bindings**: Reactive data binding

## 📝 License

This project is licensed under the **GNU General Public License v3.0 or later**
(`GPL-3.0-or-later`).

See `LICENSE` for the full text.

Third-party license notes are documented in `THIRD_PARTY_LICENSES.md`.
