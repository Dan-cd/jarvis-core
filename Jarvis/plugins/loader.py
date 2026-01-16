
from Jarvis.plugins.registry import PluginRegistry
import importlib
import pkgutil

from Jarvis.plugins_available.filesystem import __path__ as fs_path
from Jarvis.plugins_available.web.plugin import WebPlugin
from Jarvis.core.intent import IntentType


def load_plugins():
    _load_filesystem_plugins()
    _load_web_plugins()


def _load_filesystem_plugins():
    for _, module_name, _ in pkgutil.iter_modules(fs_path):
        module = importlib.import_module(
            f"Jarvis.plugins_available.filesystem.{module_name}"
        )

        plugin_cls = getattr(module, "PLUGIN_CLASS", None)
        if not plugin_cls:
            continue

        intent = getattr(plugin_cls, "INTENT", None)
        if not intent:
            continue

        PluginRegistry.register(intent, plugin_cls)


def _load_web_plugins():
    PluginRegistry.register(IntentType.WEB_FETCH, WebPlugin)