"""
DRIXL Structured (XML) Format
Full-featured XML protocol for development, debugging, and governance.
Use this when you need traceability, artifacts, and critique workflows.

For production (token optimization), use the compact format instead.
"""

import re
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from xml.etree import ElementTree as ET
from xml.dom import minidom

from drixl.exceptions import DRIXLParseError


class Artifact:
    """Represents a structured artifact (code, data, test, doc, plan)."""
    
    def __init__(self, artifact_type: str, artifact_id: str, content: str):
        self.type = artifact_type
        self.id = artifact_id
        self.content = content
    
    def to_xml(self) -> ET.Element:
        artifact = ET.Element("artifact", type=self.type, id=self.id)
        artifact.text = self.content
        return artifact
    
    @staticmethod
    def from_xml(element: ET.Element) -> "Artifact":
        return Artifact(
            artifact_type=element.get("type", "unknown"),
            artifact_id=element.get("id", "ART-UNKNOWN"),
            content=element.text or ""
        )


class StructuredMessage:
    """DRIXL Structured Message - Full XML format with metadata, artifacts, and status tracking."""
    
    MESSAGE_TYPES = {"REQUEST", "RESPONSE", "CRITIQUE", "DELEGATE", "ACK", "ESCALATE", "FINALIZE"}
    PRIORITIES = {"LOW", "NORMAL", "HIGH", "BLOCKING"}
    STATUSES = {"PENDING", "IN_PROGRESS", "COMPLETE", "BLOCKED", "ESCALATED"}
    
    def __init__(
        self,
        to: str,
        fr: str,
        msg_type: str,
        intent: str,
        content: str,
        msg_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        reply_to: Optional[str] = None,
        timestamp: Optional[str] = None,
        priority: str = "NORMAL",
        status: str = "PENDING",
        next_action: Optional[str] = None,
        artifacts: Optional[List[Artifact]] = None
    ):
        self.msg_id = msg_id or f"MSG-{uuid.uuid4().hex[:8].upper()}"
        self.thread_id = thread_id or f"THREAD-{uuid.uuid4().hex[:8].upper()}"
        self.reply_to = reply_to or "NULL"
        self.timestamp = timestamp or datetime.utcnow().isoformat()
        self.priority = priority.upper()
        self.to = to
        self.fr = fr
        self.msg_type = msg_type.upper()
        self.intent = intent
        self.content = content
        self.status = status.upper()
        self.next_action = next_action or ""
        self.artifacts = artifacts or []
        
        # Validate
        if self.msg_type not in self.MESSAGE_TYPES:
            raise ValueError(f"Invalid message type: {self.msg_type}. Must be one of {self.MESSAGE_TYPES}")
        if self.priority not in self.PRIORITIES:
            raise ValueError(f"Invalid priority: {self.priority}. Must be one of {self.PRIORITIES}")
        if self.status not in self.STATUSES:
            raise ValueError(f"Invalid status: {self.status}. Must be one of {self.STATUSES}")
    
    def add_artifact(self, artifact_type: str, content: str, artifact_id: Optional[str] = None) -> Artifact:
        """Add an artifact to this message."""
        if not artifact_id:
            artifact_id = f"ART-{len(self.artifacts) + 1:03d}"
        artifact = Artifact(artifact_type, artifact_id, content)
        self.artifacts.append(artifact)
        return artifact
    
    def to_xml(self, pretty: bool = True) -> str:
        """Convert to XML string."""
        message = ET.Element("message")
        
        # Meta section
        meta = ET.SubElement(message, "meta")
        ET.SubElement(meta, "msg_id").text = self.msg_id
        ET.SubElement(meta, "thread_id").text = self.thread_id
        ET.SubElement(meta, "reply_to").text = self.reply_to
        ET.SubElement(meta, "timestamp").text = self.timestamp
        ET.SubElement(meta, "priority").text = self.priority
        
        # Envelope section
        envelope = ET.SubElement(message, "envelope")
        ET.SubElement(envelope, "to").text = self.to
        ET.SubElement(envelope, "from").text = self.fr
        ET.SubElement(envelope, "type").text = self.msg_type
        ET.SubElement(envelope, "intent").text = self.intent
        
        # Content
        ET.SubElement(message, "content").text = self.content
        
        # Artifacts
        artifacts_elem = ET.SubElement(message, "artifacts")
        for artifact in self.artifacts:
            artifacts_elem.append(artifact.to_xml())
        
        # Status and next action
        ET.SubElement(message, "status").text = self.status
        ET.SubElement(message, "next_action").text = self.next_action
        
        # Convert to string
        xml_str = ET.tostring(message, encoding="unicode")
        
        if pretty:
            dom = minidom.parseString(xml_str)
            return dom.toprettyxml(indent="  ")
        return xml_str
    
    @staticmethod
    def from_xml(xml_str: str) -> "StructuredMessage":
        """Parse XML string into StructuredMessage."""
        try:
            root = ET.fromstring(xml_str)
        except ET.ParseError as e:
            raise DRIXLParseError(f"Invalid XML: {e}")
        
        if root.tag != "message":
            raise DRIXLParseError(f"Root element must be <message>, got <{root.tag}>")
        
        # Extract meta
        meta = root.find("meta")
        if meta is None:
            raise DRIXLParseError("Missing <meta> section")
        
        msg_id = meta.findtext("msg_id", "MSG-UNKNOWN")
        thread_id = meta.findtext("thread_id", "THREAD-UNKNOWN")
        reply_to = meta.findtext("reply_to", "NULL")
        timestamp = meta.findtext("timestamp", datetime.utcnow().isoformat())
        priority = meta.findtext("priority", "NORMAL")
        
        # Extract envelope
        envelope = root.find("envelope")
        if envelope is None:
            raise DRIXLParseError("Missing <envelope> section")
        
        to = envelope.findtext("to", "UNKNOWN")
        fr = envelope.findtext("from", "UNKNOWN")
        msg_type = envelope.findtext("type", "REQUEST")
        intent = envelope.findtext("intent", "")
        
        # Extract content and status
        content = root.findtext("content", "")
        status = root.findtext("status", "PENDING")
        next_action = root.findtext("next_action", "")
        
        # Extract artifacts
        artifacts_elem = root.find("artifacts")
        artifacts = []
        if artifacts_elem is not None:
            for art_elem in artifacts_elem.findall("artifact"):
                artifacts.append(Artifact.from_xml(art_elem))
        
        return StructuredMessage(
            to=to, fr=fr, msg_type=msg_type, intent=intent, content=content,
            msg_id=msg_id, thread_id=thread_id, reply_to=reply_to,
            timestamp=timestamp, priority=priority, status=status,
            next_action=next_action, artifacts=artifacts
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "msg_id": self.msg_id,
            "thread_id": self.thread_id,
            "reply_to": self.reply_to,
            "timestamp": self.timestamp,
            "priority": self.priority,
            "to": self.to,
            "fr": self.fr,
            "msg_type": self.msg_type,
            "intent": self.intent,
            "content": self.content,
            "status": self.status,
            "next_action": self.next_action,
            "artifacts": [{"type": a.type, "id": a.id, "content": a.content} for a in self.artifacts]
        }
    
    def __repr__(self) -> str:
        return f"StructuredMessage(id={self.msg_id}, type={self.msg_type}, to={self.to}, from={self.fr})"
