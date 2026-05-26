"""Root URL configuration."""
import django
import sys

from django.shortcuts import render
from django.urls import include, path


def home(request):
    return render(request, "home.html", {
        "python_version": sys.version.split()[0],
        "django_version": django.__version__,
    })


urlpatterns = [
    path("", home, name="home"),
    path("api/", include("codecompare.api.urls", namespace="codecompare")),
]

try:
    from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
    urlpatterns += [
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    ]
except ImportError:
    pass
