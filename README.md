# CodeCompare — Production-grade Django code comparison package

A Django package and microservice for comparing code snippets, files, and repositories. Combines Myers diff, TF-IDF cosine similarity, Jaccard, Levenshtein, AST analysis, and Winnowing fingerprinting into a single pipeline.

## Features

- **Similarity scoring** — overall, token, cosine, jaccard, AST, levenshtein (0-100%)
- **Plagiarism detection** — Winnowing fingerprinting + structural analysis with confidence levels
- **Myers Diff** — O(ND) line/word/token/inline diff, unified and side-by-side output
- **Python AST analysis** — function/class/import extraction, cyclomatic complexity, body hashing
- **Complexity metrics** — cyclomatic complexity, Halstead metrics, Maintainability Index
- **Rename detection** — detects renamed variables and functions via frequency + name similarity
- **Language detection** — 21 languages (Python, JS, TS, Java, C, C++, Go, Rust, PHP, …)
- **Django REST API** — sync and async endpoints, file upload, WebSocket live comparison
- **Celery async tasks** — background processing with Redis broker
- **CLI** — `codecompare compare`, `diff`, `languages`, `serve`
- **Docker + Kubernetes** — production-ready Compose and K8s manifests

## Quick start

```bash
# Install
pip install -e .

# Or with all dev tools
pip install -r requirements-dev.txt

# Run migrations
python manage.py migrate

# Start dev server
python manage.py runserver
```

### Python API

```python
from codecompare.core.services import compare

result = compare(old_code, new_code, language="python")
print(result.similarity.overall)   # e.g. 73.5
print(result.stats.lines_added)
print(result.plagiarism.confidence)
```

### REST API

```
POST /api/compare/
Content-Type: application/json

{
  "old_code": "def foo(): pass",
  "new_code": "def bar(): pass",
  "language": "python"
}
```

```
POST /api/compare/async/      # Returns job ID
GET  /api/jobs/{id}/          # Poll status
GET  /api/jobs/{id}/result/   # Fetch result
POST /api/compare/files/      # Upload two files
GET  /api/languages/          # List supported languages
```

### CLI

```bash
codecompare compare old.py new.py --language python
codecompare diff old.py new.py --format unified
codecompare languages
codecompare serve --port 8000
```

### WebSocket

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/compare/");
ws.send(JSON.stringify({ old_code: "...", new_code: "...", language: "python" }));
ws.onmessage = (e) => console.log(JSON.parse(e.data));
// Events: parsing / diff / similarity / ast / plagiarism / done
```

## Docker

```bash
# Dev
docker-compose up

# Production
cp .env.example .env   # fill in secrets
docker-compose -f docker-compose.prod.yml up -d
```

Services: **app** (uvicorn, 2 replicas), **worker** (Celery, 2 replicas), **nginx**, **postgres**, **redis**, **flower**.

## Kubernetes

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
```

HPA scales API 2–10 replicas (CPU ≥70%) and workers 2–8 replicas (CPU ≥75%).

## Configuration

| Setting | Default | Description |
|---|---|---|
| `CODECOMPARE.MAX_FILE_SIZE` | `10485760` | Max upload bytes (10 MB) |
| `CODECOMPARE.CACHE_TTL` | `3600` | Result cache TTL (seconds) |
| `CODECOMPARE.PLAGIARISM_THRESHOLD` | `0.70` | Score above which code is flagged |
| `CODECOMPARE.LARGE_FILE_THRESHOLD` | `50000` | Lines before switching to fast diff |

## Algorithms

| Algorithm | File | Complexity |
|---|---|---|
| Myers Diff | `diff_engine/myers.py` | O(ND) |
| Wagner-Fischer | `similarity/levenshtein.py` | O(mn) |
| Damerau-Levenshtein | `similarity/levenshtein.py` | O(mn) |
| TF-IDF Cosine | `similarity/cosine.py` | O(V) |
| Jaccard (shingles) | `similarity/jaccard.py` | O(n) |
| Winnowing | `semantic_engine/fingerprinting.py` | O(n) |
| Rabin-Karp hash | `semantic_engine/fingerprinting.py` | O(n) |
| Python AST | `ast_engine/python_ast.py` | O(n) |

## Development

```bash
make dev        # install dev dependencies
make test       # run tests
make lint       # ruff check
make format     # ruff format + fix
make test-cov   # tests with HTML coverage report
make test-bench # run benchmarks
```

## License

MIT
