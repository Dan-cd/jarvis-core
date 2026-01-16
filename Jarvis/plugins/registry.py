class PluginRegistry:
    _registry: dict = {}

    @classmethod
    def register(cls, intent, plugin_cls):
        cls._registry[intent] = plugin_cls

    @classmethod
    def find_by_intent(cls, intent):
        return cls._registry.get(intent)