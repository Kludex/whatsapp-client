from __future__ import annotations

from dataclasses import asdict
from typing import Any

import httpx

from ._exceptions import WhatsAppAPIError, GraphAPIErrorBody
from ._types import (
    Contact,
    ContactInfo,
    GroupInfo,
    GroupInviteLink,
    GroupJoinRequest,
    GroupParticipant,
    GroupSummary,
    ListSection,
    MessageId,
    MessageResponse,
    ReplyButton,
    Template,
    TemplateBodyComponent,
    TemplateButtonComponent,
    TemplateComponent,
    TemplateDocumentParameter,
    TemplateHeaderComponent,
    TemplateImageParameter,
    TemplateParameter,
    TemplateTextParameter,
    TemplateVideoParameter,
)


class WhatsAppClient:
    def __init__(
        self, *, phone_number_id: str, access_token: str, base_url: str = "https://graph.facebook.com/v22.0"
    ) -> None:
        self._phone_number_id = phone_number_id
        self._access_token = access_token
        self._base_url = base_url
        self._http = httpx.AsyncClient(
            base_url=f"{base_url}/{phone_number_id}", headers={"Authorization": f"Bearer {access_token}"}
        )

    async def __aenter__(self) -> WhatsAppClient:
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: object
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._http.aclose()

    # --- Private helpers ---

    async def _api(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        url = f"{self._base_url}/{path}"
        response = await self._http.request(method, url, **kwargs)
        if response.status_code >= 400:
            body: GraphAPIErrorBody = response.json()
            raise WhatsAppAPIError.from_response(response.status_code, body)
        data: dict[str, Any] = response.json()
        return data

    async def _send(self, payload: dict[str, Any]) -> MessageResponse:
        payload["messaging_product"] = "whatsapp"
        if "@g.us" in payload.get("to", ""):
            payload["recipient_type"] = "group"
        response = await self._http.post("/messages", json=payload)
        if response.status_code >= 400:
            body: GraphAPIErrorBody = response.json()
            raise WhatsAppAPIError.from_response(response.status_code, body)
        data: dict[str, Any] = response.json()
        return MessageResponse(
            messaging_product=data["messaging_product"],
            contacts=[Contact(input=c["input"], wa_id=c["wa_id"]) for c in data["contacts"]],
            messages=[MessageId(id=m["id"]) for m in data["messages"]],
        )

    @staticmethod
    def _serialize_parameter(param: TemplateParameter) -> dict[str, Any]:
        match param:
            case TemplateTextParameter(text=text):
                return {"type": "text", "text": text}
            case TemplateImageParameter(link=link):
                return {"type": "image", "image": {"link": link}}
            case TemplateVideoParameter(link=link):
                return {"type": "video", "video": {"link": link}}
            case TemplateDocumentParameter(link=link, filename=filename):
                doc: dict[str, str] = {"link": link}
                if filename is not None:
                    doc["filename"] = filename
                return {"type": "document", "document": doc}

    @staticmethod
    def _serialize_component(component: TemplateComponent) -> dict[str, Any]:
        match component:
            case TemplateHeaderComponent(parameters=parameters):
                return {"type": "header", "parameters": [WhatsAppClient._serialize_parameter(p) for p in parameters]}
            case TemplateBodyComponent(parameters=parameters):
                return {"type": "body", "parameters": [WhatsAppClient._serialize_parameter(p) for p in parameters]}
            case TemplateButtonComponent(sub_type=sub_type, index=index, parameters=parameters):
                return {
                    "type": "button",
                    "sub_type": sub_type,
                    "index": str(index),
                    "parameters": [WhatsAppClient._serialize_parameter(p) for p in parameters],
                }

    @staticmethod
    def _serialize_contact(contact: ContactInfo) -> dict[str, Any]:
        raw = asdict(contact)
        return {k: v for k, v in raw.items() if v is not None}

    # --- Public send methods ---

    async def send_text(self, *, to: str, body: str, preview_url: bool = False) -> MessageResponse:
        return await self._send({"to": to, "type": "text", "text": {"body": body, "preview_url": preview_url}})

    async def send_image(self, *, to: str, link: str, caption: str | None = None) -> MessageResponse:
        image: dict[str, str] = {"link": link}
        if caption is not None:
            image["caption"] = caption
        return await self._send({"to": to, "type": "image", "image": image})

    async def send_audio(self, *, to: str, link: str) -> MessageResponse:
        return await self._send({"to": to, "type": "audio", "audio": {"link": link}})

    async def send_video(self, *, to: str, link: str, caption: str | None = None) -> MessageResponse:
        video: dict[str, str] = {"link": link}
        if caption is not None:
            video["caption"] = caption
        return await self._send({"to": to, "type": "video", "video": video})

    async def send_document(
        self, *, to: str, link: str, caption: str | None = None, filename: str | None = None
    ) -> MessageResponse:
        document: dict[str, str] = {"link": link}
        if caption is not None:
            document["caption"] = caption
        if filename is not None:
            document["filename"] = filename
        return await self._send({"to": to, "type": "document", "document": document})

    async def send_sticker(self, *, to: str, link: str) -> MessageResponse:
        return await self._send({"to": to, "type": "sticker", "sticker": {"link": link}})

    async def send_location(
        self, *, to: str, latitude: float, longitude: float, name: str | None = None, address: str | None = None
    ) -> MessageResponse:
        location: dict[str, str | float] = {"latitude": latitude, "longitude": longitude}
        if name is not None:
            location["name"] = name
        if address is not None:
            location["address"] = address
        return await self._send({"to": to, "type": "location", "location": location})

    async def send_contacts(self, *, to: str, contacts: list[ContactInfo]) -> MessageResponse:
        return await self._send(
            {"to": to, "type": "contacts", "contacts": [self._serialize_contact(c) for c in contacts]}
        )

    async def send_template(self, *, to: str, template: Template) -> MessageResponse:
        tmpl: dict[str, Any] = {"name": template.name, "language": {"code": template.language.code}}
        if template.components is not None:
            tmpl["components"] = [self._serialize_component(c) for c in template.components]
        return await self._send({"to": to, "type": "template", "template": tmpl})

    async def send_buttons(
        self, *, to: str, body: str, buttons: list[ReplyButton], header: str | None = None, footer: str | None = None
    ) -> MessageResponse:
        action: dict[str, Any] = {
            "buttons": [{"type": "reply", "reply": {"id": b.id, "title": b.title}} for b in buttons]
        }
        interactive: dict[str, Any] = {"type": "button", "body": {"text": body}, "action": action}
        if header is not None:
            interactive["header"] = {"type": "text", "text": header}
        if footer is not None:
            interactive["footer"] = {"text": footer}
        return await self._send({"to": to, "type": "interactive", "interactive": interactive})

    async def send_list(
        self,
        *,
        to: str,
        body: str,
        button_text: str,
        sections: list[ListSection],
        header: str | None = None,
        footer: str | None = None,
    ) -> MessageResponse:
        serialized_sections: list[dict[str, Any]] = []
        for section in sections:
            rows: list[dict[str, str]] = []
            for row in section.rows:
                r: dict[str, str] = {"id": row.id, "title": row.title}
                if row.description is not None:
                    r["description"] = row.description
                rows.append(r)
            serialized_sections.append({"title": section.title, "rows": rows})

        interactive: dict[str, Any] = {
            "type": "list",
            "body": {"text": body},
            "action": {"button": button_text, "sections": serialized_sections},
        }
        if header is not None:
            interactive["header"] = {"type": "text", "text": header}
        if footer is not None:
            interactive["footer"] = {"text": footer}
        return await self._send({"to": to, "type": "interactive", "interactive": interactive})

    # --- Group management methods ---

    async def create_group(self, *, subject: str, participants: list[str]) -> GroupInfo:
        data = await self._api(
            "POST",
            f"{self._phone_number_id}/groups",
            json={"subject": subject, "participants": participants, "messaging_product": "whatsapp"},
        )
        return GroupInfo(
            id=data["id"],
            subject=data["subject"],
            owner=data["owner"],
            creation_timestamp=data["creation_timestamp"],
            participants=[
                GroupParticipant(phone_number=p["phone_number"], admin=p["admin"]) for p in data["participants"]
            ],
        )

    async def get_groups(self) -> list[GroupSummary]:
        data = await self._api("GET", f"{self._phone_number_id}/groups")
        return [GroupSummary(id=g["id"], subject=g["subject"]) for g in data.get("data", [])]

    async def get_group(self, group_id: str) -> GroupInfo:
        data = await self._api("GET", group_id)
        return GroupInfo(
            id=data["id"],
            subject=data["subject"],
            owner=data["owner"],
            creation_timestamp=data["creation_timestamp"],
            participants=[
                GroupParticipant(phone_number=p["phone_number"], admin=p["admin"]) for p in data["participants"]
            ],
        )

    async def update_group(self, group_id: str, *, subject: str | None = None, description: str | None = None) -> None:
        payload: dict[str, str] = {}
        if subject is not None:
            payload["subject"] = subject
        if description is not None:
            payload["description"] = description
        await self._api("POST", group_id, json=payload)

    async def delete_group(self, group_id: str) -> None:
        await self._api("DELETE", group_id)

    async def get_invite_link(self, group_id: str) -> GroupInviteLink:
        data = await self._api("GET", f"{group_id}/invite_link")
        return GroupInviteLink(link=data["invite_link"])

    async def reset_invite_link(self, group_id: str) -> GroupInviteLink:
        data = await self._api("POST", f"{group_id}/invite_link")
        return GroupInviteLink(link=data["invite_link"])

    async def remove_participants(self, group_id: str, *, participants: list[str]) -> None:
        await self._api("DELETE", f"{group_id}/participants", json={"participants": participants})

    async def get_join_requests(self, group_id: str) -> list[GroupJoinRequest]:
        data = await self._api("GET", f"{group_id}/join_requests")
        return [
            GroupJoinRequest(phone_number=r["phone_number"], timestamp=r["timestamp"]) for r in data.get("data", [])
        ]

    async def approve_join_requests(self, group_id: str, *, participants: list[str]) -> None:
        await self._api("POST", f"{group_id}/join_requests", json={"participants": participants})

    async def reject_join_requests(self, group_id: str, *, participants: list[str]) -> None:
        await self._api("DELETE", f"{group_id}/join_requests", json={"participants": participants})
