# WhatsApp Client

Async Python client for the [WhatsApp Business Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api).

> [!NOTE]
> This package was mainly LLM-generated (Claude), with very strong opinions from [@Kludex](https://github.com/Kludex).

Requires Python 3.10+

## Installation

Install with uv:

```bash
uv add whatsapp-client
```

## Setup

You need two credentials from Meta to use this package:

### 1. Phone Number ID

1. Go to the [Meta Developer Portal](https://developers.facebook.com/apps/) and create a **Business** app.
2. In your app dashboard, add the **WhatsApp** product.
3. Go to **WhatsApp** > **API Setup** — your **Phone Number ID** is listed below the test phone number.

### 2. Access Token

For **testing**, click **Generate** on the API Setup page to get a temporary 24-hour token.

For **production**, create a System User in [Meta Business Suite](https://business.facebook.com/settings/system-users):

1. Create a System User with **Admin** role.
2. Assign your WhatsApp app to the System User.
3. Generate a token with the `whatsapp_business_messaging` permission.

### 3. Add test recipients

In test mode, you must verify recipient phone numbers before sending messages.
Go to **WhatsApp** > **API Setup**, click **Manage phone number list**, and add the numbers you want to message.

## Usage

Send a text message:

```python
from whatsapp_client import WhatsAppClient

async with WhatsAppClient(phone_number_id="your-phone-number-id", access_token="your-access-token") as client:
    await client.send_text(to="5511999999999", body="Hello!")
```

### Send media

Images, audio, video, documents, and stickers are sent by URL:

```python
await client.send_image(to="5511999999999", link="https://example.com/image.png", caption="Check this out")
await client.send_audio(to="5511999999999", link="https://example.com/audio.mp3")
await client.send_video(to="5511999999999", link="https://example.com/video.mp4")
await client.send_document(to="5511999999999", link="https://example.com/doc.pdf", filename="report.pdf")
await client.send_sticker(to="5511999999999", link="https://example.com/sticker.webp")
```

### Send location

Share a pin with optional name and address:

```python
await client.send_location(to="5511999999999", latitude=-23.5505, longitude=-46.6333, name="São Paulo")
```

### Send template

Send a pre-approved message template:

```python
from whatsapp_client import Template, TemplateLanguage

await client.send_template(
    to="5511999999999", template=Template(name="hello_world", language=TemplateLanguage(code="en_US"))
)
```

### Send interactive messages

Reply buttons and list menus let users pick from predefined options:

```python
from whatsapp_client import ReplyButton, ListSection, ListRow

await client.send_buttons(
    to="5511999999999",
    body="Choose an option:",
    buttons=[ReplyButton(id="btn1", title="Option 1"), ReplyButton(id="btn2", title="Option 2")],
)

await client.send_list(
    to="5511999999999",
    body="Browse products:",
    button_text="View",
    sections=[ListSection(title="Category", rows=[ListRow(id="r1", title="Item 1")])],
)
```

### Error handling

API errors are raised as `WhatsAppAPIError` with the status code and Graph API error details:

```python
from whatsapp_client import WhatsAppAPIError

try:
    await client.send_text(to="invalid", body="Hello")
except WhatsAppAPIError as e:
    print(e.status_code, e.error_code, e.message)
```

## Groups

Create and manage WhatsApp groups, and send messages to them:

```python
from whatsapp_client import WhatsAppClient

async with WhatsAppClient(phone_number_id="your-phone-number-id", access_token="your-access-token") as client:
    # Create a group
    group = await client.create_group(subject="My Group", participants=["5511999999999"])

    # Send a message to the group (works with any send method)
    await client.send_text(to=group.id, body="Hello group!")
    await client.send_image(to=group.id, link="https://example.com/image.png")

    # List and inspect groups
    groups = await client.get_groups()
    info = await client.get_group(groups[0].id)

    # Update or delete a group
    await client.update_group(group.id, subject="New Name", description="New description")
    await client.delete_group(group.id)

    # Invite links
    invite = await client.get_invite_link(group.id)
    new_invite = await client.reset_invite_link(group.id)

    # Manage participants and join requests
    await client.remove_participants(group.id, participants=["5511999999999"])
    requests = await client.get_join_requests(group.id)
    await client.approve_join_requests(group.id, participants=["5511999999999"])
    await client.reject_join_requests(group.id, participants=["5511999999999"])
```

Group IDs contain `@g.us` (e.g., `120363023561234567@g.us`). When any send method receives a group ID, it automatically sets `recipient_type: "group"` in the API request.

> [!NOTE]
> The Groups API requires your WhatsApp Business account to have at least 100,000 monthly business-initiated conversations.

## Webhooks

Receive incoming messages and status updates via Meta's webhook system.

### Starlette example

Create a `WebhookHandler` with your app secret and client. Register callbacks with `@handler.on_message` and `@handler.on_status` — the client is passed as the first argument, so replying is straightforward. Use `match/case` on `message.content` to handle different message types:

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route

from whatsapp_client import (
    MediaContent,
    Message,
    Status,
    TextContent,
    WebhookHandler,
    WebhookNotification,
    WhatsAppClient,
    verify_challenge,
)

client = WhatsAppClient(phone_number_id="your-phone-number-id", access_token="your-access-token")
handler = WebhookHandler(app_secret="your-app-secret", client=client)


@handler.on_message
async def on_message(client: WhatsAppClient, notification: WebhookNotification, message: Message) -> None:
    match message.content:
        case TextContent(body=body):
            await client.send_text(to=message.from_, body=f"Echo: {body}")
        case MediaContent():
            await client.send_text(to=message.from_, body=f"Got {message.type}: {message.content.id}")


@handler.on_status
async def on_status(client: WhatsAppClient, notification: WebhookNotification, status: Status) -> None:
    print(f"{status.id} -> {status.status}")


async def webhook_get(request: Request) -> Response:
    challenge = verify_challenge(
        mode=request.query_params["hub.mode"],
        token=request.query_params["hub.verify_token"],
        challenge=request.query_params["hub.challenge"],
        verify_token="your-verify-token",
    )
    return PlainTextResponse(challenge)


async def webhook_post(request: Request) -> Response:
    body = await request.body()
    signature = request.headers["x-hub-signature-256"]
    await handler.handle(body=body, signature=signature)
    return Response(status_code=200)


@asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[None]:
    async with client:
        yield


app = Starlette(
    routes=[Route("/webhook", webhook_get, methods=["GET"]), Route("/webhook", webhook_post, methods=["POST"])],
    lifespan=lifespan,
)
```

## License

This project is licensed under the terms of the [MIT License](LICENSE).
