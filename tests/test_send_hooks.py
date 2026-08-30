from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sdk"))

import plugin_runtime


class SendMessageHookTests(unittest.TestCase):
    def tearDown(self) -> None:
        plugin_runtime.unload_all()

    def _write_plugin(
        self,
        directory: Path,
        plugin_id: str,
        body: str,
        priority: int = 0,
    ) -> Path:
        path = directory / f"{plugin_id}.plugin"
        path.write_text(
            f"""
from base_plugin import BasePlugin, HookResult, HookStrategy
__id__ = "{plugin_id}"
__name__ = "{plugin_id}"

class Plugin(BasePlugin):
    def on_plugin_load(self):
        self.add_on_send_message_hook({priority})

{body}
""",
            encoding="utf-8",
        )
        return path

    def test_modify_chains_into_next_hook(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self._write_plugin(
                directory,
                "first",
                """    def on_send_message_hook(self, account, params):
        params.message += ":first"
        return HookResult(strategy=HookStrategy.MODIFY, params=params)
""",
                priority=20,
            )
            self._write_plugin(
                directory,
                "second",
                """    def on_send_message_hook(self, account, params):
        params.message += ":second"
        return HookResult(strategy=HookStrategy.MODIFY, params=params)
""",
                priority=10,
            )
            plugin_runtime.discover_and_load(directory)

            result = plugin_runtime.dispatch_text_message(3, "start")

            self.assertFalse(result.cancelled)
            self.assertEqual(result.params.message, "start:first:second")

    def test_cancel_stops_send_and_lower_priority_hooks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self._write_plugin(
                directory,
                "cancel",
                """    def on_send_message_hook(self, account, params):
        return HookResult(strategy=HookStrategy.CANCEL)
""",
                priority=20,
            )
            self._write_plugin(
                directory,
                "later",
                """    def on_send_message_hook(self, account, params):
        params.message = "should-not-run"
        return HookResult(strategy=HookStrategy.MODIFY, params=params)
""",
                priority=10,
            )
            plugin_runtime.discover_and_load(directory)

            result = plugin_runtime.dispatch_text_message(0, "original")

            self.assertTrue(result.cancelled)
            self.assertEqual(result.params.message, "original")

    def test_modify_final_stops_further_processing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self._write_plugin(
                directory,
                "final",
                """    def on_send_message_hook(self, account, params):
        params.message = "final"
        return HookResult(strategy=HookStrategy.MODIFY_FINAL, params=params)
""",
                priority=20,
            )
            self._write_plugin(
                directory,
                "later",
                """    def on_send_message_hook(self, account, params):
        params.message = "wrong"
        return HookResult(strategy=HookStrategy.MODIFY, params=params)
""",
                priority=10,
            )
            plugin_runtime.discover_and_load(directory)

            result = plugin_runtime.dispatch_text_message(0, "original")

            self.assertFalse(result.cancelled)
            self.assertEqual(result.params.message, "final")

    def test_unregistered_hook_is_not_called(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            path = directory / "unregistered.plugin"
            path.write_text(
                """
from base_plugin import BasePlugin, HookResult, HookStrategy
__id__ = "unregistered"
__name__ = "Unregistered"

class Plugin(BasePlugin):
    def on_send_message_hook(self, account, params):
        params.message = "wrong"
        return HookResult(strategy=HookStrategy.MODIFY, params=params)
""",
                encoding="utf-8",
            )
            plugin_runtime.load_plugin(path)

            result = plugin_runtime.dispatch_text_message(0, "original")

            self.assertFalse(result.cancelled)
            self.assertEqual(result.params.message, "original")

    def test_hook_exception_does_not_break_send(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self._write_plugin(
                directory,
                "broken",
                """    def on_send_message_hook(self, account, params):
        raise RuntimeError("boom")
""",
                priority=20,
            )
            self._write_plugin(
                directory,
                "working",
                """    def on_send_message_hook(self, account, params):
        params.message = "recovered"
        return HookResult(strategy=HookStrategy.MODIFY, params=params)
""",
                priority=10,
            )
            plugin_runtime.discover_and_load(directory)

            result = plugin_runtime.dispatch_text_message(0, "original")

            self.assertFalse(result.cancelled)
            self.assertEqual(result.params.message, "recovered")

    def test_account_is_forwarded_to_hook(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self._write_plugin(
                directory,
                "account",
                """    def on_send_message_hook(self, account, params):
        params.message = str(account)
        return HookResult(strategy=HookStrategy.MODIFY, params=params)
""",
            )
            plugin_runtime.discover_and_load(directory)

            result = plugin_runtime.dispatch_text_message(42, "original")

            self.assertEqual(result.params.message, "42")


if __name__ == "__main__":
    unittest.main()
