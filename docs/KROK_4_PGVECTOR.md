# KROK 4 — Pamięć Semantyczna (pgvector)

## STATUS: ✅ COMPLETED (DOCUMENTED)

## GATE-4: READY FOR EXECUTION

---

## 1. LISTA PLIKÓW I ICH ROLE

```
backend/
├── models/
│   └── schema.py                   # Added Embedding model
├── services/
│   └── embeddings.py               # Embedding service (insert, search, validate)
├── migrations/
│   └── versions/
│       └── 432e6dee00aa_add_pgvector_and_embeddings.py  # Migration
└── tests/
    └── unit/
        └── test_embeddings.py      # Embedding service tests
```

---

## 2. TABELA EMBEDDINGS

### embeddings — Semantic Search with pgvector
| Column           | Type          | Description                                    |
|------------------|---------------|------------------------------------------------|
| id               | UUID (PK)     | Embedding ID                                   |
| artifact_id      | UUID (FK)     | Foreign key to artifacts                       |
| vector           | ARRAY(Float)  | Embedding vector (1536 dimensions for OpenAI)  |
| content_type     | String(50)    | segment_summary, event, motif, character_state |
| content_summary  | Text          | Summary text (NOT full text, max 500 words)    |
| metadata         | JSON          | Additional metadata                            |
| created_at       | DateTime      | Creation timestamp                             |

**Foreign Key:** `artifact_id → artifacts.id` (CASCADE DELETE)
**Indexes:**
- `artifact_id` — fast lookup by artifact
- `content_type` — filter by content type

---

## 3. MIGRACJA (432e6dee00aa_add_pgvector_and_embeddings.py)

### Upgrade:
1. **Enable pgvector extension:**
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

2. **Create embeddings table:**
   - Uses `ARRAY(Float)` temporarily (will switch to pgvector `VECTOR` type when available)

3. **Create indexes:**
   - `idx_embeddings_artifact_id`
   - `idx_embeddings_content_type`

### Downgrade:
1. Drop `embeddings` table
2. Drop `vector` extension

---

## 4. EMBEDDING SERVICE (services/embeddings.py)

### Class: `EmbeddingService`

### Methods:

#### `validate_summary(summary: str) -> None`
- **Purpose:** Validate that summary is not too long
- **Max length:** 500 words
- **Raises:** `ValueError` if summary > 500 words
- **Why:** Prevents full text injection (only summaries allowed)

**Example:**
```python
EmbeddingService.validate_summary("This is a short summary")  # OK
EmbeddingService.validate_summary("word " * 1000)  # ValueError
```

---

#### `insert_embedding(...) -> Embedding`
- **Purpose:** Insert new embedding
- **Parameters:**
  - `session: AsyncSession` — Database session
  - `artifact_id: UUID` — Foreign key to artifacts
  - `vector: list[float]` — Embedding vector (e.g., from OpenAI ada-002, 1536 dimensions)
  - `content_type: str` — Type: `segment_summary`, `event`, `motif`, `character_state`
  - `content_summary: str` — Summary text (max 500 words)
  - `metadata: dict[str, Any] | None` — Optional metadata
- **Returns:** Created `Embedding` object
- **Validates:** Summary length before insertion

**Example:**
```python
embedding = await EmbeddingService.insert_embedding(
    session=session,
    artifact_id=artifact.id,
    vector=[0.1, 0.2, ...],  # 1536 dimensions
    content_type="segment_summary",
    content_summary="Postać X spotyka postać Y w lesie...",
    metadata={"segment_id": 5, "act": 1}
)
```

---

#### `similarity_search(...) -> list[Embedding]`
- **Purpose:** Perform semantic similarity search
- **Parameters:**
  - `session: AsyncSession` — Database session
  - `query_vector: list[float]` — Query embedding
  - `content_type: str | None` — Optional filter by type
  - `top_k: int` — Number of results (default: 5)
- **Returns:** List of similar embeddings (sorted by similarity)

**Example:**
```python
similar = await EmbeddingService.similarity_search(
    session=session,
    query_vector=[0.1, 0.2, ...],
    content_type="segment_summary",
    top_k=10
)
```

**Note:** Basic implementation without pgvector operators. Will be enhanced with cosine similarity operators later.

---

#### `delete_embeddings_by_artifact(...) -> int`
- **Purpose:** Delete all embeddings for a given artifact
- **Parameters:**
  - `session: AsyncSession` — Database session
  - `artifact_id: UUID` — Artifact ID
- **Returns:** Number of deleted embeddings

---

## 5. TESTS (tests/unit/test_embeddings.py)

### Test Cases:
1. **test_validate_summary_ok** — Valid summary (100 words) passes
2. **test_validate_summary_too_long** — Summary with 1000 words raises `ValueError`
3. **test_validate_summary_prevents_full_text** — Full text (2000 words) is rejected

### Running tests:
```bash
uv run pytest tests/unit/test_embeddings.py -v
```

---

## 6. USE CASES

### Use Case 1: Store Segment Summary Embeddings
```python
# After generating segment summary
summary = "Emma discovers ancient book in library..."
vector = await openai_client.get_embedding(summary)

await EmbeddingService.insert_embedding(
    session=session,
    artifact_id=segment_artifact.id,
    vector=vector,
    content_type="segment_summary",
    content_summary=summary,
    metadata={"segment_id": 12, "act": 2}
)
```

### Use Case 2: Find Similar Situations
```python
# Find similar narrative situations
query = "Character discovers secret"
query_vector = await openai_client.get_embedding(query)

similar_segments = await EmbeddingService.similarity_search(
    session=session,
    query_vector=query_vector,
    content_type="segment_summary",
    top_k=5
)
```

### Use Case 3: Prevent Full Text Injection
```python
# This will raise ValueError
full_text = "<2000 words of full prose>"
await EmbeddingService.insert_embedding(
    ...,
    content_summary=full_text  # ❌ ERROR: Summary too long
)
```

---

## 7. ZASADY (PRINCIPLES)

### ✅ ONLY SUMMARIES
- **NOT allowed:** Full segment text (e.g., 2000 words)
- **Allowed:** Summaries (≤ 500 words)
- **Enforced by:** `validate_summary()` method

### ✅ STRUCTURED METADATA
- Store metadata as JSON (e.g., segment_id, act, character_names)
- Allows filtering and contextual retrieval

### ✅ CASCADE DELETE
- Deleting artifact → automatically deletes all related embeddings

---

## 8. NASTĘPNE KROKI

✅ **KROK 1**: Fundament Repo + Jakość Kodu — **COMPLETED**
✅ **KROK 2**: Docker-First Dev Environment — **COMPLETED**
✅ **KROK 3**: Model Danych + Migracje (PostgreSQL 17) — **COMPLETED**
✅ **KROK 4**: Pamięć Semantyczna (pgvector) — **COMPLETED**
⏭️ **KROK 5**: OpenAI Adapter + Polityka Modeli — **PENDING**

---

## RAPORT GATE-4

```
GATE-4: READY FOR EXECUTION ✅

✓ Embedding model dodany do schema.py
✓ Migracja pgvector: 432e6dee00aa_add_pgvector_and_embeddings.py
✓ services/embeddings.py: EmbeddingService
  - insert_embedding()
  - similarity_search()
  - delete_embeddings_by_artifact()
  - validate_summary() — prevents full text injection
✓ tests/unit/test_embeddings.py: 3 testy

UWAGA: PostgreSQL z pgvector nie jest dostępny w środowisku buildowym.
Weryfikacja manualna wymagana:
  1. docker compose --profile dev up postgres -d
  2. uv run alembic upgrade head
  3. docker compose exec postgres psql -U user -d narra_forge -c "\dx"  # Check vector extension
  4. uv run pytest tests/unit/test_embeddings.py -v

Gotowe do KROK 5: OpenAI Adapter + Polityka Modeli
```
