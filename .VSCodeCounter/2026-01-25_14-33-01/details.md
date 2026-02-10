# Details

Date : 2026-01-25 14:33:01

Directory /home/danvic/JARVIS/Jarvis

Total : 74 files,  2213 codes, 442 comments, 698 blanks, all 3353 lines

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [Jarvis/\_\_init\_\_.py](/Jarvis/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [Jarvis/core/LLMManager.py](/Jarvis/core/LLMManager.py) | Python | 43 | 14 | 14 | 71 |
| [Jarvis/core/\_\_init\_\_.py](/Jarvis/core/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [Jarvis/core/action\_plan.py](/Jarvis/core/action_plan.py) | Python | 8 | 0 | 1 | 9 |
| [Jarvis/core/action\_request.py](/Jarvis/core/action_request.py) | Python | 11 | 0 | 1 | 12 |
| [Jarvis/core/action\_result.py](/Jarvis/core/action_result.py) | Python | 19 | 4 | 8 | 31 |
| [Jarvis/core/answer.py](/Jarvis/core/answer.py) | Python | 10 | 0 | 3 | 13 |
| [Jarvis/core/answer\_pipeline.py](/Jarvis/core/answer_pipeline.py) | Python | 93 | 34 | 31 | 158 |
| [Jarvis/core/bootstrap.py](/Jarvis/core/bootstrap.py) | Python | 11 | 0 | 3 | 14 |
| [Jarvis/core/config.py](/Jarvis/core/config.py) | Python | 37 | 26 | 15 | 78 |
| [Jarvis/core/context.py](/Jarvis/core/context.py) | Python | 23 | 11 | 12 | 46 |
| [Jarvis/core/decision.py](/Jarvis/core/decision.py) | Python | 33 | 0 | 7 | 40 |
| [Jarvis/core/dev\_mode.py](/Jarvis/core/dev_mode.py) | Python | 17 | 0 | 7 | 24 |
| [Jarvis/core/dev\_mode\_guard.py](/Jarvis/core/dev_mode_guard.py) | Python | 45 | 0 | 11 | 56 |
| [Jarvis/core/errors.py](/Jarvis/core/errors.py) | Python | 82 | 44 | 41 | 167 |
| [Jarvis/core/executor.py](/Jarvis/core/executor.py) | Python | 115 | 57 | 39 | 211 |
| [Jarvis/core/intent.py](/Jarvis/core/intent.py) | Python | 56 | 11 | 13 | 80 |
| [Jarvis/core/llm\_contract.py](/Jarvis/core/llm_contract.py) | Python | 25 | 0 | 9 | 34 |
| [Jarvis/core/logger.py](/Jarvis/core/logger.py) | Python | 14 | 0 | 1 | 15 |
| [Jarvis/core/main.py](/Jarvis/core/main.py) | Python | 63 | 12 | 20 | 95 |
| [Jarvis/core/memory.py](/Jarvis/core/memory.py) | Python | 42 | 0 | 11 | 53 |
| [Jarvis/core/memory/\_\_init\_\_.py](/Jarvis/core/memory/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [Jarvis/core/memory/execution\_memory.py](/Jarvis/core/memory/execution_memory.py) | Python | 16 | 13 | 8 | 37 |
| [Jarvis/core/memory/manager.py](/Jarvis/core/memory/manager.py) | Python | 25 | 0 | 7 | 32 |
| [Jarvis/core/memory/models.py](/Jarvis/core/memory/models.py) | Python | 32 | 0 | 5 | 37 |
| [Jarvis/core/memory/parser.py](/Jarvis/core/memory/parser.py) | Python | 29 | 5 | 9 | 43 |
| [Jarvis/core/memory/policies.py](/Jarvis/core/memory/policies.py) | Python | 4 | 0 | 0 | 4 |
| [Jarvis/core/memory/store.py](/Jarvis/core/memory/store.py) | Python | 49 | 0 | 7 | 56 |
| [Jarvis/core/memory/temp\_memory.py](/Jarvis/core/memory/temp_memory.py) | Python | 37 | 19 | 12 | 68 |
| [Jarvis/core/output\_formatter.py](/Jarvis/core/output_formatter.py) | Python | 7 | 0 | 2 | 9 |
| [Jarvis/core/params\_resolver.py](/Jarvis/core/params_resolver.py) | Python | 85 | 10 | 39 | 134 |
| [Jarvis/core/policy.py](/Jarvis/core/policy.py) | Python | 56 | 31 | 20 | 107 |
| [Jarvis/core/router.py](/Jarvis/core/router.py) | Python | 57 | 6 | 14 | 77 |
| [Jarvis/core/router\_result.py](/Jarvis/core/router_result.py) | Python | 5 | 0 | 1 | 6 |
| [Jarvis/core/types.py](/Jarvis/core/types.py) | Python | 5 | 0 | 1 | 6 |
| [Jarvis/data/dev\_mode\_state.json](/Jarvis/data/dev_mode_state.json) | JSON | 1 | 0 | 0 | 1 |
| [Jarvis/data/memory.json](/Jarvis/data/memory.json) | JSON | 18 | 0 | 0 | 18 |
| [Jarvis/data/memory/short\_term.json](/Jarvis/data/memory/short_term.json) | JSON | 0 | 0 | 1 | 1 |
| [Jarvis/dev/\_\_init\_\_.py](/Jarvis/dev/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [Jarvis/dev/debug.py](/Jarvis/dev/debug.py) | Python | 0 | 0 | 1 | 1 |
| [Jarvis/dev/inspect.py](/Jarvis/dev/inspect.py) | Python | 0 | 0 | 1 | 1 |
| [Jarvis/dev/simulate.py](/Jarvis/dev/simulate.py) | Python | 8 | 0 | 1 | 9 |
| [Jarvis/main.py](/Jarvis/main.py) | Python | 57 | 10 | 16 | 83 |
| [Jarvis/modules/\_\_init\_\_.py](/Jarvis/modules/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [Jarvis/modules/llm/\_\_init\_\_.py](/Jarvis/modules/llm/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [Jarvis/modules/llm/base.py](/Jarvis/modules/llm/base.py) | Python | 16 | 0 | 7 | 23 |
| [Jarvis/modules/llm/groq.py](/Jarvis/modules/llm/groq.py) | Python | 48 | 4 | 14 | 66 |
| [Jarvis/modules/llm/ollama.py](/Jarvis/modules/llm/ollama.py) | Python | 34 | 3 | 10 | 47 |
| [Jarvis/plugins/\_\_init\_\_.py](/Jarvis/plugins/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [Jarvis/plugins/base.py](/Jarvis/plugins/base.py) | Python | 14 | 0 | 2 | 16 |
| [Jarvis/plugins/loader.py](/Jarvis/plugins/loader.py) | Python | 23 | 0 | 11 | 34 |
| [Jarvis/plugins/registry.py](/Jarvis/plugins/registry.py) | Python | 12 | 19 | 8 | 39 |
| [Jarvis/plugins\_available/\_\_init\_\_.py](/Jarvis/plugins_available/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [Jarvis/plugins\_available/domain\_check.py](/Jarvis/plugins_available/domain_check.py) | Python | 0 | 0 | 1 | 1 |
| [Jarvis/plugins\_available/filesystem/\_\_init\_\_.py](/Jarvis/plugins_available/filesystem/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [Jarvis/plugins\_available/filesystem/filesystem\_delete.py](/Jarvis/plugins_available/filesystem/filesystem_delete.py) | Python | 57 | 6 | 16 | 79 |
| [Jarvis/plugins\_available/filesystem/filesystem\_edit.py](/Jarvis/plugins_available/filesystem/filesystem_edit.py) | Python | 51 | 3 | 16 | 70 |
| [Jarvis/plugins\_available/filesystem/filesystem\_move.py](/Jarvis/plugins_available/filesystem/filesystem_move.py) | Python | 52 | 5 | 16 | 73 |
| [Jarvis/plugins\_available/filesystem/filesystem\_pdf\_read.py](/Jarvis/plugins_available/filesystem/filesystem_pdf_read.py) | Python | 81 | 8 | 29 | 118 |
| [Jarvis/plugins\_available/filesystem/filesystem\_read.py](/Jarvis/plugins_available/filesystem/filesystem_read.py) | Python | 49 | 3 | 17 | 69 |
| [Jarvis/plugins\_available/filesystem/filesystem\_write.py](/Jarvis/plugins_available/filesystem/filesystem_write.py) | Python | 38 | 4 | 13 | 55 |
| [Jarvis/plugins\_available/filesystem/utils/pdf\_ocr.py](/Jarvis/plugins_available/filesystem/utils/pdf_ocr.py) | Python | 20 | 7 | 7 | 34 |
| [Jarvis/plugins\_available/filesystem/utils/pdf\_summary.py](/Jarvis/plugins_available/filesystem/utils/pdf_summary.py) | Python | 31 | 8 | 9 | 48 |
| [Jarvis/plugins\_available/filesystem/utils/resolver.py](/Jarvis/plugins_available/filesystem/utils/resolver.py) | Python | 66 | 4 | 23 | 93 |
| [Jarvis/plugins\_available/filesystem/utils/text\_summary.py](/Jarvis/plugins_available/filesystem/utils/text_summary.py) | Python | 19 | 10 | 12 | 41 |
| [Jarvis/plugins\_available/filesystem/utils/ui.py](/Jarvis/plugins_available/filesystem/utils/ui.py) | Python | 85 | 21 | 24 | 130 |
| [Jarvis/plugins\_available/web/models.py](/Jarvis/plugins_available/web/models.py) | Python | 13 | 0 | 5 | 18 |
| [Jarvis/plugins\_available/web/plugin.py](/Jarvis/plugins_available/web/plugin.py) | Python | 174 | 28 | 24 | 226 |
| [Jarvis/plugins\_available/web/web\_cache.py](/Jarvis/plugins_available/web/web_cache.py) | Python | 28 | 1 | 9 | 38 |
| [Jarvis/plugins\_available/web\_search.py](/Jarvis/plugins_available/web_search.py) | Python | 18 | 0 | 7 | 25 |
| [Jarvis/safe/\_\_init\_\_.py](/Jarvis/safe/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [Jarvis/safe/safe\_execution.py](/Jarvis/safe/safe_execution.py) | Python | 19 | 1 | 3 | 23 |
| [Jarvis/sandbox/\_\_init\_\_.py](/Jarvis/sandbox/__init__.py) | Python | 1 | 0 | 1 | 2 |
| [Jarvis/sandbox/handler.py](/Jarvis/sandbox/handler.py) | Python | 26 | 0 | 12 | 38 |

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)