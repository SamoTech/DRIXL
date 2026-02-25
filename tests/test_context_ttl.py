"""
Tests for ContextStore TTL support in memory backend.
"""

import time
from drixl import ContextStore


def test_memory_backend_ttl_expires():
    """Test TTL expiry in memory backend."""
    store = ContextStore(backend="memory")
    store.set("ref#1", "value", ttl=1)  # 1 second TTL
    assert store.get("ref#1") == "value"
    time.sleep(1.1)
    assert store.get("ref#1") is None  # Should be expired


def test_memory_backend_ttl_not_expired():
    """Test TTL not expired yet."""
    store = ContextStore(backend="memory")
    store.set("ref#2", "value", ttl=5)
    assert store.get("ref#2") == "value"
    time.sleep(1)
    assert store.get("ref#2") == "value"  # Still valid


def test_memory_backend_no_ttl():
    """Test keys without TTL never expire."""
    store = ContextStore(backend="memory")
    store.set("ref#3", "permanent")
    time.sleep(1)
    assert store.get("ref#3") == "permanent"


def test_all_refs_filters_expired():
    """Test all_refs() excludes expired keys."""
    store = ContextStore(backend="memory")
    store.set("ref#1", "value1", ttl=1)
    store.set("ref#2", "value2")  # No TTL
    assert "ref#1" in store.all_refs()
    time.sleep(1.1)
    refs = store.all_refs()
    assert "ref#1" not in refs
    assert "ref#2" in refs
