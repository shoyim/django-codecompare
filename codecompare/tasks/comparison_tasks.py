"""Celery tasks for asynchronous comparison processing."""
from __future__ import annotations
import dataclasses, logging
from typing import Any

logger = logging.getLogger(__name__)


def _run_comparison_sync(job_id: str) -> None:
    from django.utils import timezone
    from codecompare.core.services import ComparisonService
    from codecompare.models.models import ComparisonJob, ComparisonResult

    try:
        job = ComparisonJob.objects.get(id=job_id)
    except ComparisonJob.DoesNotExist:
        logger.error("ComparisonJob %s not found", job_id)
        return

    job.status = ComparisonJob.Status.RUNNING
    job.started_at = timezone.now()
    job.save(update_fields=["status", "started_at"])

    try:
        service = ComparisonService()
        result = service.compare(
            job.old_code, job.new_code,
            job.language if job.language and job.language != "auto" else None,
            job.comparison_options,
        )

        def _diff_dict(diff_result):
            return {
                "added": diff_result.added, "removed": diff_result.removed,
                "equal": diff_result.equal, "mode": diff_result.mode.value,
                "chunks": [
                    {"old_start": c.old_start, "old_count": c.old_count,
                     "new_start": c.new_start, "new_count": c.new_count, "header": c.header,
                     "lines": [{"old_no": l.old_no, "new_no": l.new_no,
                                "content": l.content, "change_type": l.change_type.value}
                               for l in c.lines[:200]]}
                    for c in diff_result.chunks
                ],
            }

        ComparisonResult.objects.update_or_create(
            job=job,
            defaults={
                "language": result.language,
                "similarity_overall": result.similarity.overall,
                "similarity_exact": result.similarity.exact,
                "similarity_semantic": result.similarity.semantic,
                "similarity_structural": result.similarity.structural,
                "similarity_token": result.similarity.token,
                "similarity_ast": result.similarity.ast,
                "diff_data": _diff_dict(result.diff),
                "ast_diff_data": result.ast_diff,
                "statistics_data": dataclasses.asdict(result.statistics),
                "complexity_old": dataclasses.asdict(result.old_complexity),
                "complexity_new": dataclasses.asdict(result.new_complexity),
                "plagiarism_data": dataclasses.asdict(result.plagiarism),
                "warnings": result.warnings,
                "metadata": result.metadata,
            },
        )
        job.status = ComparisonJob.Status.COMPLETED
        job.processing_time_ms = result.processing_time_ms

    except Exception as exc:
        logger.exception("Comparison failed for job %s", job_id)
        job.status = ComparisonJob.Status.FAILED
        job.error_message = str(exc)

    finally:
        job.completed_at = timezone.now()
        job.save(update_fields=["status", "processing_time_ms", "error_message", "completed_at"])


def _get_celery_app():
    try:
        from config.celery import app
        return app
    except ImportError:
        return None


celery_app = _get_celery_app()

if celery_app is not None:
    @celery_app.task(bind=True, name="codecompare.tasks.run_comparison",
                     max_retries=3, default_retry_delay=5, queue="comparison", acks_late=True)
    def run_comparison(self, job_id: str) -> dict[str, Any]:
        try:
            _run_comparison_sync(job_id)
            return {"job_id": job_id, "status": "completed"}
        except Exception as exc:
            raise self.retry(exc=exc)
else:
    class _StubTask:
        def delay(self, *args, **kwargs):
            logger.warning("Celery not available — running synchronously")
            if args:
                _run_comparison_sync(args[0])
            return type("FakeResult", (), {"id": "sync"})()
        def __call__(self, *args, **kwargs):
            if args:
                _run_comparison_sync(args[0])

    run_comparison = _StubTask()
