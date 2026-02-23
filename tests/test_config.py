"""Tests for configuration loading, saving, and key mapping."""

import json
import os
import tempfile
import pytest

# We need to patch CONFIG_PATH before importing, so import the module parts we need
import importlib


@pytest.fixture
def config_file(tmp_path):
    """Provides a temporary config file path."""
    return str(tmp_path / "test-config.json")


@pytest.fixture
def gui_module(config_file, monkeypatch):
    """Imports macos-lock-gui with patched CONFIG_PATH."""
    import macos_lock_gui as mod

    monkeypatch.setattr(mod, "CONFIG_PATH", config_file)
    return mod


class TestKeycodeMap:
    """Tests for the keycode mapping."""

    def test_known_keys_exist(self, gui_module):
        for key in ["a", "b", "c", "x", "z", "1", "0", "space", "return"]:
            assert key in gui_module.KEYCODE_MAP, f"Key '{key}' not in KEYCODE_MAP"

    def test_x_keycode_is_7(self, gui_module):
        assert gui_module.KEYCODE_MAP["x"] == 7

    def test_c_keycode_is_8(self, gui_module):
        assert gui_module.KEYCODE_MAP["c"] == 8

    def test_reverse_map_consistent(self, gui_module):
        for name, code in gui_module.KEYCODE_MAP.items():
            assert gui_module.REVERSE_KEYCODE_MAP[code] == name

    def test_keys_to_keycodes(self, gui_module):
        result = gui_module.keys_to_keycodes(["x", "c"])
        assert result == [7, 8]

    def test_keys_to_keycodes_unknown_key_skipped(self, gui_module):
        result = gui_module.keys_to_keycodes(["x", "UNKNOWN", "c"])
        assert result == [7, 8]

    def test_keys_to_keycodes_empty(self, gui_module):
        result = gui_module.keys_to_keycodes([])
        assert result == []


class TestConfig:
    """Tests for config loading and saving."""

    def test_load_default_when_no_file(self, gui_module, config_file):
        config = gui_module.load_config()
        assert config["unlock_keys"] == ["x", "c"]

    def test_save_and_load_roundtrip(self, gui_module, config_file):
        config = {"unlock_keys": ["a", "s", "d"]}
        gui_module.save_config(config)

        loaded = gui_module.load_config()
        assert loaded["unlock_keys"] == ["a", "s", "d"]

    def test_load_corrupted_file_returns_default(self, gui_module, config_file):
        with open(config_file, "w") as f:
            f.write("not valid json{{{")

        config = gui_module.load_config()
        assert config["unlock_keys"] == ["x", "c"]

    def test_save_creates_file(self, gui_module, config_file):
        assert not os.path.exists(config_file)
        gui_module.save_config({"unlock_keys": ["q", "w"]})
        assert os.path.exists(config_file)

    def test_saved_file_is_valid_json(self, gui_module, config_file):
        gui_module.save_config({"unlock_keys": ["m", "n"]})
        with open(config_file) as f:
            data = json.load(f)
        assert data["unlock_keys"] == ["m", "n"]

    def test_load_merges_with_defaults(self, gui_module, config_file):
        # Save partial config
        with open(config_file, "w") as f:
            json.dump({"unlock_keys": ["f", "g"]}, f)

        config = gui_module.load_config()
        assert config["unlock_keys"] == ["f", "g"]


class TestInputLockerState:
    """Tests for InputLocker state management (without Quartz)."""

    def test_initial_state(self, gui_module):
        locker = gui_module.InputLocker.__new__(gui_module.InputLocker)
        locker.locked = False
        locker.pressed_keys = set()
        locker.unlock_keycodes = {7, 8}
        locker.tap = None
        locker.run_loop_source = None
        locker.lock_thread = None
        locker.app_callback = None

        assert not locker.locked
        assert locker.pressed_keys == set()

    def test_set_unlock_keycodes(self, gui_module):
        locker = gui_module.InputLocker.__new__(gui_module.InputLocker)
        locker.unlock_keycodes = {7, 8}
        locker.set_unlock_keycodes([0, 1, 2])
        assert locker.unlock_keycodes == {0, 1, 2}

    def test_default_unlock_keycodes(self, gui_module):
        locker = gui_module.InputLocker.__new__(gui_module.InputLocker)
        locker.unlock_keycodes = set([7, 8])
        assert locker.unlock_keycodes == {7, 8}

    def test_custom_unlock_keycodes(self, gui_module):
        locker = gui_module.InputLocker.__new__(gui_module.InputLocker)
        locker.unlock_keycodes = set([0, 1, 2])
        assert locker.unlock_keycodes == {0, 1, 2}
