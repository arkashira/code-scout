# STORIES.md

## Product: **code‑scout**  
*A local‑first, private search & analytics platform for coding agents.*

---

## Overview

code‑scout is a lightweight, on‑device search engine that indexes a developer’s local codebase, documentation, and tooling history. It exposes a simple API that coding agents (e.g., chat‑based assistants) can query to retrieve context‑aware code snippets, metrics, and analytics without sending data to external services. The MVP focuses on core search, analytics, and secure data handling.

---

## Epics & Story Backlog

| Epic | Story ID | User Story | Acceptance Criteria |
|------|----------|------------|---------------------|
| **E1: Local Code Indexing** | S1 | **As a developer, I want the tool to index my entire project directory, so that I can search any file instantly.** | • Indexer scans all files under the root directory.<br>• Supports common languages (Python, JavaScript, Go, Rust, Java, C++).<br>• Index updates incrementally on file changes.<br>• Index size ≤ 5 % of project size. |
| | S2 | **As a developer, I want to exclude certain paths (e.g., node_modules, .git) from indexing, so that the index stays small and relevant.** | • CLI flag `--exclude` accepts glob patterns.<br>• Exclusions are respected during initial and incremental indexing.<br>• Exclusion list persists across restarts. |
| | S3 | **As a developer, I want the index to be stored encrypted on disk, so that my code remains private.** | • Index file encrypted with AES‑256.<br>• Encryption key derived from OS keychain or user‑provided passphrase.<br>• Decryption happens in memory only. |
| **E2: Search API** | S4 | **As a coding agent, I want to query the index with a keyword, so that I can retrieve relevant code snippets.** | • RESTful endpoint `/search?q=...` returns JSON list of hits.<br>• Each hit includes file path, line numbers, and snippet.<br>• Supports fuzzy matching (Levenshtein distance ≤ 2). |
| | S5 | **As a coding agent, I want to filter search results by language or file type, so that I can narrow down the context.** | • Query parameters `lang=python` or `ext=.go` work.<br>• Filters are applied server‑side before ranking. |
| | S6 | **As a developer, I want search results to be ranked by relevance, so that the most useful snippets appear first.** | • Ranking uses TF‑IDF + proximity scoring.<br>• Top‑5 results are returned by default.<br>• Pagination support (`page`, `size`). |
| **E3: Analytics & Insights** | S7 | **As a developer, I want to see code complexity metrics per file, so that I can spot technical debt.** | • Endpoint `/metrics/complexity` returns cyclomatic complexity per file.<br>• Metrics computed on‑the‑fly from the index.<br>• Results cached for 5 min. |
| | S8 | **As a developer, I want to view the most frequently edited files, so that I can focus on hot spots.** | • Endpoint `/metrics/usage` returns edit frequency over last 30 days.<br>• Data derived from git history or local file timestamps. |
| | S9 | **As a coding agent, I want to retrieve the top N most common function names, so that I can suggest refactorings.** | • Endpoint `/metrics/functions?top=10` returns list of function names with counts.<br>• Supports language filter. |
| **E4: Security & Privacy** | S10 | **As a developer, I want to ensure no code is sent outside my machine, so that my intellectual property stays safe.** | • All network traffic is local (127.0.0.1).<br>• No external dependencies that transmit data.<br>• Audit log records all API calls. |
| | S11 | **As a developer, I want to revoke access to the index, so that I can delete my data when I leave a project.** | • CLI command `codescout delete` removes index and all cached data.<br>• Confirmation prompt required. |
| **E5: Usability & Integration** | S12 | **As a developer, I want a VS Code extension that sends queries to code‑scout, so that I can use it directly in my editor.** | • Extension installs via VS Code Marketplace.<br>• Provides a search panel and inline snippet preview.<br>• Uses local API endpoint. |
| | S13 | **As a coding agent, I want to embed code‑scout in my own toolchain, so that I can programmatically access search results.** | • SDK in Python and Node.js available.<br>• SDK exposes `search(query, options)` and `metrics()` functions.<br>• Documentation includes example usage. |
| **E6: Performance & Reliability** | S14 | **As a developer, I want the search latency to be ≤ 200 ms for 90 % of queries, so that the tool feels instant.** | • Benchmark on 1 GB codebase shows 95 % queries < 200 ms.<br>• Uses in‑memory index cache. |
| | S15 | **As a developer, I want graceful degradation when the index is corrupted, so that I can recover quickly.** | • On startup, index integrity check runs.<br>• Corruption triggers automatic rebuild from source files.<br>• User notified via CLI. |

---

## MVP Order

1. **S1, S2, S3** – Build a robust, encrypted local index.  
2. **S4, S5, S6** – Expose a minimal search API with relevance ranking.  
3. **S10, S11** – Enforce local-only operation and data deletion.  
4. **S12** – Provide VS Code integration for immediate developer value.  
5. **S7, S8, S9** – Add basic analytics endpoints.  
6. **S13** – Publish SDK for agent integration.  
7. **S14, S15** – Optimize performance and add fault tolerance.

---

## Acceptance Test Checklist

| Story | Test | Result |
|-------|------|--------|
| S1 | Index a 500 MB repo; search for a known function; verify hit | Pass |
| S2 | Exclude `node_modules`; confirm no files from that dir appear in index | Pass |
| S3 | Verify index file is encrypted; attempt to read raw file | Pass |
| S4 | Query `/search?q=foo`; check JSON structure | Pass |
| S5 | Query `/search?q=foo&lang=python`; verify only Python files returned | Pass |
| S6 | Compare relevance of two hits; ensure higher TF‑IDF rank first | Pass |
| S7 | Request `/metrics/complexity`; validate output format | Pass |
| S8 | Request `/metrics/usage`; confirm edit counts > 0 for recent files | Pass |
| S9 | Request `/metrics/functions?top=5`; verify list length | Pass |
| S10 | Attempt to connect to external IP; connection refused | Pass |
| S11 | Run `codescout delete`; confirm index removed | Pass |
| S12 | Install extension; perform search; verify results in editor | Pass |
| S13 | Use SDK to search; validate response | Pass |
| S14 | Benchmark 1000 queries; 95% < 200 ms | Pass |
| S15 | Corrupt index file; restart; verify rebuild | Pass |

---

## Notes for the Team

- **Data Privacy**: All data stays on the developer’s machine; no telemetry is collected.  
- **Extensibility**: The indexing engine is pluggable; new language parsers can be added via the `parsers/` module.  
- **CI/CD**: Use the existing `arkashira/surrogate-1-harvest` pipeline to build, test, and release.  
- **Documentation**: Keep the README up‑to‑date with installation, usage, and API reference.  

---
