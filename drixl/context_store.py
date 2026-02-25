"""
DRIXL Context Store
Shared memory layer for inter-agent context references.
Agents pass ref IDs instead of repeating full context - saving up to 60% tokens.
"""

from typing import Optional, Dict, Any


class ContextStore:
    """
    In-memory or Redis-backed context store for DRIXL agents.

    Usage:
        store = ContextStore()  # In-memory
        store = ContextStore(backend='redis', host='localhost', port=6379)  # Redis

        store.set('ref#1', 'Project: Network security monitoring')
        store.get('ref#1')  # -> 'Project: Network security monitoring'
    """

    def __init__(self, backend: str = "memory", **kwargs: Any) -> None:
        self.backend = backend
        self._store: Dict[str, Any] = {}

        if backend == "redis":
            try:
                import redis
                self._redis = redis.Redis(
                    host=kwargs.get("host", "localhost"),
                    port=kwargs.get("port", 6379),
                    db=kwargs.get("db", 0),
                    decode_responses=True,
                )
            except ImportError:
                raise ImportError(
                    "Redis backend requires the 'redis' package. "
                    "Install it with: pip install \"drixl[redis]\""
                )

    def set(self, ref_id: str, value: Any) -> None:
        """Store a context value under a reference ID."""
        if self.backend == "redis":
            self._redis.set(f"drixl:{ref_id}", str(value))
        else:
            self._store[ref_id] = value

    def get(self, ref_id: str) -> Optional[Any]:
        """Retrieve a context value by reference ID."""
        if self.backend == "redis":
            return self._redis.get(f"drixl:{ref_id}")
        return self._store.get(ref_id)

    def delete(self, ref_id: str) -> None:
        """Remove a context reference."""
        if self.backend == "redis":
            self._redis.delete(f"drixl:{ref_id}")
        else:
            self._store.pop(ref_id, None)

    def all_refs(self) -> list:
        """Return all stored reference IDs."""
        if self.backend == "redis":
            return [k.replace("drixl:", "") for k in self._redis.keys("drixl:*")]
        return list(self._store.keys())

    def clear(self) -> None:
        """Clear all stored context."""
        if self.backend == "redis":
            for key in self._redis.keys("drixl:*"):
                self._redis.delete(key)
        else:
            self._store.clear()
