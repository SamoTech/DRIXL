#!/usr/bin/env python3
"""
Tests for DRIXL CLI commands.
Run with: pytest tests/test_cli.py
"""

import pytest
from click.testing import CliRunner
from drixl.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_version(runner):
    """Test drixl --version."""
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert '0.2.0' in result.output


def test_parse_valid_message(runner):
    """Test drixl parse with valid message."""
    msg = "@to:AGT2 @fr:AGT1 @t:REQ @p:HIGH\nANLY [input.json]"
    result = runner.invoke(cli, ['parse', msg])
    assert result.exit_code == 0
    assert '✓ Valid DRIXL message' in result.output
    assert 'AGT2' in result.output
    assert 'ANLY' in result.output


def test_parse_invalid_message(runner):
    """Test drixl parse with invalid message."""
    msg = "invalid message"
    result = runner.invoke(cli, ['parse', msg])
    assert result.exit_code == 1
    assert 'Parse Error' in result.output


def test_parse_json_output(runner):
    """Test drixl parse --json."""
    msg = "@to:AGT2 @fr:AGT1 @t:REQ @p:HIGH\nANLY [input.json]"
    result = runner.invoke(cli, ['parse', msg, '--json'])
    assert result.exit_code == 0
    assert '"to": "AGT2"' in result.output
    assert '"actions"' in result.output


def test_build_message(runner):
    """Test drixl build."""
    result = runner.invoke(cli, ['build'], input='AGT2\nAGT1\nREQ\nHIGH\nANLY\ninput.json\n')
    assert result.exit_code == 0
    assert '✓ Message built successfully' in result.output
    assert '@to:AGT2' in result.output
    assert 'ANLY' in result.output


def test_build_with_options(runner):
    """Test drixl build with command-line options."""
    result = runner.invoke(cli, [
        'build',
        '--to', 'AGT2',
        '--from', 'AGT1',
        '--type', 'REQ',
        '--priority', 'HIGH',
        '--actions', 'ANLY,XTRCT',
        '--params', 'input.json,out:json'
    ])
    assert result.exit_code == 0
    assert '@to:AGT2' in result.output
    assert 'ANLY' in result.output
    assert 'XTRCT' in result.output


def test_build_invalid_verb(runner):
    """Test drixl build with invalid verb."""
    result = runner.invoke(cli, [
        'build',
        '--to', 'AGT2',
        '--from', 'AGT1',
        '--type', 'REQ',
        '--priority', 'HIGH',
        '--actions', 'INVALID_VERB'
    ])
    assert result.exit_code == 1
    assert 'Invalid verbs' in result.output


def test_verbs_list(runner):
    """Test drixl verbs."""
    result = runner.invoke(cli, ['verbs'])
    assert result.exit_code == 0
    assert 'ANLY' in result.output
    assert 'XTRCT' in result.output
    assert 'Analyze' in result.output


def test_verbs_search(runner):
    """Test drixl verbs --search."""
    result = runner.invoke(cli, ['verbs', '--search', 'analyze'])
    assert result.exit_code == 0
    assert 'ANLY' in result.output


def test_verbs_json(runner):
    """Test drixl verbs --json."""
    result = runner.invoke(cli, ['verbs', '--json'])
    assert result.exit_code == 0
    assert '"ANLY"' in result.output
    assert '"XTRCT"' in result.output


def test_benchmark_default(runner):
    """Test drixl benchmark with default message."""
    result = runner.invoke(cli, ['benchmark'])
    # Will fail if tiktoken not installed, but that's expected
    if 'tiktoken' in result.output and result.exit_code == 1:
        pytest.skip("tiktoken not installed")
    assert 'Token Usage Comparison' in result.output or 'tiktoken' in result.output


def test_benchmark_custom_message(runner):
    """Test drixl benchmark with custom message."""
    msg = "@to:AGT2 @fr:AGT1 @t:REQ @p:HIGH\nANLY [input.json]"
    result = runner.invoke(cli, ['benchmark', msg])
    if 'tiktoken' in result.output and result.exit_code == 1:
        pytest.skip("tiktoken not installed")
    assert 'Token Usage Comparison' in result.output or 'tiktoken' in result.output
