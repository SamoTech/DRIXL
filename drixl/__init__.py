"""
DRIXL — Direct Signal Inter-Agent Language
Compressed inter-agent communication protocol for multi-agent AI systems.
"""

__version__ = "0.2.0"
__author__ = "Ossama Hashim"
__license__ = "MIT"

from drixl.message import Message
from drixl.context_store import ContextStore
from drixl.verbs import VERBS, is_valid_verb

__all__ = ["Message", "ContextStore", "VERBS", "is_valid_verb"]
