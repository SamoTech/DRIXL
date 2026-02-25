"""
DRIXL Standard Verb Vocabulary
All inter-agent communication must use these verbs to maintain compressed format.
"""

from typing import Dict

VERBS: Dict[str, str] = {
    "ANLY":  "Analyze input data or content",
    "XTRCT": "Extract specific fields or values",
    "SUMM":  "Summarize content into a shorter form",
    "EXEC":  "Execute an action or command",
    "VALD":  "Validate output against a schema or rule",
    "ESCL":  "Escalate to human or manager agent",
    "ROUT":  "Route message or payload to another agent",
    "STOR":  "Save data to context store or memory",
    "FETCH": "Retrieve data from a URL or source",
    "CMPX":  "Compare two values and return diff",
    "FLTR":  "Filter a dataset by given criteria",
    "TRNSF": "Transform data format (e.g., JSON to CSV)",
    "NTFY":  "Notify agent or system of an event",
    "RETRY": "Retry the previous failed task",
    "HALT":  "Stop pipeline execution immediately",
}


def is_valid_verb(verb: str) -> bool:
    """Check if a verb is part of the official DRIXL vocabulary."""
    return verb.upper() in VERBS


def describe_verb(verb: str) -> str:
    """Return the full description of a verb."""
    return VERBS.get(verb.upper(), "Unknown verb")
