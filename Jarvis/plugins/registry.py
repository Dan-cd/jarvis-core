class PluginRegistry:
    _registry = {}

    @classmethod
    def register(cls, intent, plugin_cls):
        metadata = getattr(plugin_cls, "metadata", {})

        cls._registry[intent] = {
            "plugin": plugin_cls,
            "action": metadata.get("name"),
            "risk": metadata.get("risk_level", "low"),
            "metadata": metadata
        }

    @classmethod
    def find_by_intent(cls, intent):
        return cls._registry.get(intent)