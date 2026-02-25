"""
DRIXL Format Converter
Convert between compact and structured (XML) formats.
"""

from typing import Optional
from drixl.message import Message
from drixl.structured import StructuredMessage
from drixl.exceptions import DRIXLParseError


def compact_to_structured(
    compact_msg: str,
    thread_id: Optional[str] = None,
    msg_id: Optional[str] = None,
    intent: Optional[str] = None,
    status: str = "PENDING",
    next_action: Optional[str] = None
) -> StructuredMessage:
    """
    Convert a compact DRIXL message to structured XML format.
    
    Args:
        compact_msg: Compact DRIXL message string
        thread_id: Optional thread ID (auto-generated if not provided)
        msg_id: Optional message ID (auto-generated if not provided)
        intent: Optional intent description (derived from actions if not provided)
        status: Message status (default: PENDING)
        next_action: Optional next action description
    
    Returns:
        StructuredMessage instance
    """
    parsed = Message.parse(compact_msg, strict=False)
    envelope = parsed["envelope"]
    actions = parsed["actions"]
    params = parsed["params"]
    
    # Map compact type to structured type
    type_mapping = {
        "REQ": "REQUEST",
        "RES": "RESPONSE",
        "ERR": "ESCALATE",
        "FIN": "FINALIZE"
    }
    msg_type = type_mapping.get(envelope["type"], "REQUEST")
    
    # Generate intent if not provided
    if not intent:
        intent = f"Execute actions: {', '.join(actions)}"
    
    # Build content from actions and params
    content_lines = [f"Actions: {', '.join(actions)}"]
    if params:
        content_lines.append(f"Parameters: {', '.join(params)}")
    content = "\n".join(content_lines)
    
    # Map priority
    priority_mapping = {"HIGH": "HIGH", "MED": "NORMAL", "LOW": "LOW"}
    priority = priority_mapping.get(envelope["priority"], "NORMAL")
    
    return StructuredMessage(
        to=envelope["to"],
        fr=envelope["fr"],
        msg_type=msg_type,
        intent=intent,
        content=content,
        msg_id=msg_id,
        thread_id=thread_id,
        priority=priority,
        status=status,
        next_action=next_action
    )


def structured_to_compact(
    structured_msg: StructuredMessage,
    actions: Optional[list] = None,
    params: Optional[list] = None
) -> str:
    """
    Convert a structured XML message to compact DRIXL format.
    
    Args:
        structured_msg: StructuredMessage instance
        actions: Optional list of DRIXL verbs (extracted from content if not provided)
        params: Optional list of parameters (extracted from content if not provided)
    
    Returns:
        Compact DRIXL message string
    """
    # Map structured type to compact type
    type_mapping = {
        "REQUEST": "REQ",
        "RESPONSE": "RES",
        "CRITIQUE": "RES",
        "DELEGATE": "REQ",
        "ACK": "RES",
        "ESCALATE": "ERR",
        "FINALIZE": "FIN"
    }
    msg_type = type_mapping.get(structured_msg.msg_type, "REQ")
    
    # Map priority
    priority_mapping = {"HIGH": "HIGH", "NORMAL": "MED", "LOW": "LOW", "BLOCKING": "HIGH"}
    priority = priority_mapping.get(structured_msg.priority, "MED")
    
    # Extract actions and params if not provided
    if not actions:
        # Try to extract from content
        actions = ["EXEC"]  # Default fallback
    
    if not params:
        params = []
    
    # Build compact message
    return Message.build(
        to=structured_msg.to,
        fr=structured_msg.fr,
        msg_type=msg_type,
        priority=priority,
        actions=actions,
        params=params
    )


def detect_format(message: str) -> str:
    """
    Auto-detect message format.
    
    Args:
        message: Message string
    
    Returns:
        'compact' or 'structured'
    """
    stripped = message.strip()
    if stripped.startswith("<message>") or stripped.startswith("<?xml"):
        return "structured"
    elif stripped.startswith("@to:"):
        return "compact"
    else:
        raise DRIXLParseError("Unable to detect message format. Must start with '@to:' (compact) or '<message>' (XML)")
