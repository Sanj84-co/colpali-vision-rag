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

Measured on a 15-question labeled set spanning a synthetic chart, a real SEC 10-K filing, and a real Federal Reserve economic report:

| | Accuracy |
|---|---|
| Raw retrieval (no reranking) | 33% |
| With reranking | 73% |

Reranking recovered 6 of 10 questions raw retrieval got wrong, at the cost of extra Gemini API calls per query.

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
