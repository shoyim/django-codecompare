"""REST API views — stateless code comparison."""
from __future__ import annotations
import dataclasses
import logging
from typing import Any

from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from codecompare.core.exceptions import CodeCompareError, FileSizeLimitError, SecurityError
from codecompare.core.services import ComparisonService
from codecompare.core.types import Language
from codecompare.utils.security import validate_upload

logger = logging.getLogger(__name__)
_MAX_FILE_SIZE = 100 * 1024 * 1024


def _exception_handler(exc, context):
    from rest_framework.views import exception_handler
    response = exception_handler(exc, context)
    if response is None and isinstance(exc, CodeCompareError):
        return Response(exc.to_dict(), status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    return response


def _result_to_dict(result) -> dict[str, Any]:
    return {
        "language": result.language,
        "similarity": dataclasses.asdict(result.similarity),
        "statistics": dataclasses.asdict(result.statistics),
        "diff": {
            "chunks": [
                {
                    "old_start": c.old_start, "old_count": c.old_count,
                    "new_start": c.new_start, "new_count": c.new_count,
                    "header": c.header,
                    "lines": [
                        {"old_no": l.old_no, "new_no": l.new_no,
                         "content": l.content, "change_type": l.change_type.value}
                        for l in c.lines
                    ],
                }
                for c in result.diff.chunks
            ],
            "added": result.diff.added,
            "removed": result.diff.removed,
            "equal": result.diff.equal,
            "mode": result.diff.mode.value,
        },
        "ast_diff": result.ast_diff,
        "old_complexity": dataclasses.asdict(result.old_complexity),
        "new_complexity": dataclasses.asdict(result.new_complexity),
        "plagiarism": dataclasses.asdict(result.plagiarism),
        "warnings": result.warnings,
        "metadata": result.metadata,
        "processing_time_ms": result.processing_time_ms,
    }


class CompareView(APIView):
    """POST /api/compare/ — compare two code snippets."""
    throttle_classes = [AnonRateThrottle]
    parser_classes = [JSONParser]

    def post(self, request: Request) -> Response:
        old_code = request.data.get("old_code", "")
        new_code = request.data.get("new_code", "")
        language = request.data.get("language") or None
        options = request.data.get("options", {})

        if language == "auto":
            language = None

        if not old_code or not new_code:
            return Response(
                {"error": "MISSING_FIELDS", "message": "old_code and new_code are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        for name, code in [("old_code", old_code), ("new_code", new_code)]:
            if len(str(code).encode()) > _MAX_FILE_SIZE:
                return Response(
                    {"error": "FILE_SIZE_LIMIT", "message": f"{name} exceeds 100MB limit"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            result = ComparisonService().compare(str(old_code), str(new_code), language, options)
        except CodeCompareError as exc:
            logger.warning("Comparison error: %s", exc)
            return Response(exc.to_dict(), status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Exception as exc:
            logger.exception("Unexpected error in CompareView")
            return Response(
                {"error": "INTERNAL_ERROR", "message": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(_result_to_dict(result), status=status.HTTP_200_OK)


class FileCompareView(APIView):
    """POST /api/compare/files/ — compare two uploaded files."""
    parser_classes = [MultiPartParser, FormParser]
    throttle_classes = [AnonRateThrottle]

    def post(self, request: Request) -> Response:
        old_file = request.FILES.get("old_file")
        new_file = request.FILES.get("new_file")

        if not old_file or not new_file:
            return Response(
                {"error": "Both old_file and new_file are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_upload(old_file)
            validate_upload(new_file)
        except SecurityError as exc:
            return Response(exc.to_dict(), status=status.HTTP_400_BAD_REQUEST)

        old_code = old_file.read().decode("utf-8", errors="replace")
        new_code = new_file.read().decode("utf-8", errors="replace")
        language = request.data.get("language") or None

        try:
            result = ComparisonService().compare(old_code, new_code, language)
        except CodeCompareError as exc:
            return Response(exc.to_dict(), status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        return Response(_result_to_dict(result))


class LanguageListView(APIView):
    """GET /api/languages/ — list supported languages."""
    def get(self, request: Request) -> Response:
        languages = [
            {"id": lang.value, "name": lang.value.title()}
            for lang in Language if lang != Language.UNKNOWN
        ]
        return Response({"languages": languages})
