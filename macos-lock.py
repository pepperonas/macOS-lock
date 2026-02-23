#!/usr/bin/env python3
"""
macOS keyboard and trackpad lock (CLI).
Blocks all input until the configured key combination is pressed.
"""

import Quartz
import threading
import json
import sys
import os

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


def load_config():
    default = {"unlock_keys": ["x", "c"]}
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                saved = json.load(f)
            default.update(saved)
        except (json.JSONDecodeError, IOError):
            pass
    return default


class InputLocker:
    def __init__(self, unlock_keycodes):
        self.locked = True
        self.pressed_keys = set()
        self.unlock_keycodes = set(unlock_keycodes)
        self.unlock_thread = None

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
                self.locked = False
                if not self.unlock_thread:
                    self.unlock_thread = threading.Timer(0.2, self.stop_app)
                    self.unlock_thread.start()
                return event

        return None

    def stop_app(self):
        Quartz.CFRunLoopStop(Quartz.CFRunLoopGetCurrent())

    def run(self):
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
            | (1 << Quartz.kCGEventOtherMouseDragged)
            | (1 << Quartz.kCGEventTabletPointer)
            | (1 << Quartz.kCGEventTabletProximity)
        )

        tap = Quartz.CGEventTapCreate(
            Quartz.kCGSessionEventTap,
            Quartz.kCGHeadInsertEventTap,
            Quartz.kCGEventTapOptionDefault,
            event_mask,
            self.event_callback,
            None,
        )

        if not tap:
            print("Error: Could not create Event Tap!")
            print("Tip: Grant Terminal/Python access in System Settings > ")
            print("   Privacy & Security > Privacy > Accessibility")
            sys.exit(1)

        run_loop_source = Quartz.CFMachPortCreateRunLoopSource(
            Quartz.kCFAllocatorDefault, tap, 0
        )
        Quartz.CFRunLoopAddSource(
            Quartz.CFRunLoopGetCurrent(),
            run_loop_source,
            Quartz.kCFRunLoopCommonModes,
        )
        Quartz.CGEventTapEnable(tap, True)
        Quartz.CFRunLoopRun()


def main():
    config = load_config()
    keycodes = [KEYCODE_MAP[k] for k in config["unlock_keys"] if k in KEYCODE_MAP]
    if not keycodes:
        keycodes = [7, 8]  # fallback X+C

    locker = InputLocker(keycodes)
    try:
        locker.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
