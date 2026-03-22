# GTM Sales Agent (Agentic RAG)

A high-performance Sales Agent powered by **Gemini 3 Flash** and **LangChain**, designed to generate data-driven GTM (Go-To-Market) strategies from unstructured enterprise data.

## 🚀 Overview
This project implements a **Retrieval-Augmented Generation (RAG)** architecture. By leveraging the low-latency reasoning of the **Gemini 3 Flash** model, the agent can analyze complex strategy documents (e.g., STIHL 2026 Strategy) and generate actionable, context-aware sales pitches in real-time.

## 🛠️ Tech Stack
* **LLM:** Google Gemini 3 Flash (Optimized for low-latency reasoning)
* **Orchestration:** LangChain & LangGraph
* **Vector Database:** ChromaDB
* **Backend API:** FastAPI (Containerized with Docker)
* **Frontend UI:** Streamlit (Python-native dashboard)
* **Infrastructure:** Docker (Optimized for CPU-only environments)

## ✨ Key Features
* **Model Optimization:** Utilizes **Gemini 3 Flash** to minimize "Time-to-First-Token," ensuring a snappy, responsive experience for sales teams.
* **Semantic Retrieval:** High-dimensional vector search using `sentence-transformers` to ground AI responses in "ground truth" company data.
* **Production-Ready API:** Fully documented Swagger UI via FastAPI.
* **Architectural Efficiency:** Specialized Docker build using CPU-specific PyTorch wheels to reduce image footprint by ~80%.

## 🔧 Installation & Setup

### Running with Docker (Recommended)
1. **Clone the repository:**
   ```bash
   git clone [https://github.com/amartinez26/gtm-sales-agent.git](https://github.com/amartinez26/gtm-sales-agent.git)
   cd gtm-sales-agent
   docker build -t gtm-sales-agent .
   docker run -p 8000:8000 --env-file .env gtm-sales-agent

# Install UI dependencies
   pip install streamlit requests

# Launch the dashboard
  streamlit run frontend/app_ui.py