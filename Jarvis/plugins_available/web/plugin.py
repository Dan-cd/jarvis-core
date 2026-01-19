import requests
from typing import TYPE_CHECKING

from Jarvis.plugins.base import Plugin
from Jarvis.core.action_request import ActionRequest
from Jarvis.core.action_result import ActionResult
from Jarvis.core.intent import IntentType
from Jarvis.plugins_available.web.models import WebRequest, WebResult
from Jarvis.plugins_available.web.web_cache import WebCache
from Jarvis.core.errors import PluginError

if TYPE_CHECKING:
    # evita importação circular em tipos
    from Jarvis.core.errors import JarvisError


class WebPlugin(Plugin):
    """
    Plugin WEB — V6.5
    Responsabilidade:
      1) construir WebRequest
      2) buscar resultados com cache
      3) retornar WebResult com fontes e confiança
    """

    metadata = {
        "name": "web.fetch",
        "risk_level": "low",
        "description": "Busca conteúdo textual simples na web",
    }

    INTENT = IntentType.WEB_FETCH
    cache = WebCache()

    def execute(self, action: ActionRequest, dry_run: bool = False) -> ActionResult:
        if dry_run:
            return ActionResult(
                success=True,
                message="(dry-run) Busca web planejada.",
                data=None
            )

        web_request = self._build_request(action)
        if not web_request:
            return ActionResult(
                success=False,
                message="Consulta web inválida ou sem query.",
                data=None
            )

        try:
            # tenta cache primeiro
            cached = WebPlugin.cache.get(web_request.query)
            if cached:
                return ActionResult(
                    success=True,
                    message="Resultado retornado do cache.",
                    data=cached
                )

            # faz a busca real
            result = self._fetch(web_request)

            # armazena no cache
            WebPlugin.cache.set(web_request.query, result)

            return ActionResult(
                success=True,
                message="Busca web concluída.",
                data=result
            )

        except Exception as e:
            # encapsula exceção de plugin em PluginError
            return ActionResult(
                success=False,
                message=f"Erro ao acessar a web: {str(e)}",
                data=None
            )

    def _build_request(self, action: ActionRequest) -> WebRequest | None:
        query = (
            action.params.get("query")
            or action.params.get("url")
            or action.intent.raw
        )
        if not query:
            return None
        return WebRequest(query=query)

    def _fetch(self, req: WebRequest) -> WebResult:
        """
        Faz a requisição na API externa (DuckDuckGo por padrão)
        e converte para WebResult de forma padronizada.
        """

        response = requests.get(
            "https://api.duckduckgo.com/",
            params={
                "q": req.query,
                "format": "json",
                "no_redirect": 1,
                "no_html": 1,
                "skip_disambig": 1,
                "kl": "br-pt",
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        # Lista de fontes (lista para padronização)
        sources: list[str] = []

        # DuckDuckGo tem AbstractText, Heading, Relinks, etc.
        # vamos coletar tudo que pudermos como fonte
        if data.get("AbstractSource"):
            sources.append(data["AbstractSource"])

        # fiel à sua implementação anterior
        if data.get("AbstractText"):
            return WebResult(
                query=req.query,
                content=data["AbstractText"],
                sources=sources or ["duckduckgo"],
                confidence=0.8,
                is_summary=True,
                is_partial=False
            )

        if data.get("Heading"):
            return WebResult(
                query=req.query,
                content=data["Heading"],
                sources=sources or ["duckduckgo"],
                confidence=0.4,
                is_summary=False,
                is_partial=True
            )

        return WebResult(
            query=req.query,
            content="Nenhum resultado relevante encontrado.",
            sources=sources or ["duckduckgo"],
            confidence=0.1,
            is_summary=False,
            is_partial=True
        )
