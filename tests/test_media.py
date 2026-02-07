from __future__ import annotations

import pytest
from inline_snapshot import snapshot

from whatsapp_client import Contact, MessageId, MessageResponse, WhatsAppClient


@pytest.mark.vcr
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


@pytest.mark.vcr
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


@pytest.mark.vcr
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


@pytest.mark.vcr
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


@pytest.mark.vcr
async def test_send_sticker(whatsapp_client: WhatsAppClient) -> None:
    response = await whatsapp_client.send_sticker(to="33788813966", link="https://www.gstatic.com/webp/gallery/1.webp")
    assert response == snapshot(
        MessageResponse(
            messaging_product="whatsapp",
            contacts=[Contact(input="33788813966", wa_id="33788813966")],
            messages=[MessageId(id="wamid.HBgLMzM3ODg4MTM5NjYVAgARGBJGODg5NDg0QUQ4QjY1Mzg3QjEA")],
        )
    )
