# Jarvis/core/policy.py

from enum import Enum
from dataclasses import dataclass
from typing import Optional

from Jarvis.core.action_request import ActionRequest
from Jarvis.core.intent import IntentType


class PolicyResult(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_DEV_MODE = "require_dev_mode"


@dataclass
class PolicyDecision:
    result: PolicyResult
    reason: Optional[str] = None


class PolicyEngine:
    """
    PolicyEngine verifica se uma intenção ou ação é permitida
    dado o estado atual do Context (dev_mode, offline, llm availability).
    """

    def __init__(self, context):
        self.context = context

    # ====================================
    # INTENT POLICY (ALTO NÍVEL — ANTES DE ROUTER)
    # ====================================
    def evaluate_intent(self, intent) -> PolicyDecision:
        """
        Valida intenção antes do roteamento.
        - Dev commands permitidos conforme flags
        - Intenções sensíveis offline/sem LLM são negadas
        """

        # Dev mode e comandos internos
        if intent.type == IntentType.DEV_ENTER or intent.type == IntentType.DEV_EXIT:
            return PolicyDecision(PolicyResult.ALLOW)

        if intent.type.name.startswith("DEV_"):
            # Comandos reservados para dev mode
            if not self.context.dev_mode:
                return PolicyDecision(
                    PolicyResult.REQUIRE_DEV_MODE,
                    reason="Intenção restrita ao modo desenvolvedor."
                )
            return PolicyDecision(PolicyResult.ALLOW)

        # Se offline, proibir web fetch
        if getattr(self.context, "offline", False):
            if intent.type == IntentType.WEB_FETCH:
                return PolicyDecision(
                    PolicyResult.DENY,
                    reason="Consulta web proibida em modo offline."
                )

        # Se LLM não disponível, evitar intents que dependem dele
        if not self.context.llm_available:
            # Chat/help fallback deve ser tratado no Router/Executor
            if intent.type in (
                IntentType.CHAT,
                IntentType.HELP,
            ):
                return PolicyDecision(
                    PolicyResult.DENY,
                    reason="LLM indisponível para esse tipo de consulta."
                )

        # Intenção padrão permitida
        return PolicyDecision(PolicyResult.ALLOW)

    # ====================================
    # ACTION POLICY (BAIXO NÍVEL — APÓS ACTION_REQUEST)
    # ====================================
    def evaluate_action(self, action: ActionRequest) -> PolicyDecision:
        """
        Avalia um ActionRequest para permitir/negociar sua execução.
        - Ações de alto risco exigem dev_mode
        - Outras podem ser permitidas
        """

        # Se for ação sensível à estrutura do sistema
        # Exemplo: deletar algo
        if action.risk == "high":
            if not self.context.dev_mode:
                return PolicyDecision(
                    PolicyResult.REQUIRE_DEV_MODE,
                    reason="Ação de risco elevado requer modo desenvolvedor."
                )

        # Exemplo específico de exclusão de arquivos
        if action.action.startswith("filesystem.delete"):
            if not self.context.dev_mode:
                return PolicyDecision(
                    PolicyResult.DENY,
                    reason="Exclusão de arquivos proibida fora do modo desenvolvedor."
                )

        # Outros: permitir por padrão
        return PolicyDecision(PolicyResult.ALLOW)
