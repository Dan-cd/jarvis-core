from typing import Type, List


class PluginRegistry:
    """
    Registro global de plugins mapeados por intenção.

    find_by_intent() agora retorna sempre uma lista —
    pode ser vazia, ou conter uma ou mais classes de plugin.
    """

    _registry: dict = {}

    @classmethod
    def register(cls, intent, plugin_cls):
        """
        Registra um plugin para uma intenção específica.

        Args:
            intent: IntentType (chave)
            plugin_cls: classe do plugin (não instanciado)
        """
        cls._registry[intent] = plugin_cls

    @classmethod
    def find_by_intent(cls, intent) -> List[Type]:
        """
        Retorna uma lista de plugins registrados para esta intenção.

        Mesmo que seja um único plugin,
        retornamos lista para compatibilidade com Executor/Router.
        """
        plugin_cls = cls._registry.get(intent)

        if plugin_cls is None:
            return []  # lista vazia
        return [plugin_cls]  # lista com um elemento

