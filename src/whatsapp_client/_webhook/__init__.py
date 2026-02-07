from __future__ import annotations

import hashlib
import hmac
import json
from collections.abc import Awaitable, Callable
from typing import Any

from .._client import WhatsAppClient
from .._exceptions import WhatsAppError
from ._types import (
    ButtonReplyContent,
    Conversation,
    ConversationOrigin,
    ListReplyContent,
    LocationContent,
    MediaContent,
    Message,
    MessageContext,
    Pricing,
    ReactionContent,
    Status,
    StatusError,
    TextContent,
    UnsupportedContent,
    WebhookContact,
    WebhookMetadata,
    WebhookNotification,
)


class WebhookVerificationError(WhatsAppError): ...


MessageCallback = Callable[[WhatsAppClient, WebhookNotification, Message], Awaitable[None]]
StatusCallback = Callable[[WhatsAppClient, WebhookNotification, Status], Awaitable[None]]


def verify_signature(*, body: bytes, signature: str, app_secret: str) -> None:
    if not signature.startswith("sha256="):
        raise WebhookVerificationError("Invalid signature format: missing 'sha256=' prefix")
    expected = hmac.new(app_secret.encode(), body, hashlib.sha256).hexdigest()
    received = signature.removeprefix("sha256=")
    if not hmac.compare_digest(expected, received):
        raise WebhookVerificationError("Signature mismatch")


def verify_challenge(*, mode: str, token: str, challenge: str, verify_token: str) -> str:
    if mode != "subscribe":
        raise WebhookVerificationError(f"Unexpected mode: {mode}")
    if token != verify_token:
        raise WebhookVerificationError("Token mismatch")
    return challenge


class WebhookHandler:
    def __init__(
        self,
        *,
        app_secret: str,
        client: WhatsAppClient,
        on_message: MessageCallback | None = None,
        on_status: StatusCallback | None = None,
    ) -> None:
        self._app_secret = app_secret
        self._client = client
        self._on_message = on_message
        self._on_status = on_status

    def on_message(self, func: MessageCallback) -> MessageCallback:
        self._on_message = func
        return func

    def on_status(self, func: StatusCallback) -> StatusCallback:
        self._on_status = func
        return func

    async def handle(self, *, body: bytes, signature: str) -> None:
        verify_signature(body=body, signature=signature, app_secret=self._app_secret)
        data: dict[str, Any] = json.loads(body)
        notifications = WebhookNotification.from_dict(data)
        for notification in notifications:
            if self._on_message is not None:
                for message in notification.messages:
                    await self._on_message(self._client, notification, message)
            if self._on_status is not None:
                for status in notification.statuses:
                    await self._on_status(self._client, notification, status)


__all__ = [
    "ButtonReplyContent",
    "Conversation",
    "ConversationOrigin",
    "ListReplyContent",
    "LocationContent",
    "MediaContent",
    "Message",
    "MessageContext",
    "Pricing",
    "ReactionContent",
    "Status",
    "StatusError",
    "TextContent",
    "UnsupportedContent",
    "WebhookContact",
    "WebhookHandler",
    "WebhookMetadata",
    "WebhookNotification",
    "WebhookVerificationError",
    "verify_challenge",
    "verify_signature",
]
