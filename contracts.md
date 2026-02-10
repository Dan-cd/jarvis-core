## PASSO 2 — CONTRACTS.md (schemas e garantias)

### Contrato de Intenção (Router → Executor)

```json
{
  "intent": "help | dev | plugin | sandbox | other",
  "confidence": 0.0,
  "requires_confirmation": true
}
```

### Contrato de Plugin (Executor → Plugin)

```json
{
  "input": {},
  "scope": "read | write | external",
  "allowed": true
}
```

### Retorno Padrão de Plugin

```json
{
  "data": {},
  "source": "plugin_name",
  "confidence": 0.0,
  "errors": []
}
```

### Contrato de Resposta (AnswerPipeline)

Toda resposta **DEVE** conter:

* **Origem**: sistema / plugin / conhecimento interno
* **Confiança**: explícita (0–1)
* **Limitações**: o que não foi possível fazer

Se qualquer campo faltar → **fallback honesto**.

---
