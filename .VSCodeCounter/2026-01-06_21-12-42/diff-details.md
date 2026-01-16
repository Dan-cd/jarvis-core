# Diff Details

Date : 2026-01-06 21:12:42

Directory /home/danvic/JARVIS/Jarvis

Total : 40 files,  781 codes, 80 comments, 262 blanks, all 1123 lines

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [Jarvis/\_\_init\_\_.py](/Jarvis/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [Jarvis/data/dev\_mode\_state.json](/Jarvis/data/dev_mode_state.json) | JSON | 1 | 0 | 0 | 1 |
| [Jarvis/data/logs/error.log](/Jarvis/data/logs/error.log) | Log | 0 | 0 | 1 | 1 |
| [Jarvis/data/memory.json](/Jarvis/data/memory.json) | JSON | 10 | 0 | 0 | 10 |
| [Jarvis/data/memory/short\_term.json](/Jarvis/data/memory/short_term.json) | JSON | 0 | 0 | 1 | 1 |
| [Jarvis/dev/\_\_init\_\_.py](/Jarvis/dev/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [Jarvis/dev/debug.py](/Jarvis/dev/debug.py) | Python | 0 | 0 | 1 | 1 |
| [Jarvis/dev/inspect.py](/Jarvis/dev/inspect.py) | Python | 0 | 0 | 1 | 1 |
| [Jarvis/dev/simulate.py](/Jarvis/dev/simulate.py) | Python | 8 | 0 | 1 | 9 |
| [Jarvis/main.py](/Jarvis/main.py) | Python | 59 | 1 | 16 | 76 |
| [Jarvis/modules/\_\_init\_\_.py](/Jarvis/modules/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [Jarvis/modules/llm/\_\_init\_\_.py](/Jarvis/modules/llm/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [Jarvis/modules/llm/base.py](/Jarvis/modules/llm/base.py) | Python | 5 | 0 | 2 | 7 |
| [Jarvis/modules/llm/groq.py](/Jarvis/modules/llm/groq.py) | Python | 26 | 0 | 5 | 31 |
| [Jarvis/modules/llm/ollama.py](/Jarvis/modules/llm/ollama.py) | Python | 12 | 0 | 6 | 18 |
| [Jarvis/plugins/\_\_init\_\_.py](/Jarvis/plugins/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [Jarvis/plugins/base.py](/Jarvis/plugins/base.py) | Python | 13 | 0 | 4 | 17 |
| [Jarvis/plugins/loader.py](/Jarvis/plugins/loader.py) | Python | 18 | 0 | 5 | 23 |
| [Jarvis/plugins/registry.py](/Jarvis/plugins/registry.py) | Python | 14 | 0 | 3 | 17 |
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
| [Jarvis/plugins\_available/web/models.py](/Jarvis/plugins_available/web/models.py) | Python | 0 | 0 | 1 | 1 |
| [Jarvis/plugins\_available/web/plugin.py](/Jarvis/plugins_available/web/plugin.py) | Python | 0 | 0 | 1 | 1 |
| [Jarvis/plugins\_available/web\_search.py](/Jarvis/plugins_available/web_search.py) | Python | 18 | 0 | 7 | 25 |
| [Jarvis/safe/\_\_init\_\_.py](/Jarvis/safe/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [Jarvis/safe/safe\_execution.py](/Jarvis/safe/safe_execution.py) | Python | 21 | 0 | 3 | 24 |
| [Jarvis/sandbox/\_\_init\_\_.py](/Jarvis/sandbox/__init__.py) | Python | 1 | 0 | 1 | 2 |
| [Jarvis/sandbox/handler.py](/Jarvis/sandbox/handler.py) | Python | 26 | 0 | 12 | 38 |

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details