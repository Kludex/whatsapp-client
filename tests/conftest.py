from __future__ import annotations

import os

import pytest

from whatsapp_client import WhatsAppClient


@pytest.fixture(scope="session")
def vcr_config():
    return {"filter_headers": ["authorization"], "match_on": ["method", "scheme", "host", "port", "body"]}


@pytest.fixture
async def whatsapp_client():
    phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "123456789")
    access_token = os.environ.get("WHATSAPP_ACCESS_TOKEN", "test-token")
    async with WhatsAppClient(phone_number_id=phone_number_id, access_token=access_token) as client:
        yield client
