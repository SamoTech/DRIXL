"""
DRIXL Message Builder and Parser
Handles construction and parsing of DRIXL-format inter-agent messages.
"""

import re
from typing import Optional, Dict, List, Any
from drixl.verbs import VERBS
from drixl.exceptions import DRIXLParseError, DRIXLInvalidVerbError


MESSAGE_TYPES = {"REQ", "RES", "ERR", "FIN"}
PRIORITIES = {"HIGH", "MED", "LOW"}


class Message:
    """DRIXL Message — builder and parser for inter-agent signals."""

    def __init__(self, to: str, fr: str, msg_type: str, priority: str,
                 actions: List[str], params: List[str], ctx_ref: Optional[str] = None):
        """Internal constructor. Use Message.build() or Message.from_dict() instead."""
        self.to = to
        self.fr = fr
        self.msg_type = msg_type.upper()
        self.priority = priority.upper()
        self.actions = [a.upper() for a in actions]
        self.params = params
        self.ctx_ref = ctx_ref

    @staticmethod
    def build(
        to: str,
        fr: str,
        msg_type: str,
        priority: str,
        actions: list,
        params: list,
        ctx_ref: Optional[str] = None,
    ) -> str:
        """
        Build a DRIXL-formatted inter-agent message.

        Args:
            to: Recipient agent ID (e.g., 'AGT2')
            fr: Sender agent ID (e.g., 'AGT1')
            msg_type: Message type - REQ | RES | ERR | FIN
            priority: Message priority - HIGH | MED | LOW
            actions: List of DRIXL verbs (e.g., ['ANLY', 'XTRCT'])
            params: List of parameters (e.g., ['input.json', 'out:json'])
            ctx_ref: Optional context store reference ID (e.g., 'ref#1')

        Returns:
            Formatted DRIXL message string
        """
        if msg_type.upper() not in MESSAGE_TYPES:
            raise ValueError(f"Invalid message type: {msg_type}. Must be one of {MESSAGE_TYPES}")
        if priority.upper() not in PRIORITIES:
            raise ValueError(f"Invalid priority: {priority}. Must be one of {PRIORITIES}")

        for verb in actions:
            if verb.upper() not in VERBS:
                raise DRIXLInvalidVerbError(f"Unknown verb: '{verb}'. Use drixl.VERBS to see valid verbs.")

        envelope = f"@to:{to} @fr:{fr} @t:{msg_type.upper()} @p:{priority.upper()}"
        body = " ".join(v.upper() for v in actions)
        if params:
            body += " " + " ".join(f"[{p}]" for p in params)
        if ctx_ref:
            body += f" [ctx:{ctx_ref}]"

        return f"{envelope}\n{body}"

    @staticmethod
    def error(to: str, fr: str, code: str, detail: str, priority: str = "HIGH") -> str:
        """
        Build a structured ERR message.

        Args:
            to: Recipient agent ID
            fr: Sender agent ID
            code: Error code (e.g., 'TIMEOUT', 'NOT_FOUND')
            detail: Error detail description
            priority: Message priority (default: HIGH)

        Returns:
            Formatted DRIXL error message
        """
        return Message.build(
            to=to, fr=fr, msg_type="ERR", priority=priority,
            actions=["ESCL"],
            params=[f"code:{code}", f"detail:{detail}"]
        )

    @staticmethod
    def parse(raw: str, strict: bool = True) -> dict:
        """
        Parse a raw DRIXL message string into a structured dictionary.

        Args:
            raw: Raw DRIXL message string
            strict: If True, raises error on unknown verbs. If False, treats all non-bracketed tokens as actions.

        Returns:
            Dictionary with keys: envelope, actions, params
        """
        lines = raw.strip().splitlines()
        if len(lines) < 2:
            raise DRIXLParseError("Invalid DRIXL message: must have envelope and body lines.")

        envelope_line = lines[0]
        body_line = " ".join(lines[1:])

        def extract(pattern: str, text: str) -> Optional[str]:
            match = re.search(pattern, text)
            return match.group(1) if match else None

        envelope = {
            "to":       extract(r"@to:(\S+)", envelope_line),
            "fr":       extract(r"@fr:(\S+)", envelope_line),
            "type":     extract(r"@t:(\S+)", envelope_line),
            "priority": extract(r"@p:(\S+)", envelope_line),
        }

        # Extract params first, then remaining tokens are actions
        params = re.findall(r"\[([^\]]+)\]", body_line)
        body_without_params = re.sub(r"\[[^\]]+\]", "", body_line).strip()
        tokens = body_without_params.split()

        if strict:
            actions = []
            for token in tokens:
                if token.upper() in VERBS:
                    actions.append(token.upper())
                else:
                    raise DRIXLInvalidVerbError(f"Unknown verb in message body: '{token}'")
        else:
            actions = [token.upper() for token in tokens]

        return {
            "envelope": envelope,
            "actions":  actions,
            "params":   params,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Message":
        """
        Construct a Message object from a dictionary.

        Args:
            data: Dictionary with keys: to, fr, msg_type, priority, actions, params, ctx_ref (optional)

        Returns:
            Message instance
        """
        return Message(
            to=data["to"],
            fr=data["fr"],
            msg_type=data["msg_type"],
            priority=data["priority"],
            actions=data["actions"],
            params=data["params"],
            ctx_ref=data.get("ctx_ref")
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Message to dictionary.

        Returns:
            Dictionary representation of the message
        """
        result = {
            "to": self.to,
            "fr": self.fr,
            "msg_type": self.msg_type,
            "priority": self.priority,
            "actions": self.actions,
            "params": self.params,
        }
        if self.ctx_ref:
            result["ctx_ref"] = self.ctx_ref
        return result

    def reply(
        self,
        actions: List[str],
        params: List[str],
        priority: Optional[str] = None,
        ctx_ref: Optional[str] = None
    ) -> str:
        """
        Create a reply message (auto-swaps to/fr, sets type=RES).

        Args:
            actions: List of DRIXL verbs for the reply
            params: List of parameters for the reply
            priority: Priority (defaults to original message priority)
            ctx_ref: Context reference (defaults to original ctx_ref)

        Returns:
            Formatted DRIXL reply message string
        """
        return Message.build(
            to=self.fr,  # Reply to sender
            fr=self.to,  # From original recipient
            msg_type="RES",
            priority=priority or self.priority,
            actions=actions,
            params=params,
            ctx_ref=ctx_ref or self.ctx_ref
        )

    def __str__(self) -> str:
        """String representation of the message."""
        return Message.build(
            to=self.to, fr=self.fr, msg_type=self.msg_type,
            priority=self.priority, actions=self.actions,
            params=self.params, ctx_ref=self.ctx_ref
        )

    def __repr__(self) -> str:
        return f"Message(to={self.to}, fr={self.fr}, type={self.msg_type}, priority={self.priority})"
