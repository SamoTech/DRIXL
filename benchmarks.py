"""
DRIXL Benchmarks
Compares token usage: DRIXL vs Natural Language vs JSON vs XML.

Requires: pip install tiktoken
"""

import json

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    print("Install tiktoken for accurate token counts: pip install tiktoken")

from drixl import Message


def count_tokens(text: str, model: str = "gpt-4") -> int:
    if not TIKTOKEN_AVAILABLE:
        return len(text.split())
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))


DRIXL_MSG = Message.build(
    to="AGT2", fr="AGT1", msg_type="REQ", priority="HIGH",
    actions=["ANLY", "XTRCT"],
    params=["firewall.log", "denied_ips", "out:json"],
    ctx_ref="ref#1"
)

JSON_MSG = json.dumps({
    "to": "AGT2", "from": "AGT1", "message_type": "REQUEST", "priority": "HIGH",
    "actions": ["analyze", "extract"],
    "parameters": {"input": "firewall.log", "extract": "denied_ips", "output_format": "json"},
    "context_reference": "ref#1"
})

NATURAL_MSG = (
    "Agent 1 to Agent 2: Please analyze the attached firewall log file called firewall.log, "
    "extract all denied IP addresses from it, and return the results in JSON format. "
    "The project context is stored under reference ref#1 - this is a firewall threat detection pipeline."
)

XML_MSG = """<message>
  <to>AGT2</to><from>AGT1</from><type>REQUEST</type><priority>HIGH</priority>
  <actions><action>analyze</action><action>extract</action></actions>
  <params><input>firewall.log</input><extract>denied_ips</extract><output>json</output></params>
  <context_reference>ref#1</context_reference>
</message>"""

formats = {
    "DRIXL": DRIXL_MSG,
    "JSON": JSON_MSG,
    "Natural Language": NATURAL_MSG,
    "XML (verbose)": XML_MSG,
}

print("\n=== DRIXL Token Benchmark ===")
print(f"{'Format':<20} {'Tokens':>8} {'vs DRIXL':>10}")
print("-" * 42)

drixl_tokens = count_tokens(DRIXL_MSG)
for name, text in formats.items():
    tokens = count_tokens(text)
    ratio = f"{tokens / drixl_tokens:.2f}x"
    print(f"{name:<20} {tokens:>8} {ratio:>10}")
