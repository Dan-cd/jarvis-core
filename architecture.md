# Jarvis — Contratos Fundamentais (v6.5)

> **Objetivo**: congelar comportamento, autoridade e limites do sistema. Este documento é a **fonte de verdade** para qualquer humano ou IA que interaja com o Jarvis.

---

## PASSO 1 — ARCHITECTURE.md (quem manda em quem)

### Identidade do Sistema

* **Jarvis é um sistema arquitetural**.
* **LLMs são ferramentas**, nunca o núcleo decisório.
* Toda ação nasce de uma **decisão explícita do sistema**.

### Fluxo Oficial (imutável)

```
Input → Router → Executor → (Plugins) → AnswerPipeline → Output
```

### Responsabilidades (contrato)

* **Router**: classifica intenção. **Nunca responde conteúdo**.
* **Executor**: executa ações decididas. **Nunca inventa ações**.
* **Plugins**: executam capacidades isoladas. **Nunca decidem**.
* **AnswerPipeline**: formata resposta com **origem, confiança e limites**.
* **LLM**: gera texto sob comando. **Nunca decide nem finge capacidades**.

### Regras Invioláveis

* LLM **não**:

  * decide ações
  * acessa web diretamente
  * afirma fontes externas
  * fala sobre treinamento
* Plugins **não**:

  * chamam outros plugins
  * acessam memória diretamente
* Apenas o **WebPlugin** acessa recursos externos.

---

A v6.5 só está concluída se:

* [ ] Nenhuma resposta ignora o Router
* [ ] Dev Mode não vaza
* [ ] Plugins respeitam contrato
* [ ] AnswerPipeline sempre explica origem
* [ ] LLM nunca finge capacidade
* [ ] Sandbox é isolada

---

## Cláusula Final

> **Se um comportamento não estiver documentado aqui, ele é proibido.**

## Fluxo Principal do Sistema (obrigatório para agentes)

1. Todo input do usuário entra pelo Router
2. O Router classifica a intenção (não responde)
3. O Executor executa ações permitidas
4. Plugins só rodam se chamados pelo Executor
5. O AnswerPipeline constrói a resposta final
6. O LLM apenas gera texto sob comando

⚠️ Nenhum atalho é permitido.

## Fluxos Proibidos

- Input → LLM → Output
- Plugin → Plugin
- LLM → Plugin
- Sandbox → Memória
- Dev Mode implícito
