"""
Tests for DRIXL Structured (XML) format.
"""

import pytest
from drixl import StructuredMessage, Artifact, Message
from drixl.converter import compact_to_structured, structured_to_compact, detect_format
from drixl.exceptions import DRIXLParseError


def test_structured_message_creation():
    """Test creating a structured message."""
    msg = StructuredMessage(
        to="AGT2", fr="AGT1", msg_type="REQUEST",
        intent="Analyze firewall logs",
        content="Please analyze firewall.log and extract denied IPs.",
        priority="HIGH"
    )
    assert msg.to == "AGT2"
    assert msg.fr == "AGT1"
    assert msg.msg_type == "REQUEST"
    assert msg.priority == "HIGH"
    assert msg.status == "PENDING"


def test_structured_message_with_artifacts():
    """Test structured message with artifacts."""
    msg = StructuredMessage(
        to="AGT2", fr="AGT1", msg_type="RESPONSE",
        intent="Deliver implementation",
        content="Implementation complete."
    )
    msg.add_artifact("code", "def validate(): pass", "ART-001")
    assert len(msg.artifacts) == 1
    assert msg.artifacts[0].type == "code"
    assert msg.artifacts[0].id == "ART-001"


def test_structured_to_xml():
    """Test XML serialization."""
    msg = StructuredMessage(
        to="AGT2", fr="AGT1", msg_type="REQUEST",
        intent="Test intent", content="Test content"
    )
    xml = msg.to_xml()
    assert "<message>" in xml
    assert "<meta>" in xml
    assert "<envelope>" in xml
    assert "<to>AGT2</to>" in xml
    assert "<from>AGT1</from>" in xml


def test_structured_from_xml():
    """Test XML parsing."""
    xml = """<?xml version="1.0" ?>
<message>
  <meta>
    <msg_id>MSG-001</msg_id>
    <thread_id>THREAD-001</thread_id>
    <reply_to>NULL</reply_to>
    <timestamp>2026-02-25T20:00:00</timestamp>
    <priority>HIGH</priority>
  </meta>
  <envelope>
    <to>AGT2</to>
    <from>AGT1</from>
    <type>REQUEST</type>
    <intent>Test intent</intent>
  </envelope>
  <content>Test content</content>
  <artifacts/>
  <status>PENDING</status>
  <next_action>AGT2 should respond</next_action>
</message>
"""
    msg = StructuredMessage.from_xml(xml)
    assert msg.msg_id == "MSG-001"
    assert msg.to == "AGT2"
    assert msg.fr == "AGT1"
    assert msg.msg_type == "REQUEST"
    assert msg.priority == "HIGH"


def test_compact_to_structured_conversion():
    """Test converting compact to structured format."""
    compact = "@to:AGT2 @fr:AGT1 @t:REQ @p:HIGH\nANLY XTRCT [input.json] [out:json]"
    structured = compact_to_structured(compact, intent="Analyze and extract")
    assert structured.to == "AGT2"
    assert structured.fr == "AGT1"
    assert structured.msg_type == "REQUEST"
    assert structured.priority == "HIGH"
    assert "ANLY" in structured.content
    assert "XTRCT" in structured.content


def test_structured_to_compact_conversion():
    """Test converting structured to compact format."""
    structured = StructuredMessage(
        to="AGT2", fr="AGT1", msg_type="REQUEST",
        intent="Test", content="Test", priority="HIGH"
    )
    compact = structured_to_compact(structured, actions=["ANLY"], params=["input.json"])
    assert "@to:AGT2" in compact
    assert "@fr:AGT1" in compact
    assert "@t:REQ" in compact
    assert "ANLY" in compact


def test_detect_format_compact():
    """Test format detection for compact messages."""
    compact = "@to:AGT2 @fr:AGT1 @t:REQ @p:HIGH\nANLY [input.json]"
    assert detect_format(compact) == "compact"


def test_detect_format_structured():
    """Test format detection for structured messages."""
    xml = "<message><meta><msg_id>MSG-001</msg_id></meta></message>"
    assert detect_format(xml) == "structured"


def test_detect_format_invalid():
    """Test format detection with invalid input."""
    with pytest.raises(DRIXLParseError):
        detect_format("invalid message format")


def test_message_build_structured_format():
    """Test Message.build() with format='structured'."""
    msg = Message.build(
        to="AGT2", fr="AGT1", msg_type="REQ", priority="HIGH",
        actions=["ANLY"], params=["input.json"],
        format="structured", intent="Analyze input"
    )
    assert "<message>" in msg
    assert "<to>AGT2</to>" in msg
    assert "<type>REQUEST</type>" in msg


def test_message_parse_auto_detect():
    """Test Message.parse() auto-detects format."""
    compact = "@to:AGT2 @fr:AGT1 @t:REQ @p:HIGH\nANLY [input.json]"
    parsed_compact = Message.parse(compact)
    assert parsed_compact["envelope"]["to"] == "AGT2"
    
    structured = StructuredMessage(
        to="AGT3", fr="AGT2", msg_type="RESPONSE",
        intent="Test", content="Test"
    ).to_xml()
    parsed_structured = Message.parse(structured)
    assert parsed_structured["to"] == "AGT3"
