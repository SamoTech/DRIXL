"""
Tests for DRIXL Verb Vocabulary.
"""

from drixl import VERBS, is_valid_verb
from drixl.verbs import describe_verb


def test_standard_verbs_exist():
    required = ["ANLY", "XTRCT", "SUMM", "EXEC", "VALD", "ESCL", "ROUT", "STOR"]
    for verb in required:
        assert verb in VERBS


def test_valid_verb_check():
    assert is_valid_verb("ANLY") is True
    assert is_valid_verb("anly") is True
    assert is_valid_verb("UNKNOWN") is False


def test_describe_verb():
    desc = describe_verb("ANLY")
    assert len(desc) > 0
    assert describe_verb("NOTEXIST") == "Unknown verb"
