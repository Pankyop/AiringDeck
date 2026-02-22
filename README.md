# AiringDeck

Native desktop app to track anime airing schedules with AniList integration.

![Release](https://img.shields.io/github/v/release/Pankyop/AiringDeck?display_name=tag)
![License](https://img.shields.io/badge/license-MIT-blue)
![Platform](https://img.shields.io/badge/platform-Windows-0078D6)

## 🚀 Features

- ✅ Qt 6.7 native application
- ✅ AniList OAuth authentication
- ✅ Calendar view of airing episodes
- ✅ Episode tracking and notifications
- ✅ Modern QML UI
- ✅ Low memory footprint (~50MB)
- ✅ Windows native .exe

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
- an `Update now` button (opens the release page),
- an arrow button to dismiss the notice.

Optional environment configuration:

```bash
AIRINGDECK_UPDATE_REPOSITORY=Pankyop/AiringDeck
AIRINGDECK_UPDATE_FEED_URL=https://api.github.com/repos/Pankyop/AiringDeck/releases/latest
AIRINGDECK_UPDATE_TAGS_URL=https://api.github.com/repos/Pankyop/AiringDeck/tags
AIRINGDECK_UPDATE_DOWNLOAD_URL=https://github.com/Pankyop/AiringDeck/releases
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

### Automated Release Post on X

Release posting is automated with GitHub Actions:
- workflow: `.github/workflows/x_release.yml`
- script: `scripts/post_to_x.py`
- source notes: `CHANGELOG.md` (section matching the released tag)

To test locally without posting:

```bash
python scripts/post_to_x.py --tag v3.3.0 --dry-run
```

GitHub repository secrets required for real posting:
- `X_POST_ENABLED=true`
- `X_API_KEY`
- `X_API_SECRET`
- `X_ACCESS_TOKEN`
- `X_ACCESS_TOKEN_SECRET`

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

MIT
