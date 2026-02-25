"""
Tests for DRIXL Message builder and parser.
"""

import pytest
from drixl import Message
from drixl.exceptions import DRIXLParseError, DRIXLInvalidVerbError


def test_build_basic_message():
    msg = Message.build(
        to="AGT2", fr="AGT1", msg_type="REQ", priority="HIGH",
        actions=["ANLY"], params=["input.json", "out:json"]
    )
    assert "@to:AGT2" in msg
    assert "@fr:AGT1" in msg
    assert "@t:REQ" in msg
    assert "@p:HIGH" in msg
    assert "ANLY" in msg
    assert "[input.json]" in msg


def test_build_with_ctx_ref():
    msg = Message.build(
        to="AGT3", fr="AGT2", msg_type="RES", priority="MED",
        actions=["VALD"], params=["result:ok"], ctx_ref="ref#1"
    )
    assert "[ctx:ref#1]" in msg


def test_parse_message():
    raw = "@to:AGT2 @fr:AGT1 @t:REQ @p:HIGH\nANLY [input.json] [out:json] [ctx:ref#1]"
    parsed = Message.parse(raw)
    assert parsed["envelope"]["to"] == "AGT2"
    assert parsed["envelope"]["type"] == "REQ"
    assert "ANLY" in parsed["actions"]
    assert "ctx:ref#1" in parsed["params"]


def test_invalid_verb_raises_error():
    with pytest.raises(DRIXLInvalidVerbError):
        Message.build(
            to="AGT2", fr="AGT1", msg_type="REQ", priority="HIGH",
            actions=["INVALID_VERB"], params=[]
        )


def test_invalid_message_type_raises_error():
    with pytest.raises(ValueError):
        Message.build(
            to="AGT2", fr="AGT1", msg_type="SEND", priority="HIGH",
            actions=["ANLY"], params=[]
        )


def test_parse_invalid_message_raises_error():
    with pytest.raises(DRIXLParseError):
        Message.parse("only one line here")
