# Changelog

All notable changes to django-codecompare are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] — 2026-05-26

### Added
- Myers O(ND) diff: line, word, token, inline, unified, side-by-side output
- Similarity engines: TF-IDF cosine, Jaccard (shingles), Levenshtein/Wagner-Fischer, Damerau-Levenshtein, token LCS
- Weighted similarity aggregator (token 30%, AST 20%, cosine 20%, jaccard 15%, levenshtein 15%)
- Python AST analysis: function/class/import extraction, cyclomatic complexity, body hashing
- Winnowing fingerprinting + Rabin-Karp rolling hash for plagiarism detection
- Halstead metrics (vocabulary, volume, difficulty, effort) and Maintainability Index
- Rename detection for variables and functions via frequency + name similarity
- Language auto-detection for 21 languages
- Django REST API: sync compare, async compare, file upload, job polling
- WebSocket live comparison via Django Channels with progress events
- Celery async task queue with Redis broker; stub fallback when Celery not installed
- CLI via Click: compare, diff, languages, serve
- Redis-backed cache with gzip compression
- Django models: ComparisonJob, ComparisonResult, FileAnalysis, SimilarityResult
- Docker multi-stage build + docker-compose (dev and production)
- Kubernetes manifests: Deployment, Service, Ingress, HorizontalPodAutoscaler
- GitHub Actions CI/CD: lint, test (Python 3.11/3.12), build, TestPyPI, PyPI, GHCR
