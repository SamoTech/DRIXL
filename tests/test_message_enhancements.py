"""
Tests for new Message enhancements: reply(), error(), from_dict(), strict parsing
"""

import pytest
from drixl import Message
from drixl.exceptions import DRIXLInvalidVerbError


def test_message_error_helper():
    """Test Message.error() helper for ERR messages."""
    msg = Message.error(
        to="ORCH", fr="AGT2",
        code="TIMEOUT", detail="firewall.json not found"
    )
    assert "@t:ERR" in msg
    assert "[code:TIMEOUT]" in msg
    assert "[detail:firewall.json not found]" in msg
    assert "ESCL" in msg


def test_message_from_dict():
    """Test Message.from_dict() constructor."""
    data = {
        "to": "AGT2", "fr": "AGT1",
        "msg_type": "REQ", "priority": "HIGH",
        "actions": ["ANLY"], "params": ["input.json"],
        "ctx_ref": "ref#1"
    }
    msg = Message.from_dict(data)
    assert msg.to == "AGT2"
    assert msg.fr == "AGT1"
    assert msg.msg_type == "REQ"
    assert msg.priority == "HIGH"
    assert msg.actions == ["ANLY"]
    assert msg.ctx_ref == "ref#1"


def test_message_to_dict():
    """Test Message.to_dict() serialization."""
    msg = Message(
        to="AGT2", fr="AGT1", msg_type="REQ", priority="HIGH",
        actions=["ANLY"], params=["input.json"], ctx_ref="ref#1"
    )
    data = msg.to_dict()
    assert data["to"] == "AGT2"
    assert data["fr"] == "AGT1"
    assert data["msg_type"] == "REQ"
    assert data["ctx_ref"] == "ref#1"


def test_message_reply_helper():
    """Test Message.reply() auto-swaps to/fr and sets type=RES."""
    original = Message(
        to="AGT2", fr="AGT1", msg_type="REQ", priority="HIGH",
        actions=["ANLY"], params=["input.json"], ctx_ref="ref#1"
    )
    reply = original.reply(
        actions=["VALD"], params=["result:ok"]
    )
    assert "@to:AGT1" in reply  # Reply to original sender
    assert "@fr:AGT2" in reply  # From original recipient
    assert "@t:RES" in reply
    assert "[ctx:ref#1]" in reply  # Preserves ctx_ref


def test_parse_strict_mode_rejects_unknown_verbs():
    """Test strict=True rejects unknown verbs."""
    raw = "@to:AGT2 @fr:AGT1 @t:REQ @p:HIGH\nANLY UNKNOWN_VERB [input.json]"
    with pytest.raises(DRIXLInvalidVerbError):
        Message.parse(raw, strict=True)


def test_parse_lenient_mode_allows_unknown_verbs():
    """Test strict=False allows unknown verbs (for ERR freeform text)."""
    raw = "@to:AGT2 @fr:AGT1 @t:ERR @p:HIGH\nESCL CUSTOM_TEXT [code:FAIL]"
    parsed = Message.parse(raw, strict=False)
    assert "ESCL" in parsed["actions"]
    assert "CUSTOM_TEXT" in parsed["actions"]


def test_round_trip_dict_serialization():
    """Test Message -> dict -> Message round-trip."""
    original = Message(
        to="AGT3", fr="AGT2", msg_type="RES", priority="MED",
        actions=["VALD", "STOR"], params=["result:pass"], ctx_ref="ref#2"
    )
    data = original.to_dict()
    restored = Message.from_dict(data)
    assert restored.to == original.to
    assert restored.fr == original.fr
    assert restored.actions == original.actions
    assert restored.ctx_ref == original.ctx_ref
