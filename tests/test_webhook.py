from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any
from unittest.mock import AsyncMock

import pytest

from whatsapp_client import (
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
    WebhookHandler,
    WebhookMetadata,
    WebhookNotification,
    WebhookVerificationError,
    WhatsAppClient,
    verify_challenge,
    verify_signature,
)

APP_SECRET = "test_app_secret"


def _sign(body: bytes, secret: str = APP_SECRET) -> str:
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def _wrap_payload(value: dict[str, Any]) -> dict[str, Any]:
    return {
        "object": "whatsapp_business_account",
        "entry": [{"id": "BIZ_ID", "changes": [{"value": value, "field": "messages"}]}],
    }


METADATA = {"display_phone_number": "15550001111", "phone_number_id": "123456"}


# --- Signature verification ---


class TestVerifySignature:
    def test_valid(self) -> None:
        body = b'{"test": true}'
        verify_signature(body=body, signature=_sign(body), app_secret=APP_SECRET)

    def test_invalid_signature(self) -> None:
        with pytest.raises(WebhookVerificationError, match="Signature mismatch"):
            verify_signature(body=b"body", signature="sha256=bad", app_secret=APP_SECRET)

    def test_bad_format(self) -> None:
        with pytest.raises(WebhookVerificationError, match="missing 'sha256=' prefix"):
            verify_signature(body=b"body", signature="invalid", app_secret=APP_SECRET)


# --- Challenge verification ---


class TestVerifyChallenge:
    def test_valid(self) -> None:
        result = verify_challenge(
            mode="subscribe", token="mytoken", challenge="challenge_string", verify_token="mytoken"
        )
        assert result == "challenge_string"

    def test_wrong_token(self) -> None:
        with pytest.raises(WebhookVerificationError, match="Token mismatch"):
            verify_challenge(mode="subscribe", token="wrong", challenge="c", verify_token="mytoken")

    def test_wrong_mode(self) -> None:
        with pytest.raises(WebhookVerificationError, match="Unexpected mode"):
            verify_challenge(mode="unsubscribe", token="mytoken", challenge="c", verify_token="mytoken")


# --- Payload parsing ---


class TestParseTextMessage:
    def test_text(self) -> None:
        payload = _wrap_payload(
            {
                "metadata": METADATA,
                "contacts": [{"wa_id": "5511999999999", "profile": {"name": "John"}}],
                "messages": [
                    {
                        "id": "wamid.abc",
                        "from": "5511999999999",
                        "timestamp": "1700000000",
                        "type": "text",
                        "text": {"body": "Hello"},
                    }
                ],
            }
        )
        notifications = WebhookNotification.from_dict(payload)
        assert len(notifications) == 1
        n = notifications[0]
        assert n.metadata == WebhookMetadata(display_phone_number="15550001111", phone_number_id="123456")
        assert n.contacts == [WebhookContact(wa_id="5511999999999", name="John")]
        assert len(n.messages) == 1
        msg = n.messages[0]
        assert msg.id == "wamid.abc"
        assert msg.from_ == "5511999999999"
        assert msg.type == "text"
        assert msg.content == TextContent(body="Hello")
        assert msg.context is None


class TestParseImageMessage:
    def test_image(self) -> None:
        payload = _wrap_payload(
            {
                "metadata": METADATA,
                "messages": [
                    {
                        "id": "wamid.img",
                        "from": "5511999999999",
                        "timestamp": "1700000000",
                        "type": "image",
                        "image": {
                            "id": "media_id_123",
                            "mime_type": "image/jpeg",
                            "sha256": "abc123",
                            "caption": "Look!",
                        },
                    }
                ],
            }
        )
        msg = WebhookNotification.from_dict(payload)[0].messages[0]
        assert msg.type == "image"
        assert msg.content == MediaContent(id="media_id_123", mime_type="image/jpeg", sha256="abc123", caption="Look!")


class TestParseDocumentMessage:
    def test_document_no_caption(self) -> None:
        payload = _wrap_payload(
            {
                "metadata": METADATA,
                "messages": [
                    {
                        "id": "wamid.doc",
                        "from": "5511999999999",
                        "timestamp": "1700000000",
                        "type": "document",
                        "document": {"id": "media_doc", "mime_type": "application/pdf", "sha256": "def456"},
                    }
                ],
            }
        )
        msg = WebhookNotification.from_dict(payload)[0].messages[0]
        assert msg.type == "document"
        assert msg.content == MediaContent(id="media_doc", mime_type="application/pdf", sha256="def456", caption=None)


class TestParseLocationMessage:
    def test_location(self) -> None:
        payload = _wrap_payload(
            {
                "metadata": METADATA,
                "messages": [
                    {
                        "id": "wamid.loc",
                        "from": "5511999999999",
                        "timestamp": "1700000000",
                        "type": "location",
                        "location": {"latitude": 48.8566, "longitude": 2.3522, "name": "Paris", "address": "France"},
                    }
                ],
            }
        )
        msg = WebhookNotification.from_dict(payload)[0].messages[0]
        assert msg.content == LocationContent(latitude=48.8566, longitude=2.3522, name="Paris", address="France")


class TestParseButtonReply:
    def test_interactive_button_reply(self) -> None:
        payload = _wrap_payload(
            {
                "metadata": METADATA,
                "messages": [
                    {
                        "id": "wamid.btn",
                        "from": "5511999999999",
                        "timestamp": "1700000000",
                        "type": "interactive",
                        "interactive": {"type": "button_reply", "button_reply": {"id": "btn_1", "title": "Yes"}},
                    }
                ],
            }
        )
        msg = WebhookNotification.from_dict(payload)[0].messages[0]
        assert msg.content == ButtonReplyContent(id="btn_1", title="Yes")

    def test_quick_reply_button(self) -> None:
        payload = _wrap_payload(
            {
                "metadata": METADATA,
                "messages": [
                    {
                        "id": "wamid.qr",
                        "from": "5511999999999",
                        "timestamp": "1700000000",
                        "type": "button",
                        "button": {"payload": "btn_payload", "text": "Quick Reply"},
                    }
                ],
            }
        )
        msg = WebhookNotification.from_dict(payload)[0].messages[0]
        assert msg.content == ButtonReplyContent(id="btn_payload", title="Quick Reply")


class TestParseListReply:
    def test_list_reply(self) -> None:
        payload = _wrap_payload(
            {
                "metadata": METADATA,
                "messages": [
                    {
                        "id": "wamid.list",
                        "from": "5511999999999",
                        "timestamp": "1700000000",
                        "type": "interactive",
                        "interactive": {
                            "type": "list_reply",
                            "list_reply": {"id": "row_1", "title": "Option A", "description": "First option"},
                        },
                    }
                ],
            }
        )
        msg = WebhookNotification.from_dict(payload)[0].messages[0]
        assert msg.content == ListReplyContent(id="row_1", title="Option A", description="First option")


class TestParseReaction:
    def test_reaction(self) -> None:
        payload = _wrap_payload(
            {
                "metadata": METADATA,
                "messages": [
                    {
                        "id": "wamid.react",
                        "from": "5511999999999",
                        "timestamp": "1700000000",
                        "type": "reaction",
                        "reaction": {"message_id": "wamid.original", "emoji": "\U0001f44d"},
                    }
                ],
            }
        )
        msg = WebhookNotification.from_dict(payload)[0].messages[0]
        assert msg.content == ReactionContent(message_id="wamid.original", emoji="\U0001f44d")


class TestParseMessageWithContext:
    def test_context(self) -> None:
        payload = _wrap_payload(
            {
                "metadata": METADATA,
                "messages": [
                    {
                        "id": "wamid.reply",
                        "from": "5511999999999",
                        "timestamp": "1700000000",
                        "type": "text",
                        "text": {"body": "Reply"},
                        "context": {"from": "15550001111", "id": "wamid.original"},
                    }
                ],
            }
        )
        msg = WebhookNotification.from_dict(payload)[0].messages[0]
        assert msg.context == MessageContext(from_="15550001111", id="wamid.original")


class TestParseStatus:
    def test_status_sent(self) -> None:
        payload = _wrap_payload(
            {
                "metadata": METADATA,
                "statuses": [
                    {
                        "id": "wamid.status1",
                        "status": "sent",
                        "timestamp": "1700000000",
                        "recipient_id": "5511999999999",
                        "conversation": {"id": "conv_123", "origin": {"type": "business_initiated"}},
                        "pricing": {"billable": True, "pricing_model": "CBP", "category": "business_initiated"},
                    }
                ],
            }
        )
        n = WebhookNotification.from_dict(payload)[0]
        assert len(n.statuses) == 1
        s = n.statuses[0]
        assert s == Status(
            id="wamid.status1",
            status="sent",
            timestamp="1700000000",
            recipient_id="5511999999999",
            conversation=Conversation(id="conv_123", origin=ConversationOrigin(type="business_initiated")),
            pricing=Pricing(billable=True, pricing_model="CBP", category="business_initiated"),
        )

    def test_status_with_errors(self) -> None:
        payload = _wrap_payload(
            {
                "metadata": METADATA,
                "statuses": [
                    {
                        "id": "wamid.fail",
                        "status": "failed",
                        "timestamp": "1700000000",
                        "recipient_id": "5511999999999",
                        "errors": [{"code": 131047, "title": "Message failed to send"}],
                    }
                ],
            }
        )
        s = WebhookNotification.from_dict(payload)[0].statuses[0]
        assert s.errors == [StatusError(code=131047, title="Message failed to send")]
        assert s.conversation is None
        assert s.pricing is None


class TestParseUnsupported:
    def test_unknown_type(self) -> None:
        payload = _wrap_payload(
            {
                "metadata": METADATA,
                "messages": [
                    {
                        "id": "wamid.unk",
                        "from": "5511999999999",
                        "timestamp": "1700000000",
                        "type": "contacts",
                        "contacts": [{}],
                    }
                ],
            }
        )
        msg = WebhookNotification.from_dict(payload)[0].messages[0]
        assert isinstance(msg.content, UnsupportedContent)

    def test_unsupported_interactive_type(self) -> None:
        payload = _wrap_payload(
            {
                "metadata": METADATA,
                "messages": [
                    {
                        "id": "wamid.unk2",
                        "from": "5511999999999",
                        "timestamp": "1700000000",
                        "type": "interactive",
                        "interactive": {"type": "unknown_type"},
                    }
                ],
            }
        )
        msg = WebhookNotification.from_dict(payload)[0].messages[0]
        assert isinstance(msg.content, UnsupportedContent)


class TestParseEmptyPayload:
    def test_no_entries(self) -> None:
        assert WebhookNotification.from_dict({}) == []

    def test_empty_value(self) -> None:
        payload = _wrap_payload({"metadata": METADATA})
        n = WebhookNotification.from_dict(payload)[0]
        assert n.messages == []
        assert n.statuses == []
        assert n.contacts == []


# --- Handler dispatching ---


class TestWebhookHandler:
    @pytest.fixture
    def client(self) -> WhatsAppClient:
        return WhatsAppClient(phone_number_id="123456", access_token="token")

    def _make_handler(self, client: WhatsAppClient, **kwargs: Any) -> WebhookHandler:
        return WebhookHandler(app_secret=APP_SECRET, client=client, **kwargs)

    def _signed_body(self, payload: dict[str, Any]) -> tuple[bytes, str]:
        body = json.dumps(payload).encode()
        return body, _sign(body)

    async def test_on_message_dispatch(self, client: WhatsAppClient) -> None:
        on_message = AsyncMock()
        handler = self._make_handler(client, on_message=on_message)
        payload = _wrap_payload(
            {
                "metadata": METADATA,
                "messages": [
                    {
                        "id": "wamid.1",
                        "from": "5511999999999",
                        "timestamp": "1700000000",
                        "type": "text",
                        "text": {"body": "Hi"},
                    }
                ],
            }
        )
        body, sig = self._signed_body(payload)
        await handler.handle(body=body, signature=sig)
        on_message.assert_awaited_once()
        assert on_message.await_args is not None
        _, notification, message = on_message.await_args.args
        assert isinstance(notification, WebhookNotification)
        assert message.content == TextContent(body="Hi")

    async def test_on_status_dispatch(self, client: WhatsAppClient) -> None:
        on_status = AsyncMock()
        handler = self._make_handler(client, on_status=on_status)
        payload = _wrap_payload(
            {
                "metadata": METADATA,
                "statuses": [
                    {
                        "id": "wamid.s1",
                        "status": "delivered",
                        "timestamp": "1700000000",
                        "recipient_id": "5511999999999",
                    }
                ],
            }
        )
        body, sig = self._signed_body(payload)
        await handler.handle(body=body, signature=sig)
        on_status.assert_awaited_once()
        assert on_status.await_args is not None
        _, _, status = on_status.await_args.args
        assert status.status == "delivered"

    async def test_no_handler_registered(self, client: WhatsAppClient) -> None:
        handler = self._make_handler(client)
        payload = _wrap_payload(
            {
                "metadata": METADATA,
                "messages": [
                    {
                        "id": "wamid.1",
                        "from": "5511999999999",
                        "timestamp": "1700000000",
                        "type": "text",
                        "text": {"body": "Hi"},
                    }
                ],
            }
        )
        body, sig = self._signed_body(payload)
        await handler.handle(body=body, signature=sig)  # should not raise

    async def test_signature_rejection(self, client: WhatsAppClient) -> None:
        handler = self._make_handler(client)
        with pytest.raises(WebhookVerificationError):
            await handler.handle(body=b"body", signature="sha256=bad")

    async def test_decorator_overrides_constructor(self, client: WhatsAppClient) -> None:
        constructor_cb = AsyncMock()
        decorator_cb = AsyncMock()
        handler = self._make_handler(client, on_message=constructor_cb)

        @handler.on_message
        async def handle_message(c: WhatsAppClient, n: WebhookNotification, m: Message) -> None:
            await decorator_cb(c, n, m)

        _ = handle_message  # registered via decorator

        payload = _wrap_payload(
            {
                "metadata": METADATA,
                "messages": [
                    {
                        "id": "wamid.1",
                        "from": "5511999999999",
                        "timestamp": "1700000000",
                        "type": "text",
                        "text": {"body": "Hi"},
                    }
                ],
            }
        )
        body, sig = self._signed_body(payload)
        await handler.handle(body=body, signature=sig)
        constructor_cb.assert_not_awaited()
        decorator_cb.assert_awaited_once()

    async def test_client_passed_to_callback(self, client: WhatsAppClient) -> None:
        on_message = AsyncMock()
        handler = self._make_handler(client, on_message=on_message)
        payload = _wrap_payload(
            {
                "metadata": METADATA,
                "messages": [
                    {
                        "id": "wamid.1",
                        "from": "5511999999999",
                        "timestamp": "1700000000",
                        "type": "text",
                        "text": {"body": "Hi"},
                    }
                ],
            }
        )
        body, sig = self._signed_body(payload)
        await handler.handle(body=body, signature=sig)
        assert on_message.await_args is not None
        passed_client = on_message.await_args.args[0]
        assert passed_client is client
