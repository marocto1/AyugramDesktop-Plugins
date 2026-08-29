from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SDK = ROOT / "runtime" / "sdk"
RUNTIME = ROOT / "runtime"

sys.path.insert(0, str(SDK))
sys.path.insert(0, str(RUNTIME))

import base_plugin  # noqa: E402
import loader  # noqa: E402


class LoaderTests(unittest.TestCase):
    def tearDown(self) -> None:
        loader.unload_all()

    def test_load_settings_and_unload(self) -> None:
        plugin_path = ROOT / "examples" / "hello.plugin"

        metadata = loader.load_plugin(str(plugin_path))
        self.assertEqual(metadata["id"], "desktop_hello")
        self.assertEqual(metadata["name"], "Desktop Hello")
        self.assertIn("desktop_hello", loader.loaded_plugin_ids())

        instance = loader._loaded["desktop_hello"].instance
        self.assertEqual(base_plugin._plugin_id(instance), "desktop_hello")

        settings = loader.create_settings("desktop_hello")
        self.assertEqual(len(settings), 2)
        self.assertEqual(settings[0].kind, "header")
        self.assertEqual(settings[1].kind, "switch")
        self.assertEqual(settings[1].key, "enabled")

        loader.unload_plugin("desktop_hello")
        self.assertNotIn("desktop_hello", loader.loaded_plugin_ids())


if __name__ == "__main__":
    unittest.main()
