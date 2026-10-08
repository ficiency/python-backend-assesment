# Caching Service

A FastAPI microservice that transforms and interleaves two lists of strings, persists the generated payload, and caches results to avoid redundant processing.

The service uses PostgreSQL for persistence and SQLModel for database operations. It is containerized with Docker Compose.

## Getting Started

**Requirements:** Docker and Docker Compose.

From the project root:

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.

PostgreSQL is exposed on port `5433` to avoid conflicts with local installations.

## API Endpoints

### Create a payload

`POST /payload`

```bash
curl -X POST http://localhost:8000/payload \
  -H "Content-Type: application/json" \
  -d '{"list_1":["first string","second string","third string"],"list_2":["other string","another string","last string"]}'
```

Example response:

```json
{
  "id": "03a734ef-68d2-40f9-a85d-9722e5b8d5f4",
  "message": "payload created"
}
```

Submitting the same input again returns the same `id` with `"message": "payload already stored"`. The transformation is not repeated.

### Retrieve a payload

`GET /payload/{id}`

```bash
curl http://localhost:8000/payload/<id>
```

Example response:

```json
{
  "output": "FIRST STRING, OTHER STRING, SECOND STRING, ANOTHER STRING, THIRD STRING, LAST STRING"
}
```

**Error handling:**

- `422 Unprocessable Entity` when input lists have different lengths.
- `404 Not Found` when the requested payload does not exist.

## Architecture

The service separates payload generation from caching and persistence.

**Request processing**

1. Validate the input lists.
2. Generate a deterministic SHA-256 label from the original input.
3. Check whether a payload with that label already exists.
4. For new payloads, retrieve cached string transformations or compute and persist missing ones.
5. Interleave the transformed strings, one from each list in turn, because that is how the sample output is built. Store the result with a unique identifier.

Retrieving an existing payload requires only a database lookup.

### Caching Strategy

Two database tables support caching at different levels:

| Table | Purpose |
|---|---|
| `transforms` | Stores individual string transformations for reuse across requests. |
| `payloads` | Stores the generated output, its id, and the request `label`, so identical requests reuse the same identifier. |

This avoids both redundant transformations and unnecessary payload generation.

### Design Decisions

**Simulated transformer**

The external transformation service is represented by a local function that converts strings to uppercase, matching the expected output. This keeps the assessment self-contained while preserving the caching behavior.

**Deterministic request identification**

A SHA-256 label is generated from the input lists in their original order and stored in `payloads.label`. Identical inputs produce the same label, while changes to content or ordering produce a different one. The label is internal; clients interact only with payload identifiers.

**PostgreSQL persistence**

PostgreSQL provides persistent, shared storage for both caches. Unlike process-local storage, it allows multiple application instances to access the same data.

**Database-backed payload storage**

Generated payloads are stored directly in PostgreSQL rather than as individual filesystem files. This keeps retrieval and caching within the same persistence layer and avoids dependencies on container-local storage.

**Database-first cache lookup**

The service checks for an existing payload before processing individual strings. If the payload already exists, no transformation or additional cache lookup is required.

### Lookup cost

Interleaving walks both lists once and takes one element from each. Time and space are linear in the length of the lists.

`payloads.label` and `transforms.word` are unique indexes. Each lookup is a B-tree search, O(log n) in the number of stored rows, not a table scan.

A repeated request is one indexed lookup on `label`, and then it stops. A new request does one indexed lookup per word and inserts only the words that are not already stored. Each operation stays cheap because of the index. What grows is the number of round trips.

That is enough for the short inputs in the task. With thousands of new words, the same rule should run as one `WHERE word IN (...)` lookup and one batch insert for the missing rows. The tables, the label, and the interleave step stay as they are.

## Testing

Running the service only needs Docker. Running the tests also needs Python.

Start the containers, install the dependencies, and then run the suite:

```bash
docker compose up -d --build
pip install -r requirements.txt
pytest
```

Tests connect to the PostgreSQL instance exposed on port `5433` by default. A local `.env` file can override the database configuration.

The test suite covers:

- String transformation and interleaving
- Database persistence
- Payload creation and retrieval
- Reuse of existing payload identifiers
- Reuse of cached string transformations
- Input validation and missing payloads
