"""URL patterns for the codecompare REST API."""
from django.urls import path
from codecompare.api.views import (
    AsyncCompareView, CompareView, FileCompareView,
    JobResultView, JobStatusView, LanguageListView,
)

app_name = "codecompare"

urlpatterns = [
    path("compare/", CompareView.as_view(), name="compare"),
    path("compare/async/", AsyncCompareView.as_view(), name="compare-async"),
    path("compare/files/", FileCompareView.as_view(), name="compare-files"),
    path("jobs/<uuid:job_id>/", JobStatusView.as_view(), name="job-status"),
    path("jobs/<uuid:job_id>/result/", JobResultView.as_view(), name="job-result"),
    path("languages/", LanguageListView.as_view(), name="languages"),
]
