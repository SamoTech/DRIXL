"""
DRIXL Custom Exceptions
"""


class DRIXLError(Exception):
    """Base exception for all DRIXL errors."""
    pass


class DRIXLParseError(DRIXLError):
    """Raised when a DRIXL message cannot be parsed."""
    pass


class DRIXLInvalidVerbError(DRIXLError):
    """Raised when an unknown verb is used in a message."""
    pass


class DRIXLContextError(DRIXLError):
    """Raised when a context reference cannot be found."""
    pass
