from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Union


# --- Webhook payload types ---


@dataclass(frozen=True, slots=True, kw_only=True)
class WebhookMetadata:
    display_phone_number: str
    phone_number_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class WebhookContact:
    wa_id: str
    name: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class MessageContext:
    from_: str
    id: str


# --- Message content types ---


@dataclass(frozen=True, slots=True, kw_only=True)
class TextContent:
    body: str


@dataclass(frozen=True, slots=True, kw_only=True)
class MediaContent:
    id: str
    mime_type: str
    sha256: str
    caption: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class LocationContent:
    latitude: float
    longitude: float
    name: str | None = None
    address: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ButtonReplyContent:
    id: str
    title: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ListReplyContent:
    id: str
    title: str
    description: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ReactionContent:
    message_id: str
    emoji: str


@dataclass(frozen=True, slots=True, kw_only=True)
class UnsupportedContent:
    raw: dict[str, Any]


MessageContent = Union[
    TextContent,
    MediaContent,
    LocationContent,
    ButtonReplyContent,
    ListReplyContent,
    ReactionContent,
    UnsupportedContent,
]


# --- Message ---


@dataclass(frozen=True, slots=True, kw_only=True)
class Message:
    id: str
    from_: str
    timestamp: str
    type: str
    content: MessageContent
    context: MessageContext | None = None


# --- Status types ---


@dataclass(frozen=True, slots=True, kw_only=True)
class StatusError:
    code: int
    title: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ConversationOrigin:
    type: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Conversation:
    id: str
    origin: ConversationOrigin


@dataclass(frozen=True, slots=True, kw_only=True)
class Pricing:
    billable: bool
    pricing_model: str
    category: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Status:
    id: str
    status: str
    timestamp: str
    recipient_id: str
    conversation: Conversation | None = None
    pricing: Pricing | None = None
    errors: list[StatusError] | None = None


# --- Top-level notification ---


@dataclass(frozen=True, slots=True, kw_only=True)
class WebhookNotification:
    metadata: WebhookMetadata
    contacts: list[WebhookContact]
    messages: list[Message]
    statuses: list[Status]

    @staticmethod
    def _parse_content(msg: dict[str, Any]) -> MessageContent:
        msg_type = msg.get("type", "")
        match msg_type:
            case "text":
                text = msg["text"]
                return TextContent(body=text["body"])
            case "image" | "video" | "audio" | "document" | "sticker":
                media = msg[msg_type]
                return MediaContent(
                    id=media["id"], mime_type=media["mime_type"], sha256=media["sha256"], caption=media.get("caption")
                )
            case "location":
                loc = msg["location"]
                return LocationContent(
                    latitude=loc["latitude"],
                    longitude=loc["longitude"],
                    name=loc.get("name"),
                    address=loc.get("address"),
                )
            case "button":
                button = msg["button"]
                return ButtonReplyContent(id=button["payload"], title=button["text"])
            case "interactive":
                interactive = msg["interactive"]
                interactive_type = interactive.get("type", "")
                if interactive_type == "button_reply":
                    reply = interactive["button_reply"]
                    return ButtonReplyContent(id=reply["id"], title=reply["title"])
                elif interactive_type == "list_reply":
                    reply = interactive["list_reply"]
                    return ListReplyContent(id=reply["id"], title=reply["title"], description=reply.get("description"))
                return UnsupportedContent(raw=msg)
            case "reaction":
                reaction = msg["reaction"]
                return ReactionContent(message_id=reaction["message_id"], emoji=reaction["emoji"])
            case _:
                return UnsupportedContent(raw=msg)

    @staticmethod
    def _parse_message(msg: dict[str, Any]) -> Message:
        context: MessageContext | None = None
        if "context" in msg:
            ctx = msg["context"]
            context = MessageContext(from_=ctx["from"], id=ctx["id"])
        return Message(
            id=msg["id"],
            from_=msg["from"],
            timestamp=msg["timestamp"],
            type=msg.get("type", ""),
            content=WebhookNotification._parse_content(msg),
            context=context,
        )

    @staticmethod
    def _parse_status(raw: dict[str, Any]) -> Status:
        conversation: Conversation | None = None
        if "conversation" in raw:
            conv = raw["conversation"]
            conversation = Conversation(id=conv["id"], origin=ConversationOrigin(type=conv["origin"]["type"]))
        pricing: Pricing | None = None
        if "pricing" in raw:
            p = raw["pricing"]
            pricing = Pricing(billable=p["billable"], pricing_model=p["pricing_model"], category=p["category"])
        errors: list[StatusError] | None = None
        if "errors" in raw:
            errors = [StatusError(code=e["code"], title=e["title"]) for e in raw["errors"]]
        return Status(
            id=raw["id"],
            status=raw["status"],
            timestamp=raw["timestamp"],
            recipient_id=raw["recipient_id"],
            conversation=conversation,
            pricing=pricing,
            errors=errors,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> list[WebhookNotification]:
        notifications: list[WebhookNotification] = []
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                meta = value.get("metadata", {})
                metadata = WebhookMetadata(
                    display_phone_number=meta.get("display_phone_number", ""),
                    phone_number_id=meta.get("phone_number_id", ""),
                )
                contacts = [
                    WebhookContact(wa_id=c["wa_id"], name=c.get("profile", {}).get("name"))
                    for c in value.get("contacts", [])
                ]
                messages = [cls._parse_message(m) for m in value.get("messages", [])]
                statuses = [cls._parse_status(s) for s in value.get("statuses", [])]
                notifications.append(
                    WebhookNotification(metadata=metadata, contacts=contacts, messages=messages, statuses=statuses)
                )
        return notifications
