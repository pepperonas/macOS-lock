# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run Commands

```bash
# Run GUI app
python3 macos-lock-gui.py

# Run CLI version
python3 macos-lock.py

# Run tests
python3 -m pytest tests/ -v

# Run a single test
python3 -m pytest tests/test_config.py::TestConfig::test_save_and_load_roundtrip -v

# Build .app bundle
./create_app.sh

# Launch built app
open "macOS Lock.app"

# Install dependencies
pip3 install PyQt6 pyobjc-core pyobjc-framework-Cocoa pyobjc-framework-Quartz
pip3 install pytest  # for tests only
```

## Architecture

**Single-file GUI app** (`macos-lock-gui.py`) with three main classes in one file:

- **`InputLocker`** — Quartz Event Tap that intercepts all keyboard/mouse/trackpad events. Runs the CFRunLoop in a daemon thread. Emits `pyqtSignal` on unlock for thread-safe GUI updates. Does NOT subclass QObject — uses a separate `UnlockSignal` bridge object.
- **`LockWindow(QMainWindow)`** — Frameless PyQt6 window with custom `paintEvent` for rounded corners and translucent background. Implements drag-to-move via mouse events. Key behavior: `_on_silent_unlock()` resets UI state without bringing window to foreground (no `showNormal`/`raise_`/`activateWindow`).
- **`SettingsDialog(QDialog)`** — Key capture dialog. Uses `keyPressEvent`/`keyReleaseEvent` to record simultaneous key presses. Maps Qt keysyms to macOS keycodes via `KEYCODE_MAP`.

**CLI version** (`macos-lock.py`) — standalone Quartz-only locker, no GUI dependencies. Shares the same config file and keycode map but is a separate implementation.

**Shared config** at `~/.macos-lock-config.json` — both GUI and CLI read/write the same file. Key names (strings) map to macOS keycodes via `KEYCODE_MAP` dict.

## Key Design Decisions

- **Dark theme** uses QSS stylesheets defined as `STYLESHEET` and `DIALOG_STYLE` string constants (inspired by the stupidisco project). Colors: bg `#18181c`, accent green `#34c759`, alert red `#ff3b30`.
- **Filenames have hyphens** (`macos-lock-gui.py`), so tests use `importlib.util.spec_from_file_location` in `conftest.py` to import them as `macos_lock_gui` / `macos_lock_cli`.
- **Tests mock both Quartz and PyQt6** in `conftest.py` so they run in CI without macOS frameworks or a display server. When testing `InputLocker`, use `__new__` to skip the constructor (which creates `UnlockSignal`, a QObject requiring the mocked PyQt6).
- **`.app` bundle** is a shell wrapper (`create_app.sh`) that searches for a Python with both PyQt6 and Quartz installed, not a py2app/pyinstaller build.

## CI

- **Tests** run on push/PR to main across Python 3.10/3.11/3.12 on `macos-latest`
- **Release** triggers on `v*` tags, builds `.app` bundle and creates GitHub release
