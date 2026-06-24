# TECH_SPEC.md

## Project: **code‑scout**

> **A local‑first, private search & analytics platform for coding agents, providing secure and efficient insights for tech professionals.**

---

## 1. Overview

`code-scout` is a self‑contained, end‑to‑end platform that ingests a developer’s codebase, indexes it locally, and exposes a lightweight API for search, analytics, and agent‑driven insights. The system is designed for **privacy‑first** usage: all data stays on the developer’s machine, no external telemetry is sent, and the architecture is fully offline‑capable.

The product is built to integrate seamlessly with existing IDEs and CI pipelines, enabling agents to query code, discover patterns, and surface actionable metrics without compromising security.

---

## 2. Architecture

```
┌───────────────────────┐
│  IDE / CLI / Agent    │
│  (Frontend client)    │
└────────────┬──────────┘
             │
             ▼
┌───────────────────────┐
│  API Gateway (FastAPI) │
│  (REST + WebSocket)    │
└────────────┬──────────┘
             │
             ▼
┌───────────────────────┐
│  Indexer Service       │
│  (Rust + LlamaIndex)   │
└────────────┬──────────┘
             │
             ▼
┌───────────────────────┐
│  Search Service        │
│  (vLLM + Pinecone‑Lite)│
└────────────┬──────────┘
             │
             ▼
┌───────────────────────┐
│  Analytics Engine      │
│  (Python + Polars)     │
└────────────┬──────────┘
             │
             ▼
┌───────────────────────┐
│  Storage Layer         │
│  (SQLite + Encrypted)  │
└───────────────────────┘
```

### 2.1 Frontend Client

- **IDE Extension** (VS Code, JetBrains) or **CLI** (`codescout search`, `codescout analyze`).
- Communicates with the API Gateway over **HTTPS** (self‑signed cert) or **Unix socket** for local-only mode.
- Provides a minimal UI for query results and analytics dashboards.

### 2.2 API Gateway

- **FastAPI** (Python 3.12) – high‑performance async framework.
- Exposes:
  - `/search` – keyword / semantic search.
  - `/analyze` – code‑metrics, trend reports.
  - `/index` – manual re‑index triggers.
  - `/health` – liveness/readiness probes.
- Implements **JWT** authentication scoped to the local machine (self‑signed key pair).
- Rate‑limits per‑minute to protect local resources.

### 2.3 Indexer Service

- **Rust** binary (`codescout-indexer`) for fast file traversal and incremental indexing.
- Uses **LlamaIndex** (Python) via FFI for vector embeddings.
- Stores embeddings in **Pinecone‑Lite** (in‑process vector DB) for low‑latency similarity search.
- Supports incremental updates: watches file changes via `notify` crate.

### 2.4 Search Service

- **vLLM** (C++/CUDA) for optional LLM‑powered semantic search (fallback to keyword if GPU unavailable).
- Exposes a lightweight RPC interface to the API Gateway.
- Returns ranked snippets with source file metadata.

### 2.5 Analytics Engine

- **Python** microservice using **Polars** for fast columnar analytics.
- Computes metrics such as:
  - Cyclomatic complexity distribution.
  - Dependency graph density.
  - Code churn over time (if Git metadata available).
- Outputs JSON reports consumable by the frontend.

### 2.6 Storage Layer

- **SQLite** encrypted with **SQLCipher** for local persistence of:
  - File metadata (paths, timestamps).
  - Embedding vectors (serialized BLOBs).
  - Analytics cache.
- All data is stored under the user’s home directory (`~/.codescout/`).

---

## 3. Data Model

| Table | Columns | Description |
|-------|---------|-------------|
| `files` | `id`, `path`, `mtime`, `size`, `lang`, `hash` | File metadata. |
| `embeddings` | `file_id`, `vector` | LLM embeddings per file. |
| `metrics` | `file_id`, `cyclomatic`, `lines`, `complexity`, `created_at` | Static code metrics. |
| `analysis_cache` | `key`, `value`, `expires_at` | Cached analytics results. |

- **Vector Storage**: Pinecone‑Lite stores vectors in a memory‑mapped file (`~/.codescout/vector_store.bin`).
- **Encryption**: All SQLite tables are encrypted; the key is derived from a user‑provided passphrase (or OS keychain).

---

## 4. Key APIs / Interfaces

| Endpoint | Method | Request | Response | Notes |
|----------|--------|---------|----------|-------|
| `/search` | POST | `{"query":"async function", "top_k":10}` | `{"results":[{"file":"src/async.c","snippet":"...","score":0.92}, ...]}` | Supports keyword + semantic search. |
| `/analyze` | POST | `{"type":"complexity"}` | `{"metrics":[{"file":"src/main.c","cyclomatic":5}, ...]}` | Returns aggregated stats. |
| `/index` | POST | `{"paths":["src/"]}` | `{"status":"reindexed","files":123}` | Triggers full or incremental index. |
| `/health` | GET | – | `{"status":"ok"}` | Liveness probe. |

### Authentication

- **JWT** signed by a local key pair.
- Token is short‑lived (15 min) and refreshed automatically by the client.

### WebSocket

- `/ws/updates` – streams real‑time index updates and analytics results.

---

## 5. Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Frontend | VS Code Extension (TypeScript), CLI (Rust) | Native IDE integration, cross‑platform CLI. |
| API Gateway | FastAPI (Python 3.12) | Async, type‑safe, excellent docs. |
| Indexer | Rust (`codescout-indexer`) | High‑performance file I/O, safe concurrency. |
| Embeddings | LlamaIndex (Python) | Modular, supports multiple backends. |
| Vector DB | Pinecone‑Lite | In‑process, zero‑config, fast similarity search. |
| LLM Search | vLLM | GPU‑accelerated inference, fallback to CPU. |
| Analytics | Polars (Python) | Columnar engine, low memory footprint. |
| Storage | SQLite + SQLCipher | Portable, encrypted, ACID. |
| Deployment | Docker (optional), native binaries | Easy distribution, local‑only mode. |

---

## 6. Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | ^0.110.0 | API framework |
| `uvicorn` | ^0.29.0 | ASGI server |
| `pydantic` | ^2.7.0 | Data validation |
| `llama-index` | ^0.10.0 | Embedding pipeline |
| `pinecone-client` | ^3.0.0 | Vector DB client |
| `vllm` | ^0.5.0 | LLM inference |
| `polars` | ^0.20.0 | Analytics |
| `sqlcipher` | ^4.5.0 | Encrypted SQLite |
| `notify` | ^5.1.0 | Rust file watcher |
| `serde` | ^1.0 | Rust serialization |
| `tokio` | ^1.0 | Async runtime (Rust) |
| `sqlx` | ^0.7 | Rust DB access |

All dependencies are open‑source and permissively licensed (MIT/Apache‑2.0).

---

## 7. Deployment & Runtime

### 7.1 Local Installation

```bash
# Install Rust toolchain
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Build indexer
cargo build --release --bin codescout-indexer

# Install Python deps
pip install -r requirements.txt

# Run API
uvicorn main:app --host 127.0.0.1 --port 8000
```

### 7.2 Docker (Optional)

```dockerfile
FROM python:3.12-slim AS python
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM rust:1.78-slim AS rust
WORKDIR /app
COPY Cargo.toml .
COPY src/ src/
RUN cargo build --release --bin codescout-indexer

FROM debian:bookworm-slim
COPY --from=python /usr/local /usr/local
COPY --from=rust /app/target/release/codescout-indexer /usr/local/bin/
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 7.3 Runtime Configuration

| Env Var | Default | Description |
|---------|---------|-------------|
| `CODESCOUT_DATA_DIR` | `~/.codescout/` | Base storage location |
| `CODESCOUT_JWT_SECRET` | auto‑generated | JWT signing key |
| `CODESCOUT_VECTOR_DB` | `pinecone-lite` | Vector backend |
| `CODESCOUT_LOG_LEVEL` | `info` | Logging verbosity |
| `CODESCOUT_MAX_WORKERS` | `4` | Async worker pool size |

---

## 8. Security Considerations

- **Local‑only**: All data remains on the host; no outbound network traffic unless explicitly configured.
- **Encryption**: Database and vector store encrypted with SQLCipher; keys stored in OS keychain.
- **Authentication**: JWT scoped to local machine; no external identity provider.
- **Sandboxing**: LLM inference runs in a separate process with limited CPU/GPU access.

---

## 9. Testing & CI

- **Unit tests**: Pytest for Python services; Rust unit tests for indexer.
- **Integration tests**: Docker Compose runs full stack; verifies search accuracy and analytics output.
- **Static analysis**: `ruff` (Python), `clippy` (Rust).
- **CI pipeline**: GitHub Actions – lint, test, build, and publish Docker image.

---

## 10. Future Enhancements

1. **Federated Search** – merge local index with remote knowledge bases.
2. **Agent‑Oriented API** – expose a GraphQL interface for coding agents.
3. **Incremental LLM Updates** – fine‑tune embeddings on the fly.
4. **Cross‑Platform GUI** – Electron app for non‑IDE users.

---

*Prepared by: [Your Name], Senior Product & Engineering Lead, Axentx*
