#!/usr/bin/env python3
"""
macOS Lock GUI - Security app with PyQt6 interface (stupidisco theme).
"""

import sys
import os
import json
import threading
import subprocess

import Quartz
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QDialog,
    QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QPainter, QColor, QPainterPath, QBrush

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
CONFIG_PATH = os.path.expanduser("~/.macos-lock-config.json")

KEYCODE_MAP = {
    "a": 0, "s": 1, "d": 2, "f": 3, "h": 4, "g": 5, "z": 6, "x": 7,
    "c": 8, "v": 9, "b": 11, "q": 12, "w": 13, "e": 14, "r": 15,
    "y": 16, "t": 17, "1": 18, "2": 19, "3": 20, "4": 21, "6": 22,
    "5": 23, "=": 24, "9": 25, "7": 26, "-": 27, "8": 28, "0": 29,
    "]": 30, "o": 31, "u": 32, "[": 33, "i": 34, "p": 35, "l": 37,
    "j": 38, "'": 39, "k": 40, ";": 41, "\\": 42, ",": 43, "/": 44,
    "n": 45, "m": 46, ".": 47, "`": 50, "space": 49, "return": 36,
    "tab": 48, "escape": 53, "delete": 51,
}

REVERSE_KEYCODE_MAP = {v: k for k, v in KEYCODE_MAP.items()}

DEFAULT_CONFIG = {"unlock_keys": ["x", "c"]}


def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                saved = json.load(f)
            cfg = DEFAULT_CONFIG.copy()
            cfg.update(saved)
            return cfg
        except (json.JSONDecodeError, IOError):
            pass
    return DEFAULT_CONFIG.copy()


def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def keys_to_keycodes(keys):
    return [KEYCODE_MAP[k] for k in keys if k in KEYCODE_MAP]


# ---------------------------------------------------------------------------
# Stylesheet (stupidisco-inspired dark theme)
# ---------------------------------------------------------------------------
STYLESHEET = """
QWidget#central {
    background: transparent;
}
QLabel {
    color: #e0e0e0;
    background: transparent;
}
QLabel#title {
    font-size: 15px;
    font-weight: bold;
    color: #ffffff;
}
QLabel#status {
    font-size: 12px;
    color: #8a8a8e;
}
QLabel#icon {
    font-size: 54px;
    color: #e0e0e0;
}
QLabel#shortcut_info {
    font-size: 11px;
    color: #8a8a8e;
    padding: 4px 8px;
    background-color: rgba(255, 255, 255, 8);
    border-radius: 6px;
}
QPushButton#lock {
    background-color: #34c759;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 14px 24px;
    font-size: 16px;
    font-weight: bold;
    min-height: 48px;
}
QPushButton#lock:hover {
    background-color: #30d158;
}
QPushButton#unlock {
    background-color: rgba(255, 59, 48, 180);
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 14px 24px;
    font-size: 16px;
    font-weight: bold;
    min-height: 48px;
}
QPushButton#unlock:hover {
    background-color: rgba(255, 59, 48, 220);
}
QPushButton#settings {
    background-color: rgba(255, 255, 255, 10);
    color: #8a8a8e;
    border: 1px solid rgba(255, 255, 255, 15);
    border-radius: 6px;
    padding: 5px 12px;
    font-size: 12px;
}
QPushButton#settings:hover {
    background-color: rgba(255, 255, 255, 18);
    color: #e0e0e0;
}
QPushButton#winbtn_close {
    background-color: #ff5f57;
    border: none;
    border-radius: 7px;
    min-width: 14px; max-width: 14px;
    min-height: 14px; max-height: 14px;
}
QPushButton#winbtn_close:hover {
    background-color: #ff3b30;
}
QPushButton#winbtn_min {
    background-color: #febc2e;
    border: none;
    border-radius: 7px;
    min-width: 14px; max-width: 14px;
    min-height: 14px; max-height: 14px;
}
QPushButton#winbtn_min:hover {
    background-color: #f0a000;
}
"""

DIALOG_STYLE = """
QDialog {
    background-color: #1e1e22;
}
QLabel {
    color: #e0e0e0;
    background: transparent;
}
QLabel#heading {
    font-size: 15px;
    font-weight: bold;
    color: #ffffff;
}
QLabel#info {
    font-size: 12px;
    color: #8a8a8e;
}
QLabel#hint {
    font-size: 11px;
    color: #8a8a8e;
}
QLabel#capture_area {
    font-size: 14px;
    color: #e0e0e0;
    padding: 12px;
    background-color: rgba(255, 255, 255, 8);
    border-radius: 8px;
    border: 2px solid rgba(255, 255, 255, 20);
    min-height: 40px;
}
QLabel#capture_active {
    font-size: 14px;
    font-weight: bold;
    color: #34c759;
    padding: 12px;
    background-color: rgba(52, 199, 89, 10);
    border-radius: 8px;
    border: 2px solid rgba(52, 199, 89, 60);
    min-height: 40px;
}
QPushButton#save {
    background-color: #34c759;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: bold;
}
QPushButton#save:hover {
    background-color: #30d158;
}
QPushButton#cancel {
    background-color: rgba(255, 255, 255, 10);
    color: #8a8a8e;
    border: 1px solid rgba(255, 255, 255, 15);
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 13px;
}
QPushButton#cancel:hover {
    background-color: rgba(255, 255, 255, 18);
    color: #e0e0e0;
}
"""


# ---------------------------------------------------------------------------
# Signals bridge (thread-safe GUI updates)
# ---------------------------------------------------------------------------
class UnlockSignal(QObject):
    unlocked = pyqtSignal()


# ---------------------------------------------------------------------------
# Input Locker (Quartz Event Tap)
# ---------------------------------------------------------------------------
class InputLocker:
    def __init__(self, unlock_keycodes=None):
        self.locked = False
        self.pressed_keys = set()
        self.tap = None
        self.run_loop_source = None
        self.lock_thread = None
        self.unlock_keycodes = set(unlock_keycodes or [7, 8])
        self.signal = UnlockSignal()

    def set_unlock_keycodes(self, keycodes):
        self.unlock_keycodes = set(keycodes)

    def event_callback(self, proxy, event_type, event, refcon):
        if not self.locked:
            return event

        if event_type in [Quartz.kCGEventKeyDown, Quartz.kCGEventKeyUp]:
            keycode = Quartz.CGEventGetIntegerValueField(
                event, Quartz.kCGKeyboardEventKeycode
            )
            if event_type == Quartz.kCGEventKeyDown:
                self.pressed_keys.add(keycode)
            elif event_type == Quartz.kCGEventKeyUp:
                self.pressed_keys.discard(keycode)

            if self.unlock_keycodes.issubset(self.pressed_keys):
                self.unlock()
                return event

        return None

    def lock(self):
        self.locked = True
        self.pressed_keys.clear()

        event_mask = (
            (1 << Quartz.kCGEventKeyDown)
            | (1 << Quartz.kCGEventKeyUp)
            | (1 << Quartz.kCGEventLeftMouseDown)
            | (1 << Quartz.kCGEventLeftMouseUp)
            | (1 << Quartz.kCGEventRightMouseDown)
            | (1 << Quartz.kCGEventRightMouseUp)
            | (1 << Quartz.kCGEventMouseMoved)
            | (1 << Quartz.kCGEventLeftMouseDragged)
            | (1 << Quartz.kCGEventRightMouseDragged)
            | (1 << Quartz.kCGEventScrollWheel)
            | (1 << Quartz.kCGEventOtherMouseDown)
            | (1 << Quartz.kCGEventOtherMouseUp)
        )

        self.tap = Quartz.CGEventTapCreate(
            Quartz.kCGSessionEventTap,
            Quartz.kCGHeadInsertEventTap,
            Quartz.kCGEventTapOptionDefault,
            event_mask,
            self.event_callback,
            None,
        )
        if not self.tap:
            return False

        self.run_loop_source = Quartz.CFMachPortCreateRunLoopSource(
            Quartz.kCFAllocatorDefault, self.tap, 0
        )
        self.lock_thread = threading.Thread(target=self._run_loop)
        self.lock_thread.daemon = True
        self.lock_thread.start()
        return True

    def _run_loop(self):
        Quartz.CFRunLoopAddSource(
            Quartz.CFRunLoopGetCurrent(),
            self.run_loop_source,
            Quartz.kCFRunLoopCommonModes,
        )
        Quartz.CGEventTapEnable(self.tap, True)
        Quartz.CFRunLoopRun()

    def unlock(self):
        self.locked = False
        if self.tap:
            Quartz.CGEventTapEnable(self.tap, False)
            Quartz.CFRunLoopStop(Quartz.CFRunLoopGetCurrent())
        self.signal.unlocked.emit()


# ---------------------------------------------------------------------------
# Settings Dialog
# ---------------------------------------------------------------------------
class SettingsDialog(QDialog):
    def __init__(self, parent, current_keys, on_save):
        super().__init__(parent)
        self.on_save = on_save
        self.captured_keys = []
        self.capturing = False

        self.setWindowTitle("Settings")
        self.setFixedSize(360, 240)
        self.setStyleSheet(DIALOG_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)

        heading = QLabel("Unlock Shortcut")
        heading.setObjectName("heading")
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(heading)

        current_display = " + ".join(k.upper() for k in current_keys)
        info = QLabel(f"Current: {current_display}")
        info.setObjectName("info")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

        self.capture_label = QLabel("Click here, then press keys")
        self.capture_label.setObjectName("capture_area")
        self.capture_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.capture_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.capture_label.mousePressEvent = self._start_capture
        layout.addWidget(self.capture_label)

        hint = QLabel("Press at least 2 keys simultaneously")
        hint.setObjectName("hint")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

        layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("save")
        self.save_btn.clicked.connect(self._save)
        btn_row.addWidget(self.save_btn)

        layout.addLayout(btn_row)

    def _start_capture(self, event=None):
        self.capturing = True
        self.captured_keys = []
        self.capture_label.setText("Press keys ...")
        self.capture_label.setObjectName("capture_active")
        self.capture_label.setStyleSheet(DIALOG_STYLE)
        self.setFocus()

    def keyPressEvent(self, event):
        if not self.capturing:
            super().keyPressEvent(event)
            return

        key_name = self._qt_key_to_name(event)
        if key_name and key_name not in self.captured_keys:
            self.captured_keys.append(key_name)
            display = " + ".join(k.upper() for k in self.captured_keys)
            self.capture_label.setText(display)

    def keyReleaseEvent(self, event):
        if self.capturing and len(self.captured_keys) >= 2:
            self.capturing = False
        super().keyReleaseEvent(event)

    @staticmethod
    def _qt_key_to_name(event):
        text = event.text().lower()
        if len(text) == 1 and text in KEYCODE_MAP:
            return text
        special = {
            Qt.Key.Key_Space: "space",
            Qt.Key.Key_Return: "return",
            Qt.Key.Key_Enter: "return",
            Qt.Key.Key_Tab: "tab",
            Qt.Key.Key_Escape: "escape",
            Qt.Key.Key_Backspace: "delete",
        }
        return special.get(event.key())

    def _save(self):
        if len(self.captured_keys) >= 2:
            self.on_save(self.captured_keys)
            self.accept()
        else:
            QMessageBox.warning(
                self, "Note", "Please press at least 2 keys simultaneously."
            )


# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------
class LockWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.is_locked = False
        self._drag_pos = None

        keycodes = keys_to_keycodes(self.config["unlock_keys"])
        self.locker = InputLocker(unlock_keycodes=keycodes)
        self.locker.signal.unlocked.connect(self._on_silent_unlock)

        self._init_ui()

    # ---- UI setup ---------------------------------------------------------
    def _init_ui(self):
        self.setWindowTitle("macOS Lock")
        self.setFixedSize(320, 340)
        self.setStyleSheet(STYLESHEET)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(14, 12, 14, 14)
        root.setSpacing(0)

        # -- title bar with window controls --
        titlebar = QHBoxLayout()
        titlebar.setSpacing(6)

        btn_close = QPushButton()
        btn_close.setObjectName("winbtn_close")
        btn_close.setFixedSize(14, 14)
        btn_close.clicked.connect(self.close)

        btn_min = QPushButton()
        btn_min.setObjectName("winbtn_min")
        btn_min.setFixedSize(14, 14)
        btn_min.clicked.connect(self.showMinimized)

        titlebar.addWidget(btn_close)
        titlebar.addWidget(btn_min)
        titlebar.addSpacing(8)

        title_label = QLabel("macOS Lock")
        title_label.setObjectName("title")
        titlebar.addWidget(title_label)
        titlebar.addStretch()

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("status")
        titlebar.addWidget(self.status_label)

        root.addLayout(titlebar)
        root.addSpacing(20)

        # -- lock icon --
        self.icon_label = QLabel("\U0001f512")
        self.icon_label.setObjectName("icon")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.icon_label)
        root.addSpacing(8)

        # -- shortcut info --
        shortcut_display = " + ".join(
            k.upper() for k in self.config["unlock_keys"]
        )
        self.shortcut_label = QLabel(f"Unlock:  {shortcut_display}")
        self.shortcut_label.setObjectName("shortcut_info")
        self.shortcut_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.shortcut_label)
        root.addSpacing(16)

        # -- lock / unlock button --
        self.lock_btn = QPushButton("LOCK")
        self.lock_btn.setObjectName("lock")
        self.lock_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lock_btn.clicked.connect(self._toggle_lock)
        root.addWidget(self.lock_btn)
        root.addSpacing(10)

        # -- settings button --
        self.settings_btn = QPushButton("\u2699  Change shortcut")
        self.settings_btn.setObjectName("settings")
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.clicked.connect(self._open_settings)
        root.addWidget(self.settings_btn)

        root.addStretch()

    # ---- frameless drag support -------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    # ---- paint rounded background -----------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 12, 12)
        painter.fillPath(path, QBrush(QColor("#18181c")))
        painter.setPen(QColor("#333338"))
        painter.drawPath(path)

    # ---- lock / unlock logic ----------------------------------------------
    def _toggle_lock(self):
        if not self.is_locked:
            if not self._check_accessibility():
                self._show_accessibility_dialog()
                return
            if self.locker.lock():
                self.is_locked = True
                self.icon_label.setText("\U0001f513")
                self.status_label.setText("Locked")
                self.status_label.setStyleSheet("color: #ff3b30;")
                self.lock_btn.setText("UNLOCK")
                self.lock_btn.setObjectName("unlock")
                self.lock_btn.setStyleSheet(STYLESHEET)
                self.settings_btn.setEnabled(False)
                self.showMinimized()
        else:
            self.locker.unlock()
            self._reset_ui()
            self.showNormal()
            self.raise_()
            self.activateWindow()

    def _on_silent_unlock(self):
        """Called via signal when unlocked with keyboard shortcut - stays minimized."""
        self._reset_ui()

    def _reset_ui(self):
        self.is_locked = False
        self.icon_label.setText("\U0001f512")
        self.status_label.setText("Ready")
        self.status_label.setStyleSheet("color: #8a8a8e;")
        self.lock_btn.setText("LOCK")
        self.lock_btn.setObjectName("lock")
        self.lock_btn.setStyleSheet(STYLESHEET)
        self.settings_btn.setEnabled(True)

    # ---- settings ---------------------------------------------------------
    def _open_settings(self):
        if self.is_locked:
            return
        SettingsDialog(self, self.config["unlock_keys"], self._apply_new_keys).exec()

    def _apply_new_keys(self, new_keys):
        self.config["unlock_keys"] = new_keys
        save_config(self.config)
        self.locker.set_unlock_keycodes(keys_to_keycodes(new_keys))
        display = " + ".join(k.upper() for k in new_keys)
        self.shortcut_label.setText(f"Unlock:  {display}")

    # ---- accessibility check ----------------------------------------------
    @staticmethod
    def _check_accessibility():
        tap = Quartz.CGEventTapCreate(
            Quartz.kCGSessionEventTap,
            Quartz.kCGHeadInsertEventTap,
            Quartz.kCGEventTapOptionDefault,
            (1 << Quartz.kCGEventKeyDown),
            lambda p, t, e, r: e,
            None,
        )
        if tap:
            Quartz.CFRelease(tap)
            return True
        return False

    @staticmethod
    def _show_accessibility_dialog():
        reply = QMessageBox.question(
            None,
            "Permission Required",
            "This app requires Accessibility permissions.\n\n"
            "Open System Settings?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            subprocess.Popen(
                ["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"]
            )

    # ---- close ------------------------------------------------------------
    def closeEvent(self, event):
        if self.is_locked:
            self.locker.unlock()
        event.accept()


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("macOS Lock")
    window = LockWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
