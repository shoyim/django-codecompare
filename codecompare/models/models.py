"""Database models for the codecompare Django application."""
from __future__ import annotations
import uuid
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ComparisonJob(TimestampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="comparison_jobs")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    language = models.CharField(max_length=50, blank=True)
    old_code_hash = models.CharField(max_length=64, blank=True)
    new_code_hash = models.CharField(max_length=64, blank=True)
    old_code = models.TextField(blank=True)
    new_code = models.TextField(blank=True)
    old_filename = models.CharField(max_length=512, blank=True)
    new_filename = models.CharField(max_length=512, blank=True)
    comparison_options = models.JSONField(default=dict, blank=True)
    task_id = models.CharField(max_length=255, blank=True)
    error_message = models.TextField(blank=True)
    processing_time_ms = models.FloatField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "codecompare"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self) -> str:
        return f"ComparisonJob({self.id}, {self.status})"


class ComparisonResult(TimestampedModel):
    job = models.OneToOneField(ComparisonJob, on_delete=models.CASCADE, related_name="result")
    language = models.CharField(max_length=50)
    similarity_overall = models.FloatField(default=0.0)
    similarity_exact = models.FloatField(default=0.0)
    similarity_semantic = models.FloatField(default=0.0)
    similarity_structural = models.FloatField(default=0.0)
    similarity_token = models.FloatField(default=0.0)
    similarity_ast = models.FloatField(default=0.0)
    diff_data = models.JSONField(default=dict)
    ast_diff_data = models.JSONField(default=dict)
    statistics_data = models.JSONField(default=dict)
    complexity_old = models.JSONField(default=dict)
    complexity_new = models.JSONField(default=dict)
    plagiarism_data = models.JSONField(default=dict)
    warnings = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)

    class Meta:
        app_label = "codecompare"

    def __str__(self) -> str:
        return f"ComparisonResult({self.job_id}, {self.similarity_overall:.1f}%)"


class FileAnalysis(TimestampedModel):
    file_hash = models.CharField(max_length=64, unique=True, db_index=True)
    filename = models.CharField(max_length=512, blank=True)
    language = models.CharField(max_length=50)
    file_size = models.IntegerField(default=0)
    line_count = models.IntegerField(default=0)
    token_count = models.IntegerField(default=0)
    complexity_data = models.JSONField(default=dict)
    ast_summary = models.JSONField(default=dict)

    class Meta:
        app_label = "codecompare"
        ordering = ["-created_at"]


class SimilarityResult(TimestampedModel):
    old_hash = models.CharField(max_length=64, db_index=True)
    new_hash = models.CharField(max_length=64, db_index=True)
    language = models.CharField(max_length=50)
    overall = models.FloatField(default=0.0)
    exact = models.FloatField(default=0.0)
    semantic = models.FloatField(default=0.0)
    structural = models.FloatField(default=0.0)
    token = models.FloatField(default=0.0)
    ast = models.FloatField(default=0.0)

    class Meta:
        app_label = "codecompare"
        unique_together = [("old_hash", "new_hash", "language")]

    def __str__(self) -> str:
        return f"SimilarityResult({self.old_hash[:8]} vs {self.new_hash[:8]}, {self.overall:.1f}%)"
