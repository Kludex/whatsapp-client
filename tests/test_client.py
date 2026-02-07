from __future__ import annotations

import pytest
from inline_snapshot import snapshot

from whatsapp_client import (
    Contact,
    ListRow,
    ListSection,
    MessageId,
    MessageResponse,
    ReplyButton,
    Template,
    TemplateLanguage,
    WhatsAppAPIError,
    WhatsAppClient,
)

pytestmark = pytest.mark.vcr


async def test_send_text(whatsapp_client: WhatsAppClient) -> None:
    response = await whatsapp_client.send_text(to="33788813966", body="Hello from Python!")
    assert response == snapshot(
        MessageResponse(
            messaging_product="whatsapp",
            contacts=[Contact(input="33788813966", wa_id="33788813966")],
            messages=[MessageId(id="wamid.HBgLMzM3ODg4MTM5NjYVAgARGBIzNzc4QTM2MTZDMDU4NEZBREQA")],
        )
    )


async def test_send_image(whatsapp_client: WhatsAppClient) -> None:
    response = await whatsapp_client.send_image(
        to="33788813966",
        link="https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png",
        caption="Check this out",
    )
    assert response == snapshot(
        MessageResponse(
            messaging_product="whatsapp",
            contacts=[Contact(input="33788813966", wa_id="33788813966")],
            messages=[MessageId(id="wamid.HBgLMzM3ODg4MTM5NjYVAgARGBI0MUU5Q0JFNjE0MUUxOTkzOEUA")],
        )
    )


async def test_send_audio(whatsapp_client: WhatsAppClient) -> None:
    response = await whatsapp_client.send_audio(
        to="33788813966", link="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
    )
    assert response == snapshot(
        MessageResponse(
            messaging_product="whatsapp",
            contacts=[Contact(input="33788813966", wa_id="33788813966")],
            messages=[MessageId(id="wamid.HBgLMzM3ODg4MTM5NjYVAgARGBIzOUU2QTQ0MUIxQ0U5OUFFMjAA")],
        )
    )


async def test_send_video(whatsapp_client: WhatsAppClient) -> None:
    response = await whatsapp_client.send_video(
        to="33788813966",
        link="https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4",
        caption="Watch this",
    )
    assert response == snapshot(
        MessageResponse(
            messaging_product="whatsapp",
            contacts=[Contact(input="33788813966", wa_id="33788813966")],
            messages=[MessageId(id="wamid.HBgLMzM3ODg4MTM5NjYVAgARGBI1Nzg2NzYxNzk2NTAwMTRFNDgA")],
        )
    )


async def test_send_document(whatsapp_client: WhatsAppClient) -> None:
    response = await whatsapp_client.send_document(
        to="33788813966",
        link="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        caption="Important doc",
        filename="report.pdf",
    )
    assert response == snapshot(
        MessageResponse(
            messaging_product="whatsapp",
            contacts=[Contact(input="33788813966", wa_id="33788813966")],
            messages=[MessageId(id="wamid.HBgLMzM3ODg4MTM5NjYVAgARGBI4NzUxOEE3NDY3Qzc1Qzg3NUQA")],
        )
    )


async def test_send_sticker(whatsapp_client: WhatsAppClient) -> None:
    response = await whatsapp_client.send_sticker(to="33788813966", link="https://www.gstatic.com/webp/gallery/1.webp")
    assert response == snapshot(
        MessageResponse(
            messaging_product="whatsapp",
            contacts=[Contact(input="33788813966", wa_id="33788813966")],
            messages=[MessageId(id="wamid.HBgLMzM3ODg4MTM5NjYVAgARGBJGODg5NDg0QUQ4QjY1Mzg3QjEA")],
        )
    )


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


async def test_invalid_token() -> None:
    async with WhatsAppClient(phone_number_id="123456789", access_token="invalid-token") as client:
        with pytest.raises(WhatsAppAPIError) as exc_info:
            await client.send_text(to="33788813966", body="Hello")
        error = exc_info.value
        assert error.status_code == snapshot(401)
        assert error.error_code == snapshot(190)
        assert error.error_type == snapshot("OAuthException")
        assert error.message == snapshot("Invalid OAuth access token - Cannot parse access token")


async def test_invalid_phone(whatsapp_client: WhatsAppClient) -> None:
    with pytest.raises(WhatsAppAPIError) as exc_info:
        await whatsapp_client.send_text(to="invalid", body="Hello")
    error = exc_info.value
    assert error.status_code == snapshot(400)
    assert error.error_code == snapshot(131030)
