from __future__ import annotations

import pytest

from whatsapp_client import GroupInfo, GroupInviteLink, GroupJoinRequest, GroupParticipant, GroupSummary, WhatsAppClient

pytestmark = pytest.mark.vcr


async def test_create_group(whatsapp_client: WhatsAppClient) -> None:
    group = await whatsapp_client.create_group(subject="Test Group", participants=["33788813966"])
    assert isinstance(group, GroupInfo)
    assert group.subject == "Test Group"
    assert len(group.participants) >= 1


async def test_get_groups(whatsapp_client: WhatsAppClient) -> None:
    groups = await whatsapp_client.get_groups()
    assert isinstance(groups, list)
    for g in groups:
        assert isinstance(g, GroupSummary)


async def test_get_group(whatsapp_client: WhatsAppClient) -> None:
    groups = await whatsapp_client.get_groups()
    assert len(groups) > 0
    group = await whatsapp_client.get_group(groups[0].id)
    assert isinstance(group, GroupInfo)
    assert group.id == groups[0].id
    for p in group.participants:
        assert isinstance(p, GroupParticipant)


async def test_update_group(whatsapp_client: WhatsAppClient) -> None:
    groups = await whatsapp_client.get_groups()
    assert len(groups) > 0
    await whatsapp_client.update_group(groups[0].id, subject="Updated Group")


async def test_get_invite_link(whatsapp_client: WhatsAppClient) -> None:
    groups = await whatsapp_client.get_groups()
    assert len(groups) > 0
    invite = await whatsapp_client.get_invite_link(groups[0].id)
    assert isinstance(invite, GroupInviteLink)
    assert invite.link.startswith("https://")


async def test_reset_invite_link(whatsapp_client: WhatsAppClient) -> None:
    groups = await whatsapp_client.get_groups()
    assert len(groups) > 0
    invite = await whatsapp_client.reset_invite_link(groups[0].id)
    assert isinstance(invite, GroupInviteLink)
    assert invite.link.startswith("https://")


async def test_get_join_requests(whatsapp_client: WhatsAppClient) -> None:
    groups = await whatsapp_client.get_groups()
    assert len(groups) > 0
    requests = await whatsapp_client.get_join_requests(groups[0].id)
    assert isinstance(requests, list)
    for r in requests:
        assert isinstance(r, GroupJoinRequest)
