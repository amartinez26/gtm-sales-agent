# 🤖 GTM Sales Agent: Strategic RAG Pipeline

An AI-powered Go-To-Market (GTM) Sales Agent that analyzes corporate strategy documents to generate high-impact, customer-facing sales pitches. This project implements a **Retrieval-Augmented Generation (RAG)** architecture using LangChain and Google Gemini 3 Flash.

**Built by:** [Antonio Martinez](https://github.com/amartinez26)

---

## 🏗️ Architecture Overview

The system is built with a decoupled microservices-style architecture to ensure environment stability and rapid frontend iteration.

* **LLM:** Gemini 3 Flash (optimized for speed and strategic reasoning).
* **Orchestration:** LangChain (LCEL) for robust RAG chain management.
* **Vector Store:** ChromaDB for local persistence of strategy embeddings.
* **Backend:** FastAPI containerized with Docker to standardize the AI environment.
* **Frontend:** Streamlit dashboard for real-time user interaction.

---

## 🚀 Getting Started

### 1. Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
* Python 3.10+ installed locally.
* A [Google Gemini API Key](https://aistudio.google.com/app/apikey).

### 2. Configure Environment
Create a `.env` file in the root directory. This file is ignored by Git for security:
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
PITCH_KEY=answer
```

### 3. Install Local Dependencies
The frontend and data ingestion scripts run locally to allow for "hot-reloading" and faster development.
```powershell
pip install -r requirements.txt
```

### 4. Initialize the Vector Database
Before launching, you must ingest the raw strategy documents (e.g., STIHL 2027 Strategy) into the ChromaDB vector store:
```powershell
python ingest.py
```

### 5. Build and Launch Backend (Docker)
The backend manages the LangChain logic and API endpoints. Using the `--no-cache` flag ensures your latest `config.py` changes are captured.
```powershell
docker build --no-cache -t gtm-sales-agent .
docker run -p 8000:8000 --env-file .env -e PYTHONUNBUFFERED=1 gtm-sales-agent
```

### 6. Launch the Frontend Dashboard
In a new terminal window, start the Streamlit UI:
```powershell
streamlit run frontend/app_ui.py
```
*Access the dashboard at:* `http://localhost:8501`

---

## 🧪 Evaluation & Quality Assurance

To ensure accuracy and prevent AI hallucinations, this project includes an automated testing suite:
```powershell
python evaluator.py
```
**The Evaluator provides:**
* **Keyword Validation:** Verifies the AI mentioned specific strategic pillars (e.g., "35% battery share").
* **Contract Sync:** Uses the centralized `PITCH_KEY` to ensure JSON responses are consistent across the stack.
* **Logs:** Generates `eval_results.json` for regression testing.

---

## 🛠️ Design Decisions & Lessons Learned

* **Unified API Contract:** Implemented a centralized `config.py` to share keys between the Dockerized FastAPI backend and the local Streamlit frontend, eliminating "naming mismatch" bugs.
* **Decoupled Workflows:** Separated data ingestion from the application runtime to avoid redundant processing of PDFs on every startup.
* **Containerization:** Dockerized the core AI engine to ensure the `sentence-transformers` and `langchain` dependencies run identically on any machine.

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.