from Jarvis.core.decision import DecisionOutcome, DecisionPath
from Jarvis.core.action_request import ActionRequest
from Jarvis.core.params_resolver import ParamsResolver
from Jarvis.core.intent import IntentType
from Jarvis.core.policy import PolicyEngine
from Jarvis.core.policy import PolicyResult
from Jarvis.core.action_plan import ActionPlan
from Jarvis.plugins_available.filesystem.utils import ui as fs_ui
from Jarvis.core.action_result import ActionResult
from pathlib import Path


class Executor:
    def __init__(
        self,
        llm,
        fallback,
        sandbox,
        memory,
        context,
        answer_pipeline,
        dev_guard
    ):
        self.llm = llm
        self.fallback = fallback
        self.sandbox = sandbox
        self.memory = memory
        self.context = context
        self.answer_pipeline = answer_pipeline
        self.dev_guard = dev_guard

    def execute(self, decision, user_input: str) -> str:

        if decision.outcome == DecisionOutcome.REQUIRE_DEV_MODE:
            if self.dev_guard.is_blocked():
                return "Dev Mode temporariamente bloqueado."

            attempt = input("Senha do Dev Mode: ")
            if self.dev_guard.validate(attempt):
                self.context.dev_mode = True
                return "Modo desenvolvedor ativado."

            return "Senha incorreta."

        if decision.outcome == DecisionOutcome.DENY:
            return decision.reason or "Operação negada."

        # DECISÃO FINAL SEM PATH (ex: dev.exit)
        if decision.path is None:
            return decision.reason or "OK."

        if decision.path == DecisionPath.LLM:
            return self.answer_pipeline.respond(
                user_input=user_input,
                context=self.context
            )

        if decision.path == DecisionPath.FALLBACK:
            return self.fallback.respond(user_input)

        if decision.path == DecisionPath.LOCAL:
            return self._execute_local(decision)

        if decision.path == DecisionPath.PLUGIN:
            return self._execute_plugin(decision)

        return "Caminho não reconhecido."

    def _execute_plugin(self, decision) -> str:
        intent = decision.payload["intent"]

        resolver = ParamsResolver()
        params = resolver.resolve(intent.type, intent.raw)

        action = ActionRequest(
            intent=intent,
            params=params,
            context=self.context
        )

        plugin_info = decision.payload["plugin"]
        plugin_cls = plugin_info["plugin"]
        plugin = plugin_cls()

        plugin_metadata = getattr(plugin, "metadata", {}) or {}
        action.action = plugin_info.get("action") or plugin_metadata.get("name")
        action.risk = plugin_info.get("risk") or plugin_metadata.get("risk_level", "low")
        action.metadata = plugin_info.get("metadata") or plugin_metadata
        # DRY-RUN
        plan = plugin.execute(action, dry_run=True)

        if isinstance(plan, ActionPlan):
            # Policy check
            policy = PolicyEngine(self.context)
            decision_policy = policy.evaluate_action(action, self.context.dev_mode)

            if decision_policy.result != PolicyResult.ALLOW:
                return decision_policy.reason or "Ação bloqueada pela política."

            # SELEÇÃO INTERATIVA (quando houver múltiplos targets)
            selected = plan.targets
            if len(plan.targets) > 1:
                chosen = fs_ui.select_targets_interactive(plan.targets)
                if not chosen:
                    return "Ação cancelada pelo usuário."
                selected = chosen

            # PREVIEW específico por tipo de ação
            if plan.action == "filesystem.delete":
                fs_ui.preview_delete(selected)
            elif plan.action == "filesystem.move":
                # para move o executor tem que saber o destino — tentamos recuperá-lo do params
                dest_name = action.params.get("target") or action.params.get("destination")
                # se dest_name for relativo, montar preview usando o primeiro selected
                if dest_name:
                    dest = (selected[0].parent / dest_name) if selected else Path(dest_name)
                else:
                    dest = None
                for s in selected:
                    fs_ui.preview_move(s, dest or Path("<destino indefinido>"))
            elif plan.action == "filesystem.write":
                # mostra diff para o primeiro arquivo como amostra
                content = action.params.get("content", "")
                fs_ui.preview_write(selected[0], content)

            # Confirmação final
            confirm = fs_ui.confirm_prompt(plan.description + "\nConfirmar execução?")
            if not confirm:
                return "Ação cancelada pelo usuário."

            # EXECUTAR por target, agregando resultados
            results = []
            for tgt in selected:
                # criar sub-action com filename absoluto para evitar nova ambiguidade
                sub_params = dict(action.params)
                sub_params["filename"] = str(tgt)
                sub_action = ActionRequest(intent=action.intent, params=sub_params, context=self.context)

                result = plugin.execute(sub_action, dry_run=False)
                results.append(result)

            # Agregar mensagens
            messages = []
            for r in results:
                if isinstance(r, ActionResult):
                    messages.append(r.message)
                else:
                    # fallback case: se o plugin retornar texto cru
                    messages.append(str(r))

            return "\n".join(messages)

        # Ações não destrutivas (sem ActionPlan)
        result = plugin.execute(action, dry_run=False)
        if isinstance(result, ActionResult):
            return result.message
        return str(result)

    def _execute_local(self, decision) -> str:
        intent = decision.payload["intent"]

        # MEMORY WRITE
        if intent.type == IntentType.MEMORY_WRITE:
            success = self.memory.remember(intent.raw)

            if success:
                return "Memória registrada com sucesso."
            else:
                return "Não encontrei nenhuma informação clara para salvar na memória."

        # MEMORY READ
        if intent.type == IntentType.MEMORY_READ:
            memories = self.memory.recall()

            if not memories:
                return "Não há memórias registradas."

            lines = []
            for m in memories:
                lines.append(f"- ({m.type.value}) {m.content}")

            return "Memórias registradas:\n" + "\n".join(lines)

        return "Ação local não reconhecida."