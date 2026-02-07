from __future__ import annotations

import pytest
from inline_snapshot import snapshot

from whatsapp_client import Contact, MessageId, MessageResponse, WhatsAppClient


@pytest.mark.vcr
async def test_send_text(whatsapp_client: WhatsAppClient) -> None:
    response = await whatsapp_client.send_text(to="33788813966", body="Hello from Python!")
    assert response == snapshot(
        MessageResponse(
            messaging_product="whatsapp",
            contacts=[Contact(input="33788813966", wa_id="33788813966")],
            messages=[MessageId(id="wamid.HBgLMzM3ODg4MTM5NjYVAgARGBIzNzc4QTM2MTZDMDU4NEZBREQA")],
        )
    )
