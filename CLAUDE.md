# WhatsApp Business Cloud API — Python Client

## Commands

- `uv sync --group test` — install all deps
- `uv run --with pyright pyright` — strict type checking (src/ only)
- `uv run --with ruff ruff format .` — format code
- `uv run pytest` — run tests against recorded cassettes
- `uv run pytest --record-mode=once` — record new cassettes from real API (requires env vars)
- `uv run pytest --record-mode=rewrite` — re-record all cassettes from scratch

## Environment Variables

Tests require these env vars when recording cassettes:

- `WHATSAPP_PHONE_NUMBER_ID` — from Meta Developer Portal > WhatsApp > API Setup (the numeric ID, not the phone number)
- `WHATSAPP_ACCESS_TOKEN` — System User token (Admin role) from Meta Business Suite with `whatsapp_business_messaging` permission

Store them in `.env` (gitignored). The test recipient phone number is hardcoded in tests.

## Architecture

- `src/whatsapp_client/` — async-only package, pyright strict, `from __future__ import annotations` everywhere
- `_client.py` — `WhatsAppClient` async context manager with all send methods
- `_types.py` — frozen dataclasses with `type` aliases (PEP 695) for unions
- `_exceptions.py` — `WhatsAppError` base, `WhatsAppAPIError` dataclass with Graph API error parsing
- Tests use `pytest-recording` (wraps vcrpy) with `@pytest.mark.vcr` — cassettes auto-named per test
- VCR cassettes are recorded from real API calls, never hand-crafted

## Style

- Ruff formatter with `line-length = 120` and `skip-magic-trailing-comma = true`
- Prefer single-line expressions when they fit within the line length
