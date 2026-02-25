#!/usr/bin/env python3
"""
DRIXL Command-Line Interface
Tools for building, parsing, validating, and benchmarking DRIXL messages.
"""

import sys
import json
from typing import Optional

try:
    import click
except ImportError:
    print("Error: CLI requires 'click' package. Install with: pip install 'drixl[cli]'")
    sys.exit(1)

from drixl import Message, VERBS, is_valid_verb
from drixl.exceptions import DRIXLParseError, DRIXLInvalidVerbError


@click.group()
@click.version_option()
def cli():
    """DRIXL - Compressed Inter-Agent Communication Language CLI"""
    pass


@cli.command()
@click.argument('message', required=False)
@click.option('--strict/--lenient', default=True, help='Strict verb validation (default: strict)')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def parse(message: Optional[str], strict: bool, output_json: bool):
    """
    Parse and validate a DRIXL message.
    
    EXAMPLE:
        drixl parse "@to:AGT2 @fr:AGT1 @t:REQ @p:HIGH\\nANLY [input.json]"
    
    If no message is provided, reads from stdin.
    """
    if not message:
        click.echo("Reading from stdin... (Ctrl+D when done)")
        message = sys.stdin.read().strip()
    
    if not message:
        click.echo("Error: No message provided", err=True)
        sys.exit(1)
    
    try:
        parsed = Message.parse(message, strict=strict)
        
        if output_json:
            click.echo(json.dumps(parsed, indent=2))
        else:
            click.echo(click.style("✓ Valid DRIXL message", fg='green', bold=True))
            click.echo()
            click.echo(click.style("Envelope:", bold=True))
            click.echo(f"  To:       {parsed['envelope']['to']}")
            click.echo(f"  From:     {parsed['envelope']['fr']}")
            click.echo(f"  Type:     {parsed['envelope']['type']}")
            click.echo(f"  Priority: {parsed['envelope']['priority']}")
            click.echo()
            click.echo(click.style("Actions:", bold=True))
            for action in parsed['actions']:
                click.echo(f"  - {action} ({VERBS.get(action, 'Unknown')})") 
            click.echo()
            click.echo(click.style("Parameters:", bold=True))
            for param in parsed['params']:
                click.echo(f"  - {param}")
    
    except (DRIXLParseError, DRIXLInvalidVerbError) as e:
        click.echo(click.style(f"✗ Parse Error: {e}", fg='red', bold=True), err=True)
        sys.exit(1)


@cli.command()
@click.option('--to', prompt='Recipient agent', help='Recipient agent ID')
@click.option('--from', 'fr', prompt='Sender agent', help='Sender agent ID')
@click.option('--type', 'msg_type', type=click.Choice(['REQ', 'RES', 'ERR', 'FIN']), 
              prompt='Message type', help='Message type')
@click.option('--priority', type=click.Choice(['HIGH', 'MED', 'LOW']), 
              prompt='Priority', default='MED', help='Message priority')
@click.option('--actions', prompt='Actions (comma-separated)', help='DRIXL verbs')
@click.option('--params', default='', help='Parameters (comma-separated)')
@click.option('--ctx-ref', help='Context reference ID')
def build(to: str, fr: str, msg_type: str, priority: str, actions: str, params: str, ctx_ref: Optional[str]):
    """
    Build a DRIXL message interactively.
    
    EXAMPLE:
        drixl build --to AGT2 --from AGT1 --type REQ --priority HIGH --actions ANLY,XTRCT --params input.json,out:json
    """
    actions_list = [a.strip().upper() for a in actions.split(',') if a.strip()]
    params_list = [p.strip() for p in params.split(',') if p.strip()]
    
    # Validate verbs
    invalid_verbs = [v for v in actions_list if not is_valid_verb(v)]
    if invalid_verbs:
        click.echo(click.style(f"✗ Invalid verbs: {', '.join(invalid_verbs)}", fg='red'), err=True)
        click.echo("Run 'drixl verbs' to see all valid verbs.")
        sys.exit(1)
    
    try:
        msg = Message.build(
            to=to, fr=fr, msg_type=msg_type, priority=priority,
            actions=actions_list, params=params_list, ctx_ref=ctx_ref
        )
        click.echo()
        click.echo(click.style("✓ Message built successfully:", fg='green', bold=True))
        click.echo()
        click.echo(msg)
    except Exception as e:
        click.echo(click.style(f"✗ Build Error: {e}", fg='red', bold=True), err=True)
        sys.exit(1)


@cli.command()
@click.option('--search', help='Search verbs by keyword')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def verbs(search: Optional[str], output_json: bool):
    """
    List all DRIXL standard verbs.
    
    EXAMPLE:
        drixl verbs
        drixl verbs --search analyze
    """
    verbs_list = list(VERBS.items())
    
    if search:
        search_lower = search.lower()
        verbs_list = [(v, desc) for v, desc in verbs_list 
                      if search_lower in v.lower() or search_lower in desc.lower()]
    
    if output_json:
        click.echo(json.dumps(dict(verbs_list), indent=2))
    else:
        if search:
            click.echo(click.style(f"Verbs matching '{search}':", bold=True))
        else:
            click.echo(click.style(f"DRIXL Standard Verbs ({len(verbs_list)} total):", bold=True))
        click.echo()
        
        for verb, description in sorted(verbs_list):
            click.echo(f"  {click.style(verb, fg='cyan', bold=True):8} {description}")
        
        if not verbs_list and search:
            click.echo(click.style(f"No verbs found matching '{search}'", fg='yellow'))


@cli.command()
@click.argument('message', required=False)
@click.option('--model', default='gpt-4', help='Model for token counting (default: gpt-4)')
def benchmark(message: Optional[str], model: str):
    """
    Compare DRIXL token usage vs JSON/Natural Language.
    
    EXAMPLE:
        drixl benchmark "@to:AGT2 @fr:AGT1 @t:REQ @p:HIGH\\nANLY XTRCT [firewall.log] [denied_ips] [out:json]"
    
    If no message is provided, uses a default example.
    """
    try:
        import tiktoken
    except ImportError:
        click.echo("Error: Benchmark requires 'tiktoken'. Install with: pip install 'drixl[dev]'", err=True)
        sys.exit(1)
    
    if not message:
        # Default example
        message = Message.build(
            to="AGT2", fr="AGT1", msg_type="REQ", priority="HIGH",
            actions=["ANLY", "XTRCT"],
            params=["firewall.log", "denied_ips", "out:json"],
            ctx_ref="ref#1"
        )
    
    try:
        enc = tiktoken.encoding_for_model(model)
    except KeyError:
        click.echo(f"Warning: Unknown model '{model}', using cl100k_base encoding", err=True)
        enc = tiktoken.get_encoding("cl100k_base")
    
    # DRIXL tokens
    drixl_tokens = len(enc.encode(message))
    
    # Equivalent JSON
    parsed = Message.parse(message, strict=False)
    json_equivalent = json.dumps({
        "to": parsed['envelope']['to'],
        "from": parsed['envelope']['fr'],
        "message_type": parsed['envelope']['type'],
        "priority": parsed['envelope']['priority'],
        "actions": parsed['actions'],
        "parameters": parsed['params']
    })
    json_tokens = len(enc.encode(json_equivalent))
    
    # Natural language equivalent
    natural = (
        f"Agent {parsed['envelope']['fr']} to Agent {parsed['envelope']['to']}: "
        f"Please {', '.join(parsed['actions']).lower()} with parameters {', '.join(parsed['params'])}. "
        f"Priority: {parsed['envelope']['priority']}."
    )
    natural_tokens = len(enc.encode(natural))
    
    # Display results
    click.echo()
    click.echo(click.style("Token Usage Comparison", bold=True, fg='cyan'))
    click.echo(click.style("=" * 50, fg='cyan'))
    click.echo()
    
    click.echo(f"{'Format':<20} {'Tokens':>10} {'vs DRIXL':>12} {'Savings':>10}")
    click.echo("-" * 54)
    
    formats = [
        ("DRIXL", drixl_tokens, 1.0),
        ("JSON", json_tokens, json_tokens / drixl_tokens),
        ("Natural Language", natural_tokens, natural_tokens / drixl_tokens)
    ]
    
    for name, tokens, ratio in formats:
        savings = f"{(1 - 1/ratio) * 100:.0f}%" if ratio > 1 else "-"
        color = 'green' if name == "DRIXL" else 'yellow' if ratio < 2 else 'red'
        click.echo(
            f"{name:<20} "
            f"{click.style(str(tokens), fg=color):>10} "
            f"{ratio:>11.2f}x "
            f"{savings:>10}"
        )
    
    click.echo()
    click.echo(click.style(f"✓ DRIXL saves ~{((natural_tokens - drixl_tokens) / natural_tokens * 100):.0f}% tokens vs natural language", 
                          fg='green', bold=True))


if __name__ == '__main__':
    cli()
