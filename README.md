# Arabic Legal Assistant — Saudi Labor Law RAG

An AI assistant that answers questions about the Saudi Labor Law — including questions written in Saudi dialect — with answers grounded in the official text and cited by article.
**Live demo:** (https://saudi-labor-law-assistant.streamlit.app/)


## The Problem

Employees and employers often need quick answers about their rights (leave, wages, end-of-service benefits), but the law is long, formal, and hard to search. General chatbots may produce confident but incorrect answers with no source.

## How It Works

1. **Extraction and cleaning** — Text is extracted from the official PDF, fixing broken Arabic character encoding, removing tatweel, and filtering headers.
2. **Structure-aware chunking** — The law is split article by article (not by fixed length), cross-references are merged back, and 35 repealed articles are removed, leaving 214 active articles.
3. **Semantic indexing** — Each article is embedded with a multilingual model (`multilingual-e5-small`) and stored in ChromaDB.
4. **Query rewriting** — Colloquial questions are rewritten into formal legal wording (e.g. "راتب" → "أجر").
5. **Fusion retrieval** — The original and rewritten questions are both searched, and results are merged with Reciprocal Rank Fusion (RRF).
6. **Grounded generation** — Gemini answers only from the retrieved articles, cites the article, and replies "not found" when the answer is not in the law.

## Evaluation

Test sets of Saudi-dialect questions were generated from randomly sampled articles, then reviewed manually. Metric: whether the correct article appears in the top results.

**Set 2 — updated law (38 questions)**

| Method | Hit@1 | Hit@3 | Hit@6 | MRR |
|---|---|---|---|---|
| Original question | 53% | 66% | 84% | 0.63 |
| Rewritten question | 68% | 84% | 92% | 0.77 |
| Fusion (both) | 63% | 84% | 92% | 0.74 |

**Set 1 — previous version of the law (40 questions)**

| Method | Hit@1 | Hit@3 | Hit@6 | MRR |
|---|---|---|---|---|
| Original question | 55% | 78% | 90% | 0.69 |
| Rewritten question | 50% | 78% | 85% | 0.64 |
| Fusion (both) | 55% | 88% | 98% | 0.71 |

**Key finding:** Query rewriting alone was unstable — the worst method on one set and the best on the other. Fusion was best or tied for best on both, so it was chosen for the final system for its stability.

## Limitations

- Evaluation sets are small (38–40 questions) and generated from article text, which may favor the article's own wording.
- Covers the Labor Law only, not its Implementing Regulations.
- The system is only as current as its source document and must be re-indexed when the law is amended.
- Answers are for guidance only and are not legal advice.

## Run Locally

```bash
pip install -r requirements.txt
```

Create a `.env` file with your key:

```
GEMINI_API_KEY=your_key_here
```

Then:

```bash
python prepare_data.py
python build_index.py
python -m streamlit run app.py
```

## Project Structure

| File | Purpose |
|---|---|
| `prepare_data.py` | Extract, clean, and split the law into articles |
| `build_index.py` | Embed articles and build the vector database |
| `rag.py` | Query rewriting, fusion retrieval, and answer generation |
| `app.py` | Streamlit chat interface |
| `build_eval.py` | Generate the evaluation question set |
| `evaluate.py` | Measure retrieval accuracy |

## Tech Stack

Python · ChromaDB · Sentence Transformers · Google Gemini · Streamlit · PyMuPDF

---

**Author:** Fahad Almghamsy — Data Science and Analytics student, University of Ha'il
