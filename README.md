# WhatsApp Client

Async Python client for the [WhatsApp Business Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api).

> [!NOTE]
> This package was mainly LLM-generated (Claude), with very strong opinions from [@Kludex](https://github.com/Kludex).

> Requires Python 3.10+

## Installation

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

```python
from whatsapp_client import WhatsAppClient

async with WhatsAppClient(
    phone_number_id="your-phone-number-id",
    access_token="your-access-token",
) as client:
    await client.send_text(to="5511999999999", body="Hello!")
```

### Send media

```python
await client.send_image(to="5511999999999", link="https://example.com/image.png", caption="Check this out")
await client.send_audio(to="5511999999999", link="https://example.com/audio.mp3")
await client.send_video(to="5511999999999", link="https://example.com/video.mp4")
await client.send_document(to="5511999999999", link="https://example.com/doc.pdf", filename="report.pdf")
await client.send_sticker(to="5511999999999", link="https://example.com/sticker.webp")
```

### Send location

```python
await client.send_location(to="5511999999999", latitude=-23.5505, longitude=-46.6333, name="São Paulo")
```

### Send template

```python
from whatsapp_client import Template, TemplateLanguage

await client.send_template(
    to="5511999999999",
    template=Template(name="hello_world", language=TemplateLanguage(code="en_US")),
)
```

### Send interactive messages

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

```python
from whatsapp_client import WhatsAppAPIError

try:
    await client.send_text(to="invalid", body="Hello")
except WhatsAppAPIError as e:
    print(e.status_code, e.error_code, e.message)
```

## License

This project is licensed under the terms of the [MIT License](LICENSE).
