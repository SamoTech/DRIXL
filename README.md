<h1 align="center">
    <a href="https://github.com/SamoTech/DRIXL">
        DRIXL
    </a>
    <br>
    <small>Compressed Inter-Agent Communication Language — Built for Speed, Cost, and Scale</small>
</h1>

<p align="center">
    <a href="https://github.com/SamoTech/DRIXL/actions/workflows/tests.yml">
        <img alt="Tests" src="https://github.com/SamoTech/DRIXL/actions/workflows/tests.yml/badge.svg"></a>
    <a href="https://pypi.org/project/drixl/">
        <img alt="PyPI version" src="https://badge.fury.io/py/drixl.svg"></a>
    <a href="https://pypi.org/project/drixl/">
        <img alt="Supported Python versions" src="https://img.shields.io/pypi/pyversions/drixl.svg"></a>
    <a href="https://github.com/SamoTech/DRIXL/blob/main/LICENSE">
        <img alt="License" src="https://img.shields.io/badge/license-MIT-blue.svg"></a>
</p>

<p align="center">
    <a href="#key-concepts"><strong>Key Concepts</strong></a>
    &middot;
    <a href="#verb-vocabulary"><strong>Verb Vocabulary</strong></a>
    &middot;
    <a href="#message-format"><strong>Message Format</strong></a>
    &middot;
    <a href="#context-store"><strong>Context Store</strong></a>
    &middot;
    <a href="#getting-started"><strong>Getting Started</strong></a>
    &middot;
    <a href="#benchmarks"><strong>Benchmarks</strong></a>
</p>

DRIXL is a compressed inter-agent communication language designed to minimize token usage and maximize value when running multiple AI agents together. Instead of agents exchanging verbose natural language, DRIXL provides a structured, minimal signal format — cutting communication overhead by up to 80%.

One standard. All agents. Zero waste.

```python
from drixl import Message, ContextStore

# Build a compressed inter-agent message
msg = Message.build(
    to="AGT2",
    fr="AGT1",
    msg_type="REQ",
    priority="HIGH",
    actions=["ANLY", "XTRCT"],
    params=["firewall.json", "denied_ips", "out:json"],
    ctx_ref="ref#1"
)
print(msg)
# @to:AGT2 @fr:AGT1 @t:REQ @p:HIGH
# ANLY XTRCT [firewall.json] [denied_ips] [out:json] [ctx:ref#1]
```

Or parse an incoming DRIXL message:
```python
from drixl import Message

raw = "@to:AGT3 @fr:AGT2 @t:RES @p:MED\nVALD [suspicious_ips:14] [src:threat_db] [out:json] [ctx:ref#1]"
parsed = Message.parse(raw)
print(parsed)
# {'envelope': {'to': 'AGT3', 'fr': 'AGT2', 'type': 'RES', 'priority': 'MED'},
#  'actions': ['VALD'], 'params': ['suspicious_ips:14', 'src:threat_db', 'out:json', 'ctx:ref#1']}
```

---

## Key Concepts

### Why DRIXL?

When multiple AI agents communicate using natural language, tokens are wasted on:
- Politeness phrases and filler words
- Redundant context repetition every message
- Verbose JSON field names
- Re-explaining roles each turn

DRIXL solves this with three layers:
- 📦 **Compressed Envelope** — Minimal header with routing, type, and priority
- 🗂️ **Shared Context Store** — Store context once, reference by ID forever
- 🔤 **Verb Shortcodes** — Fixed vocabulary of 4–6 letter action codes

### Token Savings

| Scenario | Saving |
|---|---|
| Per-message compression | ~70% reduction |
| Shared context (no repetition) | ~60% reduction |
| Verb vocabulary vs. prose | ~40% reduction |
| **Combined at scale** | **Up to 80% total** |

---

## Message Format

Every DRIXL message has two parts — an **envelope** and a **body**:

```
@to:AGT2 @fr:AGT1 @t:REQ @p:HIGH
ANLY XTRCT [input_file] [output:json] [ctx:ref#3]
```

### Envelope Fields

| Field | Values | Description |
|---|---|---|
| `@to` | Agent ID | Recipient agent |
| `@fr` | Agent ID | Sender agent |
| `@t` | REQ / RES / ERR / FIN | Message type |
| `@p` | HIGH / MED / LOW | Priority |

### Message Types

| Type | Meaning |
|---|---|
| `REQ` | Request — asking another agent to perform a task |
| `RES` | Response — returning results to sender |
| `ERR` | Error — reporting a failure with details |
| `FIN` | Finalize — signaling pipeline completion |

---

## Verb Vocabulary

DRIXL uses a fixed set of action verbs. All agents share this vocabulary:

| Verb | Full Meaning | Example |
|---|---|---|
| `ANLY` | Analyze | `ANLY [logs.json]` |
| `XTRCT` | Extract | `XTRCT [denied_ips]` |
| `SUMM` | Summarize | `SUMM [report.txt] [out:json]` |
| `EXEC` | Execute action | `EXEC [throttle_ip] [192.168.1.45]` |
| `VALD` | Validate output | `VALD [result] [schema:strict]` |
| `ESCL` | Escalate to human | `ESCL [reason:low_confidence]` |
| `ROUT` | Route to agent | `ROUT [AGT3] [payload:ref#5]` |
| `STOR` | Save to memory | `STOR [key:last_result] [val:ref#4]` |
| `FETCH` | Retrieve data | `FETCH [url:https://...] [out:html]` |
| `CMPX` | Compare values | `CMPX [val_a] [val_b] [out:diff]` |

---

## Context Store

Instead of repeating context in every message, DRIXL uses a shared **Context Store** — agents reference context by ID:

```python
from drixl import ContextStore

store = ContextStore()  # Uses in-memory store by default (Redis supported)

# Store context once
store.set("ref#1", "Project: Network security monitoring pipeline")
store.set("ref#2", "Output format: {ip, action, timestamp, confidence}")
store.set("ref#3", "Constraints: no action if confidence < 0.85")

# Agents reference it — never repeat it
print(store.get("ref#1"))  # 'Project: Network security monitoring pipeline'
```

With Redis backend for multi-agent shared state:
```python
from drixl import ContextStore

store = ContextStore(backend="redis", host="localhost", port=6379)
store.set("ref#1", "Project goal: MikroTik bandwidth monitor")
```

---

## Getting Started

### Installation

DRIXL requires Python 3.10 or higher:

```bash
pip install drixl
```

With Redis context store support:
```bash
pip install "drixl[redis]"
```

Install everything:
```bash
pip install "drixl[all]"
```

### Quick Example — 3 Agent Pipeline

```python
from drixl import Message, ContextStore

# Shared context — defined once
store = ContextStore()
store.set("ref#1", "Project: Firewall threat detection")
store.set("ref#2", "Output: JSON array [{ip, count, risk_level}]")

# Agent 1 → Agent 2: Analyze logs
msg_1 = Message.build(
    to="AGT2", fr="AGT1", msg_type="REQ", priority="HIGH",
    actions=["ANLY"], params=["firewall.log", "out:json"],
    ctx_ref="ref#1"
)

# Agent 2 → Agent 3: Validate findings
msg_2 = Message.build(
    to="AGT3", fr="AGT2", msg_type="RES", priority="HIGH",
    actions=["VALD", "ROUT"], params=["findings:14_ips", "AGT3"],
    ctx_ref="ref#2"
)

# Agent 3 → Orchestrator: Done
msg_3 = Message.build(
    to="ORCH", fr="AGT3", msg_type="FIN", priority="MED",
    actions=["STOR"], params=["key:threat_report", "val:ref#7"]
)

print(msg_1)
print(msg_2)
print(msg_3)
```

---

## Benchmarks

Token count comparison: DRIXL vs Natural Language vs JSON vs XML for the same instruction:

| # | Method | Tokens | vs DRIXL |
|---|---|---|---|
| 1 | DRIXL message | ~25 | 1.0x |
| 2 | Structured JSON | ~60 | ~2.4x |
| 3 | Natural language | ~120 | ~4.8x |
| 4 | XML (verbose) | ~140 | ~5.6x |

> Benchmarks measured using OpenAI `tiktoken` on 100+ real agent message samples. See [benchmarks.py](https://github.com/SamoTech/DRIXL/blob/main/benchmarks.py) for methodology.

---

## Project Structure

```
DRIXL/
├── drixl/
│   ├── __init__.py          # Public API
│   ├── message.py           # Message builder & parser
│   ├── context_store.py     # Shared context store (memory + Redis)
│   ├── verbs.py             # Standard verb vocabulary
│   └── exceptions.py        # Custom exceptions
├── examples/
│   ├── basic_pipeline.py    # 3-agent pipeline example
│   ├── network_monitor.py   # Network agent example
│   └── web_pipeline.py      # Web scraping agent example
├── tests/
│   ├── test_message.py
│   ├── test_context_store.py
│   └── test_verbs.py
├── .github/
│   └── workflows/
│       └── tests.yml
├── benchmarks.py
├── CONTRIBUTING.md
├── ROADMAP.md
├── LICENSE
├── pyproject.toml
└── README.md
```

---

## Contributing

We welcome contributions! Please read our [contributing guidelines](https://github.com/SamoTech/DRIXL/blob/main/CONTRIBUTING.md) before getting started.

> [!NOTE]
> DRIXL is in active early development. The verb vocabulary and message format are open for community input — open an issue to propose new verbs or format extensions.

> [!CAUTION]
> DRIXL is a communication protocol standard. Implementations using DRIXL are responsible for validating inputs and outputs. Never pass unvalidated agent outputs directly to execution functions.

## License

This project is licensed under the MIT License — see [LICENSE](https://github.com/SamoTech/DRIXL/blob/main/LICENSE) for details.

---
<div align="center"><small>Designed & crafted with ❤️ by Ossama Hashim — SamoTech.</small></div><br>
