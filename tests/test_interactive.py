from __future__ import annotations

import pytest
from inline_snapshot import snapshot

from whatsapp_client import Contact, ListRow, ListSection, MessageId, MessageResponse, ReplyButton, WhatsAppClient


@pytest.mark.vcr
async def test_send_buttons(whatsapp_client: WhatsAppClient) -> None:
    response = await whatsapp_client.send_buttons(
        to="33788813966",
        body="Choose an option:",
        buttons=[ReplyButton(id="btn1", title="Option 1"), ReplyButton(id="btn2", title="Option 2")],
        header="Menu",
        footer="Pick one",
    )
    assert response == snapshot(
        MessageResponse(
            messaging_product="whatsapp",
            contacts=[Contact(input="33788813966", wa_id="33788813966")],
            messages=[MessageId(id="wamid.HBgLMzM3ODg4MTM5NjYVAgARGBI5QTAyM0NFRUM5NUQxOTZDOUIA")],
        )
    )


@pytest.mark.vcr
async def test_send_list(whatsapp_client: WhatsAppClient) -> None:
    response = await whatsapp_client.send_list(
        to="33788813966",
        body="Browse our products:",
        button_text="View options",
        sections=[
            ListSection(
                title="Category A",
                rows=[
                    ListRow(id="row1", title="Item 1", description="First item"),
                    ListRow(id="row2", title="Item 2", description="Second item"),
                ],
            )
        ],
        header="Products",
        footer="Tap to select",
    )
    assert response == snapshot(
        MessageResponse(
            messaging_product="whatsapp",
            contacts=[Contact(input="33788813966", wa_id="33788813966")],
            messages=[MessageId(id="wamid.HBgLMzM3ODg4MTM5NjYVAgARGBI3Q0U5RjZEQkNCQTc4MkE4QjMA")],
        )
    )
