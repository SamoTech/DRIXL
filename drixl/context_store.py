"""
DRIXL Context Store
Shared memory layer for inter-agent context references.
Agents pass ref IDs instead of repeating full context - saving up to 60% tokens.
"""

import time
import warnings
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
        self._ttl_store: Dict[str, float] = {}  # Expiry timestamps for memory backend

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

    def set(self, ref_id: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store a context value under a reference ID.

        Args:
            ref_id: Reference identifier
            value: Value to store
            ttl: Time-to-live in seconds (optional)
        """
        if self.backend == "redis":
            if ttl:
                self._redis.setex(f"drixl:{ref_id}", ttl, str(value))
            else:
                self._redis.set(f"drixl:{ref_id}", str(value))
        else:
            self._store[ref_id] = value
            if ttl:
                self._ttl_store[ref_id] = time.time() + ttl

    def get(self, ref_id: str) -> Optional[Any]:
        """
        Retrieve a context value by reference ID.

        Args:
            ref_id: Reference identifier

        Returns:
            Stored value or None if not found/expired
        """
        if self.backend == "redis":
            return self._redis.get(f"drixl:{ref_id}")
        else:
            # Check TTL expiry
            if ref_id in self._ttl_store:
                if time.time() > self._ttl_store[ref_id]:
                    # Expired
                    self._store.pop(ref_id, None)
                    self._ttl_store.pop(ref_id, None)
                    return None
            return self._store.get(ref_id)

    def delete(self, ref_id: str) -> None:
        """
        Remove a context reference.

        Args:
            ref_id: Reference identifier
        """
        if self.backend == "redis":
            self._redis.delete(f"drixl:{ref_id}")
        else:
            self._store.pop(ref_id, None)
            self._ttl_store.pop(ref_id, None)

    def all_refs(self) -> list:
        """
        Return all stored reference IDs.

        Returns:
            List of reference identifiers
        """
        if self.backend == "redis":
            return [k.replace("drixl:", "") for k in self._redis.keys("drixl:*")]
        else:
            # Filter out expired keys
            current_time = time.time()
            valid_refs = []
            for ref_id in list(self._store.keys()):
                if ref_id in self._ttl_store:
                    if current_time <= self._ttl_store[ref_id]:
                        valid_refs.append(ref_id)
                    else:
                        # Clean up expired
                        self._store.pop(ref_id, None)
                        self._ttl_store.pop(ref_id, None)
                else:
                    valid_refs.append(ref_id)
            return valid_refs

    def clear(self) -> None:
        """
        Clear all stored context.
        """
        if self.backend == "redis":
            for key in self._redis.keys("drixl:*"):
                self._redis.delete(key)
        else:
            self._store.clear()
            self._ttl_store.clear()
