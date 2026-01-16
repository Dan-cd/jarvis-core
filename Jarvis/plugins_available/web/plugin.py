import requests
from Jarvis.plugins.base import Plugin
from Jarvis.core.action_request import ActionRequest
from Jarvis.core.action_result import ActionResult
from Jarvis.core.intent import IntentType
from Jarvis.plugins_available.web.models import WebRequest, WebResult
from Jarvis.plugins_available.web.web_cache import WebCache

class WebPlugin(Plugin):
    """
    Plugin WEB — V6
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
            )

        web_request = self._build_request(action)
        if not web_request:
            return ActionResult(
                success=False,
                message="Consulta web inválida ou ausente.",
            )

        try:
            result = self._fetch(web_request)
            return ActionResult(
                success=True,
                message="Busca web concluída.",
                data=result,
            )

        except Exception as e:
            return ActionResult(
                success=False,
                message=f"Erro ao acessar a web: {str(e)}",
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

        if data.get("AbstractText"):
            return WebResult(
                query=req.query,
                content=data["AbstractText"],
                source="duckduckgo",
                confidence=0.8,
                is_summary=True,
                is_partial=False,
            )

        if data.get("Heading"):
            return WebResult(
                query=req.query,
                content=data["Heading"],
                source="duckduckgo",
                confidence=0.4,
                is_summary=False,
                is_partial=True,
            )

        return WebResult(
            query=req.query,
            content="Nenhum resultado relevante encontrado.",
            source="duckduckgo",
            confidence=0.1,
            is_summary=False,
            is_partial=True,
        )
