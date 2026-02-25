"""
DRIXL Message Builder and Parser
Handles construction and parsing of DRIXL-format inter-agent messages.
"""

import re
from typing import Optional
from drixl.verbs import VERBS
from drixl.exceptions import DRIXLParseError, DRIXLInvalidVerbError


MESSAGE_TYPES = {"REQ", "RES", "ERR", "FIN"}
PRIORITIES = {"HIGH", "MED", "LOW"}


class Message:
    """DRIXL Message — builder and parser for inter-agent signals."""

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
    def parse(raw: str) -> dict:
        """
        Parse a raw DRIXL message string into a structured dictionary.

        Args:
            raw: Raw DRIXL message string

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

        actions = [word for word in body_line.split() if word.upper() in VERBS]
        params = re.findall(r"\[([^\]]+)\]", body_line)

        return {
            "envelope": envelope,
            "actions":  actions,
            "params":   params,
        }
