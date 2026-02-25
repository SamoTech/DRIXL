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
    <br/>
    <a href="https://github.com/sponsors/SamoTech">
        <img alt="Sponsor" src="https://img.shields.io/badge/Sponsor-%E2%9D%A4-ea4aaa?logo=github-sponsors"></a>
    <br/>
    <img alt="Visitors" src="https://visitor-badge.laobi.icu/badge?page_id=SamoTech.DRIXL">
    <img alt="GitHub Stars" src="https://img.shields.io/github/stars/SamoTech/DRIXL?style=social">
    <img alt="GitHub Forks" src="https://img.shields.io/github/forks/SamoTech/DRIXL?style=social">
</p>

<p align="center">
    <a href="#key-concepts"><strong>Key Concepts</strong></a>
    &middot;
    <a href="#dual-format-support"><strong>Dual Format Support</strong></a>
    &middot;
    <a href="#message-format"><strong>Message Format</strong></a>
    &middot;
    <a href="#verb-vocabulary"><strong>Verb Vocabulary</strong></a>
    &middot;
    <a href="#context-store"><strong>Context Store</strong></a>
    &middot;
    <a href="#getting-started"><strong>Getting Started</strong></a>
    &middot;
    <a href="#cli-tool"><strong>CLI Tool</strong></a>
</p>

DRIXL is a compressed inter-agent communication language designed to minimize token usage and maximize value when running multiple AI agents together. Instead of agents exchanging verbose natural language, DRIXL provides a structured, minimal signal format — cutting communication overhead by up to 80%.

**NEW in v0.3.0:** DRIXL now supports **dual formats** — use compact mode for production (80% token savings) or structured XML mode for development/debugging with full traceability.

One standard. All agents. Zero waste.

```python
from drixl import Message

# Compact format (production) — 80% token savings
msg = Message.build(
    to="AGT2", fr="AGT1", msg_type="REQ", priority="HIGH",
    actions=["ANLY", "XTRCT"], params=["firewall.json"],
    format="compact"  # Default
)
print(msg)
# @to:AGT2 @fr:AGT1 @t:REQ @p:HIGH
# ANLY XTRCT [firewall.json]

# Structured format (development) — Full traceability
msg = Message.build(
    to="AGT2", fr="AGT1", msg_type="REQ", priority="HIGH",
    actions=["ANLY", "XTRCT"], params=["firewall.json"],
    format="structured",  # NEW!
    intent="Analyze firewall logs and extract denied IPs"
)
# Returns full XML with metadata, thread tracking, status
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

## Dual Format Support

**New in v0.3.0:** DRIXL supports two message formats — choose based on your needs:

| Format | Use Case | Token Usage | Features |
|---|---|---|---|
| **Compact** | Production agents | ~25 tokens | Cost-optimized, minimal overhead |
| **Structured (XML)** | Dev/debugging | ~150 tokens | Full traceability, artifacts, critique workflow |

### When to Use Each Format

#### Compact Format (Production)
Use `format="compact"` (default) when:
- Running production agent pipelines
- Minimizing API costs is critical
- You need maximum throughput
- Messages are simple request/response patterns

```python
from drixl import Message

msg = Message.build(
    to="AGT2", fr="AGT1", msg_type="REQ", priority="HIGH",
    actions=["ANLY"], params=["input.json"],
    format="compact"  # Default, can be omitted
)
# Output: @to:AGT2 @fr:AGT1 @t:REQ @p:HIGH\nANLY [input.json]
```

#### Structured Format (Development)
Use `format="structured"` when:
- Debugging multi-agent workflows
- Need full audit trails with thread IDs
- Implementing critique/review workflows
- Attaching code artifacts or test results
- Tracking multi-round iterations

```python
from drixl import StructuredMessage

msg = StructuredMessage(
    to="AGT-QA", fr="AGT-DEV", msg_type="RESPONSE",
    intent="Deliver implementation for code review",
    content="Implementation complete. See artifact ART-001.",
    priority="HIGH", status="PENDING"
)

# Add code artifact
msg.add_artifact("code", """
def validate_envelope(raw: str) -> dict:
    # Implementation
    pass
""", artifact_id="ART-001")

xml = msg.to_xml()
```

### Format Conversion

Convert between formats as needed:

```python
from drixl.converter import compact_to_structured, structured_to_compact

# Compact → Structured (add metadata for debugging)
compact = "@to:AGT2 @fr:AGT1 @t:REQ @p:HIGH\nANLY [input.json]"
structured = compact_to_structured(
    compact,
    intent="Analyze input data",
    thread_id="THREAD-042",
    status="PENDING"
)

# Structured → Compact (strip metadata for production)
compact_again = structured_to_compact(
    structured, 
    actions=["ANLY"], 
    params=["input.json"]
)
```

### Auto-Detection

DRIXL automatically detects the message format:

```python
from drixl import Message

# Parses compact format
compact = "@to:AGT2 @fr:AGT1 @t:REQ @p:HIGH\nANLY [input.json]"
parsed = Message.parse(compact)  # Auto-detects

# Parses structured format
xml = "<message><meta>...</meta>...</message>"
parsed = Message.parse(xml)  # Auto-detects
```

---

## Message Format

### Compact Format

Every compact DRIXL message has two parts — an **envelope** and a **body**:

```
@to:AGT2 @fr:AGT1 @t:REQ @p:HIGH
ANLY XTRCT [input_file] [output:json] [ctx:ref#3]
```

#### Envelope Fields

| Field | Values | Description |
|---|---|---|
| `@to` | Agent ID | Recipient agent |
| `@fr` | Agent ID | Sender agent |
| `@t` | REQ / RES / ERR / FIN | Message type |
| `@p` | HIGH / MED / LOW | Priority |

#### Message Types

| Type | Meaning |
|---|---|
| `REQ` | Request — asking another agent to perform a task |
| `RES` | Response — returning results to sender |
| `ERR` | Error — reporting a failure with details |
| `FIN` | Finalize — signaling pipeline completion |

### Structured Format

Structured messages use XML with rich metadata:

```xml
<message>
  <meta>
    <msg_id>MSG-A3F2B1C4</msg_id>
    <thread_id>THREAD-D7E8F9A0</thread_id>
    <reply_to>MSG-XYZ</reply_to>
    <timestamp>2026-02-25T20:00:00</timestamp>
    <priority>HIGH</priority>
  </meta>
  <envelope>
    <to>AGT2</to>
    <from>AGT1</from>
    <type>REQUEST</type>
    <intent>Analyze firewall logs</intent>
  </envelope>
  <content>Detailed instructions...</content>
  <artifacts>
    <artifact type="code" id="ART-001">...</artifact>
  </artifacts>
  <status>PENDING</status>
  <next_action>AGT2 should ACK and begin</next_action>
</message>
```

#### Structured Message Types

| Type | Meaning |
|---|---|
| `REQUEST` | Task delegation |
| `RESPONSE` | Result delivery |
| `CRITIQUE` | Code review with structured feedback |
| `DELEGATE` | Pass task to another agent |
| `ACK` | Acknowledge receipt |
| `ESCALATE` | Raise unresolved issue to orchestrator |
| `FINALIZE` | Mark task complete |

---

## Verb Vocabulary

DRIXL uses a fixed set of action verbs (21 total). All agents share this vocabulary:

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
| `RETRY` | Retry task | `RETRY [max:3] [delay:5s]` |
| `MERGE` | Merge results | `MERGE [source_a] [source_b]` |
| `SPLIT` | Split for parallel | `SPLIT [batch:10]` |
| `AUTH` | Authenticate | `AUTH [token:xyz]` |
| `LOG` | Emit log entry | `LOG [level:info]` |
| `WAIT` | Pause execution | `WAIT [condition:ready]` |
| `CACHE` | Cache result | `CACHE [ttl:300]` |
| `FLTR` | Filter dataset | `FLTR [criteria:active]` |
| `TRNSF` | Transform format | `TRNSF [from:json] [to:csv]` |
| `NTFY` | Notify event | `NTFY [alert:threshold]` |
| `HALT` | Stop pipeline | `HALT [reason:error]` |

---

## Context Store

Instead of repeating context in every message, DRIXL uses a shared **Context Store** — agents reference context by ID:

```python
from drixl import ContextStore

store = ContextStore()  # Uses in-memory store by default

# Store context once
store.set("ref#1", "Project: Network security monitoring pipeline")
store.set("ref#2", "Output format: {ip, action, timestamp, confidence}")
store.set("ref#3", "Constraints: no action if confidence < 0.85")

# Agents reference it — never repeat it
print(store.get("ref#1"))  # 'Project: Network security monitoring pipeline'

# TTL support (NEW in v0.1.1)
store.set("ref#4", "Temporary data", ttl=300)  # Expires in 5 minutes
```

With Redis backend for multi-agent shared state:
```python
from drixl import ContextStore

store = ContextStore(backend="redis", host="localhost", port=6379)
store.set("ref#1", "Project goal: MikroTik bandwidth monitor", ttl=3600)
```

---

## Getting Started

### Installation

DRIXL requires Python 3.10 or higher:

```bash
pip install drixl
```

With CLI tools:
```bash
pip install "drixl[cli]"
```

With Redis context store support:
```bash
pip install "drixl[redis]"
```

Install everything:
```bash
pip install "drixl[all]"
```

### Quick Example — Compact Format (Production)

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

print(msg_1)
print(msg_2)
```

### Quick Example — Structured Format (Development)

```python
from drixl import StructuredMessage

# Developer sends implementation
dev_msg = StructuredMessage(
    to="AGT-QA", fr="AGT-DEV", msg_type="RESPONSE",
    intent="Deliver validate_envelope() for review",
    content="Implementation complete with type hints.",
    thread_id="THREAD-001"
)

dev_msg.add_artifact("code", """
def validate_envelope(raw: str) -> dict:
    # Implementation
    return {"to": "AGT2", "fr": "AGT1"}
""", artifact_id="ART-001")

dev_msg.add_artifact("test", """
def test_validate_envelope():
    result = validate_envelope("@to:AGT2...")
    assert result is not None
""", artifact_id="ART-002")

print(dev_msg.to_xml())

# QA sends critique
qa_msg = StructuredMessage(
    to="AGT-DEV", fr="AGT-QA", msg_type="CRITIQUE",
    intent="Review of validate_envelope()",
    content="""
    ISSUES:
    1. Missing error handling for empty strings
    2. No docstring
    
    SUGGESTIONS:
    1. Add try/except block
    2. Add comprehensive docstring
    
    VERDICT: REVISE
    """,
    reply_to=dev_msg.msg_id,
    thread_id=dev_msg.thread_id
)
```

---

## CLI Tool

**New in v0.2.0:** DRIXL includes a powerful command-line tool:

### Parse and Validate Messages
```bash
drixl parse "@to:AGT2 @fr:AGT1 @t:REQ @p:HIGH\nANLY [input.json]"
# ✓ Valid DRIXL message
# Envelope:
#   To:       AGT2
#   From:     AGT1
#   Type:     REQ
#   Priority: HIGH
```

### Build Messages Interactively
```bash
drixl build --to AGT2 --from AGT1 --type REQ --priority HIGH --actions ANLY,XTRCT --params input.json,out:json
# ✓ Message built successfully:
# @to:AGT2 @fr:AGT1 @t:REQ @p:HIGH
# ANLY XTRCT [input.json] [out:json]
```

### List All Verbs
```bash
drixl verbs
# DRIXL Standard Verbs (21 total):
#   ANLY     Analyze input data or content
#   XTRCT    Extract specific fields or values
#   ...
```

### Search Verbs
```bash
drixl verbs --search analyze
# Verbs matching 'analyze':
#   ANLY     Analyze input data or content
```

### Benchmark Token Usage
```bash
drixl benchmark
# Token Usage Comparison
# ==================================================
# Format               Tokens    vs DRIXL    Savings
# ------------------------------------------------------
# DRIXL                    25        1.00x          -
# JSON                     60        2.40x        58%
# Natural Language        120        4.80x        79%
```

---

## Benchmarks

Token count comparison across formats:

| Format | Tokens | vs Compact | Use Case |
|---|---|---|---|
| **Compact DRIXL** | ~25 | 1.0x | Production (default) |
| **Structured DRIXL** | ~150 | 6.0x | Development/debugging |
| **JSON** | ~60 | 2.4x | Traditional APIs |
| **Natural Language** | ~120 | 4.8x | Human-readable |
| **XML (verbose)** | ~140 | 5.6x | Enterprise integration |

> Benchmarks measured using OpenAI `tiktoken` on 100+ real agent message samples. Use `drixl benchmark` to test your own messages.

**Recommendation:** Use compact format in production, structured format during development.

---

## Project Structure

```
DRIXL/
├── drixl/
│   ├── __init__.py          # Public API
│   ├── message.py           # Message builder & parser (dual format)
│   ├── structured.py        # Structured XML message classes (NEW)
│   ├── converter.py         # Format conversion utilities (NEW)
│   ├── context_store.py     # Shared context store (memory + Redis)
│   ├── verbs.py             # Standard verb vocabulary
│   ├── exceptions.py        # Custom exceptions
│   └── cli.py               # Command-line interface
├── examples/
│   ├── basic_pipeline.py    # 3-agent pipeline example
│   ├── structured_workflow.py  # Structured format example (NEW)
│   └── format_conversion.py    # Format conversion example (NEW)
├── tests/
│   ├── test_message.py
│   ├── test_structured.py   # Structured format tests (NEW)
│   ├── test_context_store.py
│   ├── test_verbs.py
│   ├── test_cli.py
│   └── ...
├── .github/workflows/
├── CONTRIBUTING.md
├── ROADMAP.md
├── LICENSE
├── pyproject.toml
└── README.md
```

---

## What's New

### v0.3.0 (Current)
- ✨ **Dual format support** — compact (production) and structured (dev/debug)
- 📦 **Artifact support** — attach code, tests, data to messages
- 🔄 **Format conversion** — convert between compact and structured
- 🔍 **Auto-detection** — parse() automatically detects message format
- 📋 **Critique workflow** — structured CRITIQUE messages with ISSUES/SUGGESTIONS/VERDICT
- 🔗 **Thread tracking** — msg_id, thread_id, reply_to for conversation chains

### v0.2.0
- 🛠️ **CLI tool** — parse, build, verbs, benchmark commands
- 📊 **Token benchmarking** — compare DRIXL vs JSON vs Natural Language

### v0.1.1
- 🐛 **Bug fixes** — TTL support in memory backend, lenient parsing
- 🆕 **New verbs** — RETRY, MERGE, SPLIT, AUTH, LOG, WAIT, CACHE
- 🔧 **API enhancements** — reply(), error(), from_dict(), to_dict()

---

## Supporting DRIXL

If DRIXL saves you tokens and costs, consider supporting its development:

- ⭐ **Star the repo** — helps others discover DRIXL
- 💖 **[Sponsor on GitHub](https://github.com/sponsors/SamoTech)** — fund ongoing development
- 🐛 **[Open an issue](https://github.com/SamoTech/DRIXL/issues)** — report bugs or propose new verbs

---

## Contributing

We welcome contributions! Please read our [contributing guidelines](https://github.com/SamoTech/DRIXL/blob/main/CONTRIBUTING.md) before getting started.

> [!NOTE]
> DRIXL is in active development. The verb vocabulary and message formats are open for community input — open an issue to propose new verbs or format extensions.

> [!CAUTION]
> DRIXL is a communication protocol standard. Implementations using DRIXL are responsible for validating inputs and outputs. Never pass unvalidated agent outputs directly to execution functions.

## License

This project is licensed under the MIT License — see [LICENSE](https://github.com/SamoTech/DRIXL/blob/main/LICENSE) for details.

---
<div align="center"><small>Designed & crafted with ❤️ by Ossama Hashim — SamoTech.</small></div><br>
