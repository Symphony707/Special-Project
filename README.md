# DataMind SaaS

## Overview
DataMind SaaS is a forensic intelligence platform that provides deep dataset profiling, interactive visual analytics, and strategic forecasting. Designed for analysts and executives, it combines automated machine learning with robust language models to turn raw data into strategic narratives.

## Tech Stack
| Layer | Technology |
|---|---|
| **Frontend** | Streamlit, Plotly |
| **Backend** | Python, Scikit-Learn, Pandas |
| **Database** | SQLite, bcrypt |
| **LLM Engine** | Ollama (Qwen 2.5 Coder) |

## Setup
### Prerequisites
- Python 3.10+
- Ollama installed and running
- Model pulled: `ollama pull qwen2.5-coder:7b`

### Installation
```bash
git clone <repo>
cd <project>
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your values
streamlit run app.py
```

## Environment Variables
See `.env.example` for required variables. Note: Never commit `.env` to version control.

## Project Structure
```text
Special Project/
├── .streamlit/
│   └── config.toml
├── assets/
│   └── logo.jpg
├── data/
│   ├── uploads/
│   └── datamind.db
├── datamind/
│   ├── agent/       # Autonomous analytical agents
│   ├── auth/        # Multi-tenant security
│   ├── llm/         # Inference engine connectors
│   ├── memory/      # Session and caching frameworks
│   ├── tools/       # Data ingestion and profiling
│   ├── ui/          # Streamlit views and layouts
│   └── utils/       # Global helpers
├── .env.example
├── .gitignore
├── app.py
├── config.py
├── database.py
├── pyrightconfig.json
├── README.md
└── requirements.txt
```

## Features
- **Forensic Dataset Profiling**: Instant recognition of missing values, anomalies, and statistics across datasets.
- **Narrative Reporting**: Autonomous agents provide executive-level breakdown and strategic implications of data patterns.
- **Predictive Forecasting**: Apply continuous modeling and simulations for what-if scenarios.
- **Interactive Dashboards**: Seamless chart generation via natural language without coding.
- **Multi-Tenant Memory**: Persistent session histories and deduplicated file asset ingestion with PII scrubbing. 

## License
Proprietary
