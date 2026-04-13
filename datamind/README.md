# 🧠 DataMind — Autonomous Data Analysis Agent

DataMind is a Streamlit web application that lets you upload a CSV file and ask questions about your data in plain English. A local LLM (powered by [Ollama](https://ollama.com)) autonomously plans analysis steps, generates Python code, executes it in a sandbox, self-corrects on errors, and returns charts alongside plain-English insights — no coding required.

---

## Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.10+ |
| [Ollama](https://ollama.com) | Latest (installed & running) |

## Quick Start

```bash
# 1. Clone the repository
git clone <repo-url> && cd datamind

# 2. Create a virtual environment & install dependencies
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. Copy the environment config
cp .env.example .env

# 4. Pull an LLM model via Ollama
ollama pull qwen3-coder   # or: ollama pull llama3

# 5. Make sure Ollama is running
ollama serve   # (in a separate terminal)

# 6. Launch DataMind
streamlit run app.py
```

The app will open at **http://localhost:8501**.

---

## Screenshots

> _Screenshots will be added after the first release._

---

## How It Works

```
┌──────────────────────────────────────────────────┐
│  1. Upload CSV → validate, profile, detect types │
│  2. Ask a question in plain English              │
│  3. Planner (LLM) → 3-6 analysis steps (JSON)   │
│  4. For each step:                               │
│     a. Code Generator (LLM) → Python code        │
│     b. Executor → sandboxed exec()               │
│     c. Reflector → retry on failure (max 2×)     │
│  5. Explainer (LLM) → plain-English insight      │
│  6. UI renders plan, code, charts, & insights    │
└──────────────────────────────────────────────────┘
```

### Pipeline Components

| Module | Role |
|---|---|
| `llm/ollama_client.py` | Ollama API wrapper with retry + streaming |
| `agent/planner.py` | LLM generates a step-by-step analysis plan |
| `agent/code_generator.py` | LLM writes executable Python per step |
| `agent/executor.py` | Sandboxed `exec()` with stdout & figure capture |
| `agent/reflector.py` | Validates results, retries with error context |
| `agent/explainer.py` | LLM summarises findings in plain English |
| `agent/controller.py` | Orchestrates the full pipeline |
| `ui/` | Streamlit UI components (sidebar, panels) |

---

## Configuration

All settings are managed via the `.env` file:

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_MODEL` | `qwen3-coder` | Default Ollama model |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `MAX_RETRIES` | `2` | Max retries on failed code execution |
| `EXECUTION_TIMEOUT` | `30` | Timeout per code execution (seconds) |
| `MAX_PLAN_STEPS` | `6` | Maximum analysis steps in a plan |
| `DEBUG` | `false` | Enable verbose logging |

---

## Folder Structure

```
datamind/
├── app.py                    # Streamlit entry point
├── requirements.txt
├── .env.example
├── README.md
│
├── agent/
│   ├── __init__.py
│   ├── controller.py         # Pipeline orchestrator
│   ├── planner.py            # LLM → step-by-step plan
│   ├── code_generator.py     # LLM → Python code per step
│   ├── executor.py           # Sandboxed exec() runner
│   ├── reflector.py          # Error handling & retries
│   └── explainer.py          # LLM → plain-English insights
│
├── llm/
│   ├── __init__.py
│   └── ollama_client.py      # Ollama API client
│
├── utils/
│   ├── __init__.py
│   ├── data_utils.py         # CSV loading & profiling
│   └── chart_utils.py        # Figure capture utilities
│
└── ui/
    ├── __init__.py
    ├── sidebar.py            # Upload + query components
    ├── reasoning_panel.py    # Plan display
    └── results_panel.py      # Charts + insights display
```

---

## Limitations & Known Issues

- **Local LLM only**: Requires Ollama running locally. Cloud LLM providers are not currently supported.
- **CSV only**: Other file formats (Excel, Parquet, JSON) are not yet supported.
- **Sandbox limitations**: The executor blocks dangerous builtins but uses `exec()` — not a true security sandbox. Do not use with untrusted data/models in production.
- **Model quality**: Output quality depends heavily on the chosen LLM. Larger models (e.g., `llama3:70b`) produce better results but require more resources.
- **No persistent storage**: Analysis results are stored in session state only and are lost on page refresh.
- **Single DataFrame**: Only one CSV can be analysed at a time; multi-file joins are not supported.

---

## License

MIT
