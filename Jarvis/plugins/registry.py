from Jarvis.core.intent import IntentType


class PluginRegistry:
    _registry: dict[IntentType, type] = {}

    @classmethod
    def register(cls, intent: IntentType, plugin_cls: type):
        cls._registry[intent] = plugin_cls

    @classmethod
    def find_by_intent(cls, intent: IntentType):
        return cls._registry.get(intent)