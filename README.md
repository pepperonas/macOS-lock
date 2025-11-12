# macOS Lock

A security utility for macOS that temporarily locks keyboard and mouse input to prevent unauthorized access or accidental input.

![macOS Lock Screenshot](Screenshot.png)

## Features

- 🔒 **Input Locking**: Blocks all keyboard and mouse input when activated
- 🎯 **Quick Unlock**: Press `X + C` keys simultaneously to unlock
- 🖥️ **GUI Interface**: User-friendly graphical interface with lock/unlock button
- 🚀 **Lightweight**: Minimal resource usage
- 🔐 **Secure**: Uses macOS native security APIs

## Installation

### Option 1: Download Pre-built App (Recommended)

Download the latest release for Apple Silicon (M1/M2/M3) from the [Releases page](https://github.com/pepperonas/macOS-lock/releases).

1. Download `macOS-Lock.app.tar.gz`
2. Extract the archive
3. Move `macOS-Lock.app` to your Applications folder
4. Right-click and select "Open" the first time to bypass Gatekeeper

### Option 2: Build from Source

#### Prerequisites

- macOS 10.14 or later
- Python 3.8+
- Accessibility permissions for Terminal/Python

#### Quick Start

1. Clone the repository:
```bash
git clone https://github.com/pepperonas/macOS-lock.git
cd macOS-lock
```

2. Install dependencies:
```bash
pip3 install pyobjc-core pyobjc-framework-Cocoa pyobjc-framework-Quartz
```

3. Grant accessibility permissions:
   - Open System Preferences → Security & Privacy → Privacy → Accessibility
   - Add Terminal or your Python interpreter
   - Enable the checkbox

## Usage

### GUI Version (Recommended)

Run the GUI application:
```bash
python3 macos-lock-gui.py
```

- Click "SPERREN" (Lock) to activate input lock
- Press `X + C` keys simultaneously to unlock
- The window minimizes when locked

### Command Line Version

For a minimal command-line version:
```bash
python3 macos-lock.py
```

- Immediately locks input on start
- Press `X + C` to unlock and exit

### Creating a macOS App

To create a standalone .app bundle:
```bash
./create_app.sh
```

The app will be created in the `dist/` folder.

## How It Works

The utility uses macOS's Quartz Event Services to intercept and block input events at the system level. When locked:

1. All keyboard and mouse events are intercepted
2. Only the unlock combination (`X + C`) is monitored
3. Other applications continue running normally
4. Upon unlock, normal input is restored

## Security Note

This tool requires accessibility permissions to function. It intercepts system events for security purposes only and does not log or transmit any data.

## Troubleshooting

### "Event Tap could not be created"
- Ensure accessibility permissions are granted
- Restart Terminal/Python after granting permissions

### App doesn't respond
- Force quit using Activity Monitor
- Or use SSH/remote access to kill the process

## License

MIT License - See LICENSE file for details

## Author

Created by pepperonas

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.