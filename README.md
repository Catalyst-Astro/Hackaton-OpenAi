# 🧠 GPT-OSS Redteaming Toolkit

Este repositorio contiene un sistema modular automatizado para identificar, clasificar y documentar fallos de seguridad en modelos LLM, específicamente para el hackathon de OpenAI sobre `gpt-oss-20b`.

## 🎯 Objetivo

Detectar exploits reproducibles en categorías como:
- Reward Hacking
- Deception
- Sandbagging
- Sabotage
- Tool Misuse
- Data Exfiltration
- Evaluation Awareness

## ⚙️ Estructura

```
gpt-oss-redteaming/
├── main_codex_controller.py      # Orquestador CLI
├── prompts/                      # Generación y mutación de prompts
├── engine/                       # Ejecución, análisis, clasificación
├── report/                       # Generación de findings para Kaggle
├── data/                         # Prompts, salidas, análisis, hallazgos
├── notebooks/                    # Exploración visual y reproducción
└── docs/                         # Documentación del proyecto
```

## 🚀 Uso rápido

1. Generar prompts:
```bash
python main_codex_controller.py generate_prompts --domain law --samples 100
```

2. Mutarlos:
```bash
python main_codex_controller.py mutate_prompts --input data/prompts/law.json
```

3. Ejecutar contra el modelo:
```bash
python main_codex_controller.py run_model --input data/prompts/law_mutated.json
```

4. Analizar y clasificar:
```bash
python main_codex_controller.py analyze_outputs --input data/outputs/law_results.json
python main_codex_controller.py classify_failures --input data/analyzed/law_analyzed.json --output data/findings/law_findings.json
```

5. Empaquetar findings para envío:
```bash
python main_codex_controller.py generate_report
```

## 📂 Requisitos

- Python 3.10+
- `pip install -r requirements.txt`
- Modelo `gpt-oss-20b` sirviendo vía `vLLM` en `localhost:8000`

## 📑 Licencia

Apache-2.0
