"""
Tests for DRIXL ContextStore.
"""

from drixl import ContextStore


def test_set_and_get():
    store = ContextStore()
    store.set("ref#1", "Project: Test pipeline")
    assert store.get("ref#1") == "Project: Test pipeline"


def test_get_missing_returns_none():
    store = ContextStore()
    assert store.get("ref#99") is None


def test_delete():
    store = ContextStore()
    store.set("ref#1", "value")
    store.delete("ref#1")
    assert store.get("ref#1") is None


def test_all_refs():
    store = ContextStore()
    store.set("ref#1", "A")
    store.set("ref#2", "B")
    refs = store.all_refs()
    assert "ref#1" in refs
    assert "ref#2" in refs


def test_clear():
    store = ContextStore()
    store.set("ref#1", "A")
    store.set("ref#2", "B")
    store.clear()
    assert store.all_refs() == []
