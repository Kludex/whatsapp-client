from __future__ import annotations

import pytest
from inline_snapshot import snapshot

from whatsapp_client import Contact, MessageId, MessageResponse, Template, TemplateLanguage, WhatsAppClient


@pytest.mark.vcr
async def test_send_template(whatsapp_client: WhatsAppClient) -> None:
    response = await whatsapp_client.send_template(
        to="33788813966", template=Template(name="hello_world", language=TemplateLanguage(code="en_US"))
    )
    assert response == snapshot(
        MessageResponse(
            messaging_product="whatsapp",
            contacts=[Contact(input="33788813966", wa_id="33788813966")],
            messages=[MessageId(id="wamid.HBgLMzM3ODg4MTM5NjYVAgARGBI1MUU0QkQ4MzhBOTQ5MjBGODIA")],
        )
    )
