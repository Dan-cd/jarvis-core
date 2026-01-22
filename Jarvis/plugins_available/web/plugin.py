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
                data=None,
                origin="web",
                content="(dry-run) Busca web planejada.",
                confidence=0.0,
            )

        web_request = self._build_request(action)
        if not web_request:
            return ActionResult(
                success=False,
                message="Consulta web inválida ou sem query.",
                data=None,
                origin="web",
                content="",
                confidence=0.0,
            )

        try:
            # tenta cache primeiro
            cached = WebPlugin.cache.get(web_request.query)
            if cached:
                return ActionResult(
                    success=True,
                    message="Resultado retornado do cache.",
                    data=cached,
                    origin="web",
                    content=getattr(cached, "content", None) or "",
                    confidence=getattr(cached, "confidence", 0.0),
                )

            # faz a busca real
            result = self._fetch(web_request)

            # armazena no cache
            WebPlugin.cache.set(web_request.query, result)

            return ActionResult(
                success=True,
                message="Busca web concluída.",
                data=result,
                origin="web",
                content=result.content,
                confidence=getattr(result, "confidence", 0.0),
            )

        except Exception as e:
            # encapsula exceção de plugin em PluginError
            return ActionResult(
                success=False,
                message=f"Erro ao acessar a web: {str(e)}",
                data=None,
                origin="web",
                content="",
                confidence=0.0,
            )

    def _build_request(self, action: ActionRequest) -> WebRequest | None:
        query = (
            (action.params or {}).get("query")
            or (action.params or {}).get("url")
            or action.intent.raw
        )
        # Normaliza queries iniciadas por verbos comuns (ex: "pesquise", "procure")
        try:
            import re
            query = query.strip()
            # remove verbos iniciais como 'pesquise', 'procure', 'pesquisar', 'buscar', 'busca'
            query = re.sub(r'^(pesquise|pesquisar|procure|procura|procurem|procura-se|buscar|busca)\b\s*', '', query, flags=re.I)
            # remove frases iniciais como 'o que é', 'oque é', 'qual é'
            query = re.sub(r'^(o que é|oque é|o que|oque|qual é|qual)\b\s*', '', query, flags=re.I)
            query = query.strip(' ?')
        except Exception:
            pass
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
                "kl": "pt-br",
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        # Lista de fontes (lista para padronização)
        sources: list[str] = []
        if data.get("AbstractSource"):
            sources.append(data["AbstractSource"])

        # Função utilitária para tentar extrair texto de RelatedTopics recursivamente
        def extract_from_related(topics) -> list[str]:
            texts: list[str] = []
            if not topics:
                return texts
            for item in topics:
                if isinstance(item, dict):
                    if item.get("Text"):
                        texts.append(item["Text"])
                    # pode ter sub-topics
                    if item.get("Topics"):
                        texts.extend(extract_from_related(item.get("Topics")))
            return texts

        # 1) Prefer AbstractText
        if data.get("AbstractText"):
            return WebResult(
                query=req.query,
                content=data["AbstractText"],
                sources=sources or ["duckduckgo"],
                confidence=0.8,
                is_summary=True,
                is_partial=False
            )

        # 2) Heading
        if data.get("Heading"):
            return WebResult(
                query=req.query,
                content=data["Heading"],
                sources=sources or ["duckduckgo"],
                confidence=0.4,
                is_summary=False,
                is_partial=True
            )

        # 3) Results (lista de dicionários com 'Text')
        if data.get("Results") and isinstance(data.get("Results"), list):
            for r in data.get("Results"):
                if isinstance(r, dict) and r.get("Text"):
                    return WebResult(
                        query=req.query,
                        content=r.get("Text"),
                        sources=sources or ["duckduckgo"],
                        confidence=0.6,
                        is_summary=False,
                        is_partial=True
                    )

        # 4) RelatedTopics
        related = data.get("RelatedTopics")
        texts = extract_from_related(related)
        if texts:
            # concatena os primeiros 2 textos como resumo parcial
            excerpt = "\n\n".join(texts[:2])
            return WebResult(
                query=req.query,
                content=excerpt,
                sources=sources or ["duckduckgo"],
                confidence=0.5,
                is_summary=False,
                is_partial=True
            )

        # Se chegamos aqui, nada útil foi encontrado — logar JSON bruto para depuração
        try:
            log_path = Path("data/logs/web_debug.log")
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with log_path.open("a", encoding="utf-8") as lf:
                lf.write(f"--- {req.query} @ {datetime.now().isoformat()}\n")
                lf.write("RAW JSON:\n")
                lf.write(str(data))
                lf.write("\n\n")
        except Exception:
            pass

        return WebResult(
            query=req.query,
            content="Nenhum resultado relevante encontrado.",
            sources=sources or ["duckduckgo"],
            confidence=0.1,
            is_summary=False,
            is_partial=True
        )
