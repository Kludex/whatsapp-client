from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict


class ErrorData(TypedDict, total=False):
    details: str


class GraphAPIError(TypedDict, total=False):
    code: int
    type: str
    message: str
    error_subcode: int
    fbtrace_id: str
    error_data: ErrorData


class GraphAPIErrorBody(TypedDict, total=False):
    error: GraphAPIError


class WhatsAppError(Exception): ...


@dataclass
class WhatsAppAPIError(WhatsAppError):
    status_code: int
    error_code: int
    error_type: str
    message: str
    error_subcode: int | None = None
    fbtrace_id: str | None = None
    details: str | None = None

    def __str__(self) -> str:
        return f"[{self.error_code}] ({self.error_type}) {self.message}"

    @classmethod
    def from_response(cls, status_code: int, body: GraphAPIErrorBody) -> WhatsAppAPIError:
        error = body.get("error", {})
        error_data = error.get("error_data", {})
        return cls(
            status_code=status_code,
            error_code=error.get("code", 0),
            error_type=error.get("type", "unknown"),
            message=error.get("message", "Unknown error"),
            error_subcode=error.get("error_subcode"),
            fbtrace_id=error.get("fbtrace_id"),
            details=error_data.get("details"),
        )
