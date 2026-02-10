import requests
from typing import TYPE_CHECKING
from pathlib import Path
from datetime import datetime
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

    # Blacklist de domínios (anúncios, trackers e lixo técnico)
    BLACKLIST_DOMAINS = {
        "duckduckgo.com", "bing.com", "google.com", "y.js", "doubleclick.net",
        "adservice.google.com", "googleadservices.com", "adnxs.com", "taboola.com",
        "outbrain.com", "amazon-adsystem.com", "facebook.com/tr", "adsystem",
        "analytics", "tracking", "pixel", "ad_domain"
    }

    # Palavras-chave de lixo ou anúncios
    BLACKLIST_KEYWORDS = {
        "patrocinado", "patrocinados", "anúncio", "anuncio", "ads", "advertisement",
        "sponsored", "promoção", "oferta", "compre agora", "venda", "shopping"
    }

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

            # Qualificação Final: Se o resultado retornado for "Nenhum resultado", 
            # não salvamos no cache para permitir novas tentativas se o scraper falhar temporariamente.
            if result.content and "Nenhum resultado" not in result.content:
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
            or (action.intent.raw if action.intent else None)
        )
        # Normaliza queries iniciadas por verbos comuns (ex: "pesquise", "procure")
        try:
            import re
            query = query.strip()
            # remove verbos iniciais como 'pesquise', 'procure', 'pesquisar', 'buscar', 'busca'
            query = re.sub(r'^(pesquise|pesquisar|procure|procura|procurem|procura-se|buscar|busca)\b\s*', '', query, flags=re.I)
            # remove frases iniciais como 'o que é', 'oque é', 'o que|oque', 'qual é|qual'
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
        e converte para WebResult de forma padronizada com filtragem.
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

        # 1) Prefer AbstractText (Geralmente alta qualidade)
        if data.get("AbstractText") and not self._is_trash(data.get("Heading", ""), data["AbstractText"], data.get("AbstractURL", "")):
            return WebResult(
                query=req.query,
                content=data["AbstractText"],
                sources=[data.get("AbstractSource") or "duckduckgo"],
                confidence=0.9,
                is_summary=True,
                is_partial=False
            )

        # Se não tem Abstract, tentamos coletar múltiplos resultados qualificados
        qualified_results = []
        
        # 2) Results
        if data.get("Results") and isinstance(data.get("Results"), list):
            for r in data.get("Results"):
                if isinstance(r, dict) and r.get("Text"):
                    url = r.get("FirstURL", "")
                    text = r.get("Text", "")
                    if not self._is_trash("", text, url):
                        qualified_results.append(f"Fonte: {url}\n{text}")

        # 3) RelatedTopics
        related = data.get("RelatedTopics") or []
        for item in related:
            if isinstance(item, dict) and item.get("Text"):
                url = item.get("FirstURL", "")
                text = item.get("Text", "")
                if not self._is_trash("", text, url):
                    qualified_results.append(f"Fonte: {url}\n{text}")

        if qualified_results:
            # Retorna os top 2 qualificados
            return WebResult(
                query=req.query,
                content="\n\n".join(qualified_results[:2]),
                sources=["duckduckgo-api"],
                confidence=0.7,
                is_summary=False,
                is_partial=True
            )

        # 4) Fallback: Scraping HTML simples (html.duckduckgo.com)
        try:
            return self._scrape_html(req)
        except Exception:
            pass

        return WebResult(
            query=req.query,
            content="Nenhum resultado qualificado encontrado.",
            sources=["duckduckgo"],
            confidence=0.1,
            is_summary=False,
            is_partial=True
        )

    def _scrape_html(self, req: WebRequest) -> WebResult:
        import re
        from urllib.parse import unquote

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        }
        
        resp = requests.post(
            "https://html.duckduckgo.com/html/",
            data={"q": req.query},
            headers=headers,
            timeout=10
        )
        resp.raise_for_status()
        html = resp.text

        # Extração agnóstica a ordem
        matches = re.findall(r'<a[^>]+href="([^"]+)"[^]*class="[^"]*result__a[^"]*"[^]*>(.*?)</a>', html)
        if not matches:
             matches = re.findall(r'<a[^>]+class="[^"]*result__a[^"]*"[^]*href="([^"]+)"[^]*>(.*?)</a>', html)

        links = matches
        snippets = re.findall(r'<a[^>]+class="[^"]*result__snippet[^"]*"[^]*href="[^"]+">(.*?)</a>', html)
        if not snippets:
            snippets = re.findall(r'<a[^>]+href="[^"]+"[^]*class="[^"]*result__snippet[^"]*"[^]*>(.*?)</a>', html)

        final_text_parts = []
        count = 0
        limit = 4 # Analisamos mais para filtrar ads

        for i in range(min(len(links), len(snippets), 10)):
            raw_url = links[i][0]
            title = re.sub(r'<[^>]+>', '', links[i][1])
            snippet = re.sub(r'<[^>]+>', '', snippets[i])
            
            # Unquote DDG wrapper
            url = raw_url
            if "uddg=" in url:
                try:
                    url = unquote(url.split("uddg=")[1].split("&")[0])
                except: pass

            # Limpeza e Filtragem
            url = self._clean_url(url)
            if self._is_trash(title, snippet, url):
                continue

            # Verificação Semântica Simples: 
            # Se a query for longa, exige que ao menos um termo significativo esteja no resultado
            if not self._is_relevant(req.query, title, snippet):
                continue

            final_text_parts.append(f"Título: {title}\nURL: {url}\nResumo: {snippet}")
            count += 1
            if count >= 3: break

        if final_text_parts:
            return WebResult(
                query=req.query,
                content="\n\n".join(final_text_parts),
                sources=["duckduckgo-html"],
                confidence=0.8,
                is_summary=False,
                is_partial=True
            )
        
        raise Exception("Filtros removeram todos os resultados.")

    def _clean_url(self, url: str) -> str:
        from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
        try:
            parsed = urlparse(url)
            if not parsed.netloc: return url
            # Remove trackers comuns
            qs = parse_qs(parsed.query)
            clean_qs = {k: v for k, v in qs.items() if not k.startswith('utm_') and k not in {'ref', 'fbclid', 'gclid'}}
            query_string = urlencode(clean_qs, doseq=True)
            return urlunparse(parsed._replace(query=query_string))
        except:
            return url

    def _is_trash(self, title: str, content: str, url: str) -> bool:
        from urllib.parse import urlparse
        try:
            domain = urlparse(url).netloc.lower()
        except:
            domain = ""
        
        # 1. Blacklist de domínios
        for black in self.BLACKLIST_DOMAINS:
            if black in domain: return True
        
        # 2. Blacklist de keywords no conteúdo
        text = f"{title} {content}".lower()
        for kw in self.BLACKLIST_KEYWORDS:
            if kw in text: return True
            
        # 3. URLs técnicas óbvias
        if domain.endswith(".js") or "/ads/" in url or "ad_domain" in url:
            return True
            
        return False

    def _is_relevant(self, query: str, title: str, snippet: str) -> bool:
        """
        Heurística de relevância semântica:
        Verifica se termos importantes da query aparecem no resultado.
        """
        query_terms = [t.lower() for t in query.split() if len(t) > 3]
        if not query_terms: return True # Query muito curta, aceita qualquer coisa qualificada
        
        text = f"{title} {snippet}".lower()
        matches = [t for t in query_terms if t in text]
        
        # Exige que ao menos 30% dos termos significativos estejam presentes
        return len(matches) / len(query_terms) >= 0.3


