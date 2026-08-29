from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sdk"))

import plugin_runtime


class PluginRuntimeTests(unittest.TestCase):
    def tearDown(self) -> None:
        plugin_runtime.unload_all()

    def _write_plugin(self, directory: Path, source: str, name: str = "test.plugin") -> Path:
        path = directory / name
        path.write_text(source, encoding="utf-8")
        return path

    def test_loads_plugin_and_calls_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_plugin(
                Path(tmp),
                """
from base_plugin import BasePlugin
__id__ = "test_plugin"
__name__ = "Test Plugin"

class Plugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.loaded = False

    def on_plugin_load(self):
        self.loaded = True
""",
            )
            loaded = plugin_runtime.load_plugin(path)
            self.assertTrue(loaded.instance.loaded)
            self.assertEqual(loaded.metadata["__version__"], "1.0")

    def test_rejects_invalid_plugin_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_plugin(
                Path(tmp),
                """
from base_plugin import BasePlugin
__id__ = "1bad"
__name__ = "Bad"

class Plugin(BasePlugin):
    pass
""",
            )
            with self.assertRaises(plugin_runtime.PluginLoadError):
                plugin_runtime.load_plugin(path)


if __name__ == "__main__":
    unittest.main()
