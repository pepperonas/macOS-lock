"""
py2app build script for macOS Lock

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['macos-lock-gui.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'plist': {
        'CFBundleName': 'macOS Lock',
        'CFBundleDisplayName': 'macOS Lock',
        'CFBundleIdentifier': 'com.yourcompany.macoslock',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
    },
    'includes': ['Quartz'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)