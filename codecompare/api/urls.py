"""URL patterns for the codecompare REST API."""
from django.urls import path

from codecompare.api.views import CompareView, FileCompareView, LanguageListView

app_name = "codecompare"

urlpatterns = [
    path("compare/", CompareView.as_view(), name="compare"),
    path("compare/files/", FileCompareView.as_view(), name="compare-files"),
    path("languages/", LanguageListView.as_view(), name="languages"),
]
