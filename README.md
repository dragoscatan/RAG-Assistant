This repository contains the source code for a fully localized Retrieval-Augmented Generation (RAG) platform, developed as a bachelor's degree project at the Politehnica University of Timișoara. The system enables semantic search and LLM inference over user-provided PDF documents with zero external API dependencies, ensuring strict data privacy.

Architecture
The application is fully containerized using Docker and segmented into three microservices:

Frontend: React.js / Vite
Backend: Python / FastAPI, LangChain, ChromaDB (Vector Store)
Inference Engine: Ollama with NVIDIA GPU Passthrough
Embedding Model: `nomic-embed-text`
  LLM: `llama3.1` (8B)

Prerequisites

* Docker Desktop - !!engine must be running
* NVIDIA GPU with updated drivers and at least 8G VRAM

Initialization
Execute the following command in the project root directory:

```bash
docker compose up --build
