from Jarvis.plugins.base import Plugin, PluginMetadata


class WebSearchPlugin(Plugin):

    metadata = PluginMetadata(
        name="web_search",
        version="1.0",
        description="Busca informações na web",
        capabilities=["search"],
        risk_level="low",
        dev_only=False
    )

    def can_handle(self, intent: str) -> bool:
        return "buscar" in intent or "pesquisar" in intent

    def prepare(self, data):
        return {
            "action": "web_search",
            "query": data.get("query")
        }


PLUGIN_CLASS = WebSearchPlugin