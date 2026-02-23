#!/bin/bash

# Erstelle App-Bundle-Struktur
APP_NAME="macOS Lock"
APP_DIR="$APP_NAME.app"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

# Entferne alte App falls vorhanden
rm -rf "$APP_DIR"

# Erstelle Verzeichnisstruktur
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# Erstelle Info.plist
cat > "$CONTENTS_DIR/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>macOS Lock</string>
    <key>CFBundleIdentifier</key>
    <string>com.pepperonas.macoslock</string>
    <key>CFBundleName</key>
    <string>macOS Lock</string>
    <key>CFBundleDisplayName</key>
    <string>macOS Lock</string>
    <key>CFBundleVersion</key>
    <string>1.1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>CFBundleIconFile</key>
    <string>macos-lock.png</string>
</dict>
</plist>
EOF

# Kopiere Python-Scripts und Icon
cp macos-lock-gui.py "$RESOURCES_DIR/"
cp macos-lock.py "$RESOURCES_DIR/"
cp macos-lock.png "$RESOURCES_DIR/"

# Erstelle Launcher-Script
cat > "$MACOS_DIR/macOS Lock" << 'LAUNCHER'
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RESOURCES_DIR="$DIR/../Resources"
cd "$RESOURCES_DIR"

# Suche Python mit PyQt6 und Quartz
PYTHON=""

for CANDIDATE in \
    "/Users/martin/PycharmProjects/SNDBX/.venv/bin/python3" \
    "/opt/homebrew/bin/python3" \
    "/usr/local/bin/python3" \
    "/usr/bin/python3"; do
    if [ -f "$CANDIDATE" ]; then
        if "$CANDIDATE" -c "import Quartz; import PyQt6" 2>/dev/null; then
            PYTHON="$CANDIDATE"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    osascript -e 'display alert "Abhaengigkeiten fehlen" message "Bitte installiere:\npip3 install PyQt6 pyobjc-framework-Quartz" buttons {"OK"} default button "OK"'
    exit 1
fi

exec "$PYTHON" macos-lock-gui.py
LAUNCHER

# Mache Launcher ausfuehrbar
chmod +x "$MACOS_DIR/macOS Lock"

echo "App '$APP_DIR' wurde erstellt!"
echo "Starte mit: open '$APP_DIR'"
