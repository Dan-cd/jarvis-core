from Jarvis.plugins.registry import PluginRegistry
import importlib
import pkgutil
import Jarvis.plugins_available.filesystem


def load_plugins():
    for _, module_name, _ in pkgutil.iter_modules(
        Jarvis.plugins_available.filesystem.__path__
    ):
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