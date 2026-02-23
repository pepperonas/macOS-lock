# macOS Lock

[![Tests](https://github.com/pepperonas/macOS-lock/actions/workflows/tests.yml/badge.svg)](https://github.com/pepperonas/macOS-lock/actions/workflows/tests.yml)
[![Build](https://github.com/pepperonas/macOS-lock/actions/workflows/build-and-release.yml/badge.svg)](https://github.com/pepperonas/macOS-lock/actions/workflows/build-and-release.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-41CD52.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://www.apple.com/macos/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A security utility for macOS that temporarily locks all keyboard and mouse input to prevent unauthorized access or accidental input. Built with PyQt6 and a modern dark UI.

![macOS Lock Screenshot](screenshot.png)

---

## Features

| Feature | Description |
|---|---|
| **Input Locking** | Blocks all keyboard, mouse, trackpad, and scroll events system-wide |
| **Configurable Unlock Shortcut** | Define your own key combination to unlock (default: `X + C`) |
| **Silent Unlock** | Unlocking via keyboard shortcut keeps the app minimized in the dock — no window popup |
| **Settings Dialog** | Change the unlock shortcut directly within the app UI |
| **Dark Theme UI** | Modern frameless window with rounded corners, macOS-style traffic light controls, and green accent colors |
| **GUI & CLI** | Full graphical interface or minimal command-line mode |
| **Lightweight** | No background services, no daemons — uses macOS native Quartz Event Services directly |
| **Drag-to-Move** | Frameless window can be repositioned by dragging the title bar area |

---

## Installation

### Option 1: Download Pre-built App

Download the latest `.app` bundle from the [Releases page](https://github.com/pepperonas/macOS-lock/releases).

1. Download `macOS-Lock.app.tar.gz`
2. Extract: `tar -xzf macOS-Lock.app.tar.gz`
3. Move `macOS Lock.app` to `/Applications/`
4. Right-click the app and select **Open** the first time (bypasses Gatekeeper)
5. Grant **Accessibility** permissions when prompted

### Option 2: Build from Source

**Prerequisites:**
- macOS 10.14 (Mojave) or later
- Python 3.10+
- Accessibility permissions for Terminal or your Python interpreter

```bash
# Clone the repository
git clone https://github.com/pepperonas/macOS-lock.git
cd macOS-lock

# Install dependencies
pip3 install PyQt6 pyobjc-core pyobjc-framework-Cocoa pyobjc-framework-Quartz
```

**Grant Accessibility permissions:**

> System Settings > Privacy & Security > Privacy > Accessibility

Add your Terminal app (Terminal.app, iTerm2, etc.) or Python interpreter and enable the toggle.

### Option 3: Build as .app Bundle

```bash
./create_app.sh
```

This creates a `macOS Lock.app` bundle in the project directory. The launcher script automatically detects a Python installation with the required dependencies.

---

## Usage

### GUI Version (Recommended)

```bash
python3 macos-lock-gui.py
```

**Workflow:**

1. The app window appears with the dark-themed interface
2. Click **SPERREN** to lock all input — the window minimizes to the dock
3. Press your configured unlock shortcut (default: `X + C` simultaneously) to unlock
4. The app stays minimized in the dock after unlocking — **no window popup** interrupts your workflow
5. Click the dock icon to bring the window back when needed

**Settings:**

Click **"Tastenkombination aendern"** at the bottom of the window to open the shortcut configuration dialog:

1. Click the capture area in the dialog
2. Press 2 or more keys simultaneously (e.g., `A + S + D`)
3. Click **Speichern** — the new shortcut is active immediately and persists across restarts

### CLI Version

```bash
python3 macos-lock.py
```

Locks all input immediately on launch. Press the configured unlock shortcut to unlock and exit. The CLI version reads the same config file as the GUI.

---

## Configuration

The unlock shortcut is stored in `~/.macos-lock-config.json`:

```json
{
  "unlock_keys": ["x", "c"]
}
```

You can change it via:
- The **GUI settings dialog** (recommended)
- Editing the JSON file directly

### Supported Keys

| Category | Keys |
|---|---|
| Letters | `a` `b` `c` `d` `e` `f` `g` `h` `i` `j` `k` `l` `m` `n` `o` `p` `q` `r` `s` `t` `u` `v` `w` `x` `y` `z` |
| Digits | `0` `1` `2` `3` `4` `5` `6` `7` `8` `9` |
| Special | `space` `return` `tab` `escape` `delete` |
| Symbols | `` ` `` `-` `=` `[` `]` `\` `;` `'` `,` `.` `/` |

At least **2 keys** must be configured. All keys must be pressed **simultaneously** to unlock.

---

## How It Works

macOS Lock uses the [Quartz Event Services](https://developer.apple.com/documentation/coregraphics/quartz_event_services) API to intercept input events at the system level:

1. **Event Tap Creation** — An event tap is inserted at `kCGSessionEventTap` with `kCGHeadInsertEventTap` priority, intercepting events before any application receives them
2. **Event Filtering** — The callback receives all keyboard, mouse, trackpad, scroll, and tablet events. While locked, all events return `None` (blocked) except the unlock key monitoring
3. **Unlock Detection** — The pressed key set is tracked. When all configured unlock keycodes are pressed simultaneously, the tap is disabled and input is restored
4. **Thread Safety** — The Quartz event loop runs in a dedicated daemon thread. Unlock signals are emitted via Qt's `pyqtSignal` mechanism for thread-safe GUI updates

### Events Intercepted

- Keyboard: `KeyDown`, `KeyUp`
- Mouse: `LeftMouseDown/Up`, `RightMouseDown/Up`, `OtherMouseDown/Up`, `MouseMoved`
- Drag: `LeftMouseDragged`, `RightMouseDragged`
- Scroll: `ScrollWheel`

### Silent Unlock Behavior

When unlocking via the keyboard shortcut, the GUI state is reset via `_on_silent_unlock()` which only updates the internal widget states. The window is **not** brought to the foreground — no `showNormal()`, no `raise_()`, no `activateWindow()`. The app remains in the dock until the user explicitly clicks it.

---

## UI Design

The interface uses a dark theme inspired by [stupidisco](https://github.com/pepperonas/stupidisco):

| Element | Style |
|---|---|
| Background | `#18181c` with `#333338` border, 12px rounded corners |
| Text | Primary `#e0e0e0`, secondary `#8a8a8e`, headings `#ffffff` |
| Lock Button | Green `#34c759` with hover `#30d158` |
| Unlock Button | Red `rgba(255, 59, 48, 180)` |
| Window Controls | Close `#ff5f57`, Minimize `#febc2e` (macOS traffic light style) |
| Settings Button | Subtle `rgba(255, 255, 255, 10)` with `#8a8a8e` text |
| Shortcut Info | `rgba(255, 255, 255, 8)` pill with 6px border-radius |

The window is frameless (`FramelessWindowHint`) with translucent background and custom-painted rounded rectangle. Drag-to-move is implemented via `mousePressEvent`/`mouseMoveEvent`.

---

## Project Structure

```
macOS-lock/
├── macos-lock-gui.py       # Main GUI application (PyQt6 + Quartz)
├── macos-lock.py            # CLI version (Quartz only)
├── create_app.sh            # Builds macOS .app bundle
├── setup.py                 # py2app build configuration
├── screenshot.png           # App screenshot for README
├── macos-lock.png           # App icon
├── tests/
│   ├── conftest.py          # Test setup (mocks Quartz/PyQt6 for CI)
│   ├── test_config.py       # Config, keycode mapping, and locker state tests
│   └── __init__.py
└── .github/
    └── workflows/
        ├── tests.yml              # CI: pytest on Python 3.10/3.11/3.12
        └── build-and-release.yml  # CD: build .app on tag push
```

---

## Running Tests

```bash
pip3 install pytest
python3 -m pytest tests/ -v
```

The test suite covers:
- **Keycode mapping** — Verifies all key-to-keycode translations and reverse lookups
- **Config persistence** — Load/save roundtrips, default fallbacks, corrupted file recovery
- **InputLocker state** — Unlock keycode management, initial state, dynamic reconfiguration

Tests mock `Quartz` and `PyQt6` so they run on any platform and in CI without a display server.

---

## Troubleshooting

### "Event Tap could not be created"

This means accessibility permissions are not granted.

1. Open **System Settings** > **Privacy & Security** > **Privacy** > **Accessibility**
2. Add your Terminal app or the `macOS Lock.app`
3. Enable the toggle
4. **Restart** the app (permissions are checked at event tap creation time)

### App doesn't respond / system is stuck

If you forget the unlock shortcut or something goes wrong:

- **SSH** into the machine and run: `pkill -f macos-lock`
- Open **Activity Monitor** from Spotlight (Cmd+Space, type "Activity Monitor") and force-quit the Python process
- As a last resort, hold the **power button** to force restart

### Window doesn't appear after unlock

This is intentional — **silent unlock** keeps the app minimized. Click the app icon in the dock to bring the window back.

### Shortcut doesn't work

- Ensure you're pressing all configured keys **simultaneously** (not sequentially)
- Check your config: `cat ~/.macos-lock-config.json`
- Reset to default: `echo '{"unlock_keys": ["x", "c"]}' > ~/.macos-lock-config.json`

---

## Dependencies

| Package | Purpose |
|---|---|
| [PyQt6](https://pypi.org/project/PyQt6/) | GUI framework (widgets, signals, painting) |
| [pyobjc-framework-Quartz](https://pypi.org/project/pyobjc-framework-Quartz/) | macOS Quartz Event Services for input interception |
| [pyobjc-core](https://pypi.org/project/pyobjc-core/) | Core Python-ObjC bridge |
| [pyobjc-framework-Cocoa](https://pypi.org/project/pyobjc-framework-Cocoa/) | macOS Cocoa framework bindings |

---

## License

MIT License — see [LICENSE](LICENSE) for details.

## Author

Created by [pepperonas](https://github.com/pepperonas)
