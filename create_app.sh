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
    <string>com.yourcompany.macoslock</string>
    <key>CFBundleName</key>
    <string>macOS Lock</string>
    <key>CFBundleDisplayName</key>
    <string>macOS Lock</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
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
cp macos-lock-app.py "$RESOURCES_DIR/"
cp macos-lock.py "$RESOURCES_DIR/"
cp macos-lock.png "$RESOURCES_DIR/"

# Erstelle Launcher-Script
cat > "$MACOS_DIR/macOS Lock" << 'EOF'
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RESOURCES_DIR="$DIR/../Resources"
cd "$RESOURCES_DIR"

# Verwende das Python aus dem Virtual Environment
PYTHON_VENV="/Users/martin/PycharmProjects/SNDBX/.venv/bin/python3"

# Falls venv nicht verfügbar, versuche System-Python mit PyObjC zu installieren
if [ ! -f "$PYTHON_VENV" ]; then
    # Installiere PyObjC für System-Python
    /usr/bin/pip3 install --user pyobjc-core pyobjc-framework-Quartz 2>/dev/null
    PYTHON_VENV="/usr/bin/python3"
fi

# Prüfe ob pyobjc verfügbar ist
$PYTHON_VENV -c "import Quartz" 2>/dev/null
if [ $? -ne 0 ]; then
    osascript -e 'display alert "PyObjC Installation" message "Installiere PyObjC..." buttons {"OK"}'
    /usr/bin/pip3 install --user pyobjc-core pyobjc-framework-Quartz
    PYTHON_VENV="/usr/bin/python3"
fi

# Starte die GUI-App direkt
exec $PYTHON_VENV macos-lock-app.py
EOF

# Mache Launcher ausführbar
chmod +x "$MACOS_DIR/macOS Lock"

echo "App '$APP_DIR' wurde erstellt!"
echo "Starte mit: open '$APP_DIR'"