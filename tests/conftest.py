"""Test configuration - makes modules with hyphens importable and mocks macOS-only deps."""

import importlib
import sys
import os
from unittest.mock import MagicMock

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Mock Quartz if not available (for CI / non-macOS environments)
if "Quartz" not in sys.modules:
    quartz_mock = MagicMock()
    quartz_mock.kCGEventKeyDown = 10
    quartz_mock.kCGEventKeyUp = 11
    quartz_mock.kCGSessionEventTap = 0
    quartz_mock.kCGHeadInsertEventTap = 0
    quartz_mock.kCGEventTapOptionDefault = 0
    quartz_mock.kCGKeyboardEventKeycode = 9
    quartz_mock.kCGEventLeftMouseDown = 1
    quartz_mock.kCGEventLeftMouseUp = 2
    quartz_mock.kCGEventRightMouseDown = 3
    quartz_mock.kCGEventRightMouseUp = 4
    quartz_mock.kCGEventMouseMoved = 5
    quartz_mock.kCGEventLeftMouseDragged = 6
    quartz_mock.kCGEventRightMouseDragged = 7
    quartz_mock.kCGEventScrollWheel = 22
    quartz_mock.kCGEventOtherMouseDown = 25
    quartz_mock.kCGEventOtherMouseUp = 26
    quartz_mock.kCFAllocatorDefault = None
    quartz_mock.kCFRunLoopCommonModes = "kCFRunLoopCommonModes"
    sys.modules["Quartz"] = quartz_mock

# Mock PyQt6 if not available (for CI without display)
for mod_name in [
    "PyQt6", "PyQt6.QtWidgets", "PyQt6.QtCore", "PyQt6.QtGui",
]:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MagicMock()

# Import module with hyphens in filename using importlib
_spec = importlib.util.spec_from_file_location(
    "macos_lock_gui", os.path.join(project_root, "macos-lock-gui.py")
)
macos_lock_gui = importlib.util.module_from_spec(_spec)
sys.modules["macos_lock_gui"] = macos_lock_gui
_spec.loader.exec_module(macos_lock_gui)

_spec2 = importlib.util.spec_from_file_location(
    "macos_lock_cli", os.path.join(project_root, "macos-lock.py")
)
macos_lock_cli = importlib.util.module_from_spec(_spec2)
sys.modules["macos_lock_cli"] = macos_lock_cli
_spec2.loader.exec_module(macos_lock_cli)
