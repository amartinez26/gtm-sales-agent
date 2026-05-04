# 🤖 GTM Sales Agent: Strategic RAG Pipeline

An AI-powered Go-To-Market (GTM) Sales Agent that analyzes private strategy documents to generate high-impact, customer-facing sales pitches. Built on a **Retrieval-Augmented Generation (RAG)** architecture using LangChain and Google Gemini Flash — with live document monitoring, incremental ingestion, and security hardening against prompt injection.

**Built by:** [Antonio Martinez](https://github.com/amartinez26)

---

## 🏗️ Architecture Overview

```
Documents (local folder or SMB share)
        ↓
watchdog_service.py  — monitors folder 24/7 for new/changed/deleted files
        ↓
smart_ingest.py  — incremental ingest (only processes changed files),
                   multi-format loader, injection scanner, quarantine
        ↓
chroma_db/  — local vector database (persisted to disk)
        ↓
main.py (FastAPI on :8000)  — embedding model + RAG chain + Gemini API
        ↓
frontend/app_ui.py (Streamlit on :8501)  — user-facing dashboard
```

| Component | Technology |
|---|---|
| LLM | Google Gemini Flash |
| Orchestration | LangChain |
| Vector Store | ChromaDB |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (local, no API cost) |
| Backend API | FastAPI + Uvicorn |
| Frontend | Streamlit |
| File Monitoring | Watchdog |

---

## 📁 Project Structure

```
gtm-sales-agent/
├── main.py                 # FastAPI backend — RAG chain, hardened system prompt
├── smart_ingest.py         # Incremental multi-format ingestion + injection scanner
├── watchdog_service.py     # Live folder monitor — triggers smart_ingest on changes
├── ingest.py               # Legacy one-shot ingester (simple use cases)
├── config.py               # Shared constants (PITCH_KEY)
├── frontend/
│   └── app_ui.py           # Streamlit dashboard
├── data/
│   └── stihl_intelligence/ # Default document source folder
├── chroma_db/              # Auto-generated vector database (git-ignored)
├── quarantine/             # Auto-generated — files flagged for injection (git-ignored)
├── ingest_errors.log       # Ingest audit log
├── .env                    # Your secrets — never committed (git-ignored)
├── .env.example            # Template — copy this to .env and fill in values
├── requirements.txt
└── Dockerfile
```

---

## ✅ Prerequisites

Before starting, make sure you have the following:

| Requirement | Notes |
|---|---|
| **Python 3.10+** | [Download here](https://www.python.org/downloads/) — check with `python --version` |
| **Google Gemini API Key** | Free at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) |
| **Documents to query** | Any `.pdf`, `.docx`, `.xlsx`, `.csv`, `.txt`, `.md`, or `.pptx` files |
| **Docker Desktop** *(optional)* | Only needed for containerized backend — [download here](https://www.docker.com/products/docker-desktop/) |

---

## 🚀 Getting Started

> **New to the project? Follow these steps in order — every step is required before the next one.**

---

### Step 1 — Get a Gemini API Key

Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) and create a free API key. You'll need this in Step 2.

---

### Step 2 — Create your `.env` file

Copy the template and fill in your values:
```powershell
copy .env.example .env
```

Open `.env` and set the three variables:
```env
# Your Gemini API key from Step 1
GOOGLE_API_KEY=your_gemini_api_key_here

# Leave this as "answer" unless you have a reason to change it
PITCH_KEY=answer

# Full path to the folder containing your documents (local or SMB share)
# Examples:
#   Windows local:  C:\Users\YourName\Documents\strategy-docs
#   SMB share:      \\server\share\documents
WATCH_PATH=C:\path\to\your\documents
```

> ⚠️ `.env` is git-ignored — **never commit it.** Your API key stays on your machine only.

---

### Step 3 — Create a Virtual Environment & Install Dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

This installs all AI, backend, and frontend dependencies into an isolated environment. Takes 2–5 minutes on first run (downloading PyTorch).

---

### Step 4 — Add Your Documents

Place documents in the folder you set as `WATCH_PATH` in Step 2.

**Supported formats:** `.pdf` `.docx` `.xlsx` `.xls` `.csv` `.txt` `.md` `.pptx`

> All other file types (`.exe`, `.zip`, `.jpg`, etc.) are automatically skipped — the folder can be messy, it won't crash.

---

### Step 5 — Run the Initial Ingest

This reads all documents in `WATCH_PATH`, converts them into vectors, and saves them to `chroma_db/`. **Must be done before starting the backend.**

```powershell
.\.venv\Scripts\python.exe smart_ingest.py
```

**What to expect:**
- First run: processes every supported file (may take several minutes for large folders)
- Re-runs: only processes new or changed files — unchanged files are skipped instantly
- Check `ingest_errors.log` for a full list of what was ingested, skipped, or quarantined

Wait for the completion message:
```
=== Scan complete — new: X | modified: 0 | deleted: 0 | skipped: 0 | errors/quarantine: 0 ===
```

---

### Step 6 — Start the Backend

Open **Terminal 1** and run:
```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Wait for this line before moving on:
```
INFO:     Application startup complete. Uvicorn running on http://0.0.0.0:8000
```

> Keep this terminal open — the backend must stay running.

---

### Step 7 — Start the Live Document Watcher

Open **Terminal 2** and run:
```powershell
.\.venv\Scripts\python.exe watchdog_service.py
```

This monitors `WATCH_PATH` 24/7. Any file added, modified, or deleted is automatically ingested within ~5 seconds — no manual re-runs needed.

> This step is optional but strongly recommended. Without it, you must re-run Step 5 manually whenever documents change.

---

### Step 8 — Launch the Frontend

Open **Terminal 3** and run:
```powershell
.\.venv\Scripts\python.exe -m streamlit run frontend/app_ui.py
```

Open **[http://localhost:8501](http://localhost:8501)** in your browser and start querying your documents.

---

### Daily Startup (after first setup)

Once set up, you only need three commands across three terminals:
```powershell
# Terminal 1 — Backend
.\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000

# Terminal 2 — Watchdog
.\.venv\Scripts\python.exe watchdog_service.py

# Terminal 3 — Frontend
.\.venv\Scripts\python.exe -m streamlit run frontend/app_ui.py
```

---

## 🐳 Docker Setup (Optional)

Docker runs the backend in an isolated container. The watchdog and frontend always run locally.

**Important:** Mount `chroma_db` as a volume so the container and the local watchdog share the same database:

```powershell
# Build (run after any code changes)
docker build --no-cache -t gtm-sales-agent .

# Run — volume mount keeps chroma_db in sync with watchdog
docker run -p 8000:8000 --env-file .env -v ./chroma_db:/app/chroma_db -e PYTHONUNBUFFERED=1 gtm-sales-agent
```

Then start the watchdog and frontend locally as in steps 7 and 8 above.

> **No virtualization?** If Docker Desktop shows "Virtualization support not detected", run the backend locally (step 6) instead — no functionality is lost.

---

## 🔒 Security

### Prompt Injection Protection
The system defends against malicious files being dropped into the document folder:

| Layer | What it does |
|---|---|
| **Injection scanner** (ingest time) | Scans file content for known injection patterns before indexing |
| **Quarantine** | Flagged files are copied to `quarantine/` and not ingested — admin review required |
| **Hardened system prompt** | Instructs the LLM to ignore any instructions found in documents |
| **Output filter** | Blocks responses that show signs of successful injection |
| **Audit log** | Every file ingested, skipped, or quarantined is logged to `ingest_errors.log` |

> **Most important protection:** Restrict write access to the document folder via Windows ACL / Active Directory. If attackers cannot write files, they cannot inject.

---

## 📄 Supported File Types

| Extension | Loader |
|---|---|
| `.txt`, `.md` | TextLoader |
| `.pdf` | PyPDFLoader |
| `.docx` | Docx2txtLoader |
| `.xlsx`, `.xls` | Pandas ExcelFile |
| `.csv` | CSVLoader |
| `.pptx` | python-pptx |

---

## 🧪 Evaluation & Quality Assurance

To verify the RAG chain is returning accurate, grounded responses run:

```powershell
.\.venv\Scripts\python.exe evaluator.py
```

**What it checks:**
- **Keyword Validation** — verifies the AI mentioned expected strategic pillars in its response
- **API Contract Sync** — uses `PITCH_KEY` from `config.py` to confirm the JSON response shape matches across backend and frontend
- **Regression Logging** — writes results to `eval_results.json` so you can track answer quality over time

> Run this after changing documents or tuning `k` (number of retrieved chunks) to confirm quality hasn't regressed.

---

## 🛠️ Design Decisions

| Decision | Reason |
|---|---|
| **Incremental ingestion via manifest** | 2.5M file folders shouldn't re-process everything on every run — only changed files are touched |
| **Watchdog debounce (5s)** | Prevents a burst of rapid saves (e.g. copying 20 files at once) from triggering 20 separate ingest runs |
| **`k=5` retrieval chunks** | Balances context richness vs token cost — more chunks = better answers but higher API usage |
| **Chunk size 1000 / overlap 100** | Larger chunks preserve more context per retrieval hit; overlap prevents ideas from being split mid-sentence |
| **Local embeddings (`all-MiniLM-L6-v2`)** | No API cost per embedding, runs fully offline — only the final Gemini call uses the internet |
| **Hardened system prompt** | Documents ingested from shared/SMB folders can contain injection attempts — LLM is explicitly instructed to ignore them |
| **`chroma_db` volume mount in Docker** | Keeps the container's vector DB in sync with the local watchdog — without it the watchdog writes to disk but the container reads a stale internal copy |
| **`.env` excluded from Docker image** | API keys should never be baked into an image layer — injected at `docker run` time via `--env-file` instead |
| **Unified `PITCH_KEY` in `config.py`** | Single source of truth for the JSON response field name — frontend and backend both import it, eliminating key-mismatch bugs |

---

## 📄 License
Distributed under the MIT License.