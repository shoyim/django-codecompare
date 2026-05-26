"""Initial database migration for codecompare."""
from __future__ import annotations
import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies: list = []

    operations = [
        migrations.CreateModel(
            name="ComparisonJob",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("status", models.CharField(
                    choices=[
                        ("pending", "Pending"),
                        ("processing", "Processing"),
                        ("completed", "Completed"),
                        ("failed", "Failed"),
                    ],
                    default="pending",
                    max_length=20,
                )),
                ("language", models.CharField(blank=True, max_length=50)),
                ("old_code", models.TextField()),
                ("new_code", models.TextField()),
                ("task_id", models.CharField(blank=True, max_length=255)),
                ("error_message", models.TextField(blank=True)),
                ("options", models.JSONField(default=dict)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="ComparisonResult",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("job", models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="result",
                    to="codecompare.comparisonjob",
                )),
                ("overall_similarity", models.FloatField(default=0.0)),
                ("exact_similarity", models.FloatField(default=0.0)),
                ("token_similarity", models.FloatField(default=0.0)),
                ("cosine_similarity", models.FloatField(default=0.0)),
                ("jaccard_similarity", models.FloatField(default=0.0)),
                ("ast_similarity", models.FloatField(default=0.0)),
                ("plagiarism_score", models.FloatField(default=0.0)),
                ("plagiarism_confidence", models.CharField(max_length=20, default="low")),
                ("lines_added", models.IntegerField(default=0)),
                ("lines_removed", models.IntegerField(default=0)),
                ("lines_equal", models.IntegerField(default=0)),
                ("diff_chunks", models.JSONField(default=list)),
                ("complexity_old", models.JSONField(default=dict)),
                ("complexity_new", models.JSONField(default=dict)),
                ("renamed_symbols", models.JSONField(default=list)),
                ("fingerprint_old", models.JSONField(default=list)),
                ("fingerprint_new", models.JSONField(default=list)),
                ("language_detected", models.CharField(max_length=50, blank=True)),
                ("processing_time_ms", models.FloatField(default=0.0)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="FileAnalysis",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("filename", models.CharField(max_length=500)),
                ("language", models.CharField(max_length=50)),
                ("content_hash", models.CharField(max_length=64)),
                ("line_count", models.IntegerField(default=0)),
                ("cyclomatic_complexity", models.FloatField(default=0.0)),
                ("halstead_volume", models.FloatField(default=0.0)),
                ("maintainability_index", models.FloatField(default=0.0)),
                ("analysis_data", models.JSONField(default=dict)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="SimilarityResult",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("file_a", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="similarities_as_a",
                    to="codecompare.fileanalysis",
                )),
                ("file_b", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="similarities_as_b",
                    to="codecompare.fileanalysis",
                )),
                ("overall_score", models.FloatField(default=0.0)),
                ("is_duplicate", models.BooleanField(default=False)),
            ],
            options={"abstract": False},
        ),
    ]
