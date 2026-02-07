from __future__ import annotations

import pytest
from inline_snapshot import snapshot

from whatsapp_client import WhatsAppAPIError, WhatsAppClient


@pytest.mark.vcr
async def test_invalid_token() -> None:
    async with WhatsAppClient(phone_number_id="123456789", access_token="invalid-token") as client:
        with pytest.raises(WhatsAppAPIError) as exc_info:
            await client.send_text(to="33788813966", body="Hello")
        error = exc_info.value
        assert error.status_code == snapshot(401)
        assert error.error_code == snapshot(190)
        assert error.error_type == snapshot("OAuthException")
        assert error.message == snapshot("Invalid OAuth access token - Cannot parse access token")


@pytest.mark.vcr
async def test_invalid_phone(whatsapp_client: WhatsAppClient) -> None:
    with pytest.raises(WhatsAppAPIError) as exc_info:
        await whatsapp_client.send_text(to="invalid", body="Hello")
    error = exc_info.value
    assert error.status_code == snapshot(400)
    assert error.error_code == snapshot(131030)
