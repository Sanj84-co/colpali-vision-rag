---
title: Colpali Vision RAG
emoji: 📄
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---

# Colpali Vision RAG

A vision-based RAG system that answers questions about PDFs **without OCR or text extraction**. Pages are rendered as images, embedded with ColPali (ColQwen2) as multivectors, retrieved via MAX_SIM in Qdrant, reranked by Gemini, and answered by Gemini reading the actual page images. Charts and scanned documents are searchable even though no text is ever extracted from them.

## Architecture

```
PDF -> render to page images -> ColQwen2 multivector embeddings -> Qdrant (MAX_SIM)
                                                                        |
question -> ColQwen2 query embedding -> Qdrant search (top-10) -> Gemini rerank -> Gemini answer
```

## Evaluation

Measured on a 30-question labeled set spanning a synthetic chart, a real SEC 10-K filing (HEICO Corporation), and a real Federal Reserve economic report, across a 58-page collection:

| | Accuracy |
|---|---|
| Raw retrieval (no reranking) | 17% |
| With reranking (top-10 candidates) | 43% |

Reranking recovers roughly a third of retrieval's failures, but a clear pattern remains: **the system performs well on prominent, salient visual answers** (bar charts, clearly labeled headings, single standout numbers) **but struggles on precise cell-level lookups inside dense multi-column tables**. Diagnosing several failures directly showed the correct page ranking 19th-39th out of 58 in raw embedding similarity — far outside any practically-sized candidate pool. Widening the rerank candidate pool to nearly the full collection (50 of 58) recovered 2 of 3 tested cases, confirming the diagnosis, but at a real cost/latency tradeoff that doesn't scale to larger collections.

**Root cause**: ColPali's whole-page multivector embedding captures what a page is broadly about, but doesn't reliably localize one specific number buried among dozens of similar ones on a dense page. A real fix would mean embedding below the page level (splitting dense pages into sub-regions before embedding), not a config tweak — noted as a concrete next step rather than solved here.

## Running locally

```
uv sync
uv run python scripts/make_sample_pdf.py
uv run python src/ingest.py
PYTHONPATH=. uv run python src/main.py "your question"
```

## API

```
POST /query   {"question": "..."}      -> {"answer": "...", "retrieved": [...]}
POST /ingest  {}                        -> {"status": "done"}
```

Both endpoints require an `x-api-key` header matching `API_KEY` in your environment.

## Tests

```
uv run pytest          # fast tests only (no GPU/API calls)
uv run pytest -m slow  # includes real model + Gemini API tests
```
