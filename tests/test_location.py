from __future__ import annotations

import pytest
from inline_snapshot import snapshot

from whatsapp_client import Contact, MessageId, MessageResponse, WhatsAppClient


@pytest.mark.vcr
async def test_send_location(whatsapp_client: WhatsAppClient) -> None:
    response = await whatsapp_client.send_location(
        to="33788813966", latitude=-23.5505, longitude=-46.6333, name="São Paulo", address="São Paulo, Brazil"
    )
    assert response == snapshot(
        MessageResponse(
            messaging_product="whatsapp",
            contacts=[Contact(input="33788813966", wa_id="33788813966")],
            messages=[MessageId(id="wamid.HBgLMzM3ODg4MTM5NjYVAgARGBJFOTREMDk1NjFFRUZEMjI3MzIA")],
        )
    )
