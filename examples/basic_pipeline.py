"""
DRIXL Basic Example - 3 Agent Pipeline
Demonstrates building and parsing DRIXL messages across a simple pipeline.
"""

from drixl import Message, ContextStore

# Setup shared context store
store = ContextStore()
store.set("ref#1", "Project: Firewall threat detection pipeline")
store.set("ref#2", "Output: JSON array [{ip, count, risk_level, last_seen}]")
store.set("ref#3", "Constraint: Only flag IPs with count > 50 and confidence > 0.85")

# Agent 1 -> Agent 2: Analyze firewall logs
msg_1 = Message.build(
    to="AGT2", fr="AGT1", msg_type="REQ", priority="HIGH",
    actions=["ANLY", "XTRCT"],
    params=["firewall.log", "denied_ips", "out:json"],
    ctx_ref="ref#1"
)
print("[AGT1 -> AGT2]")
print(msg_1)
print()

# Agent 2 -> Agent 3: Validate and route
msg_2 = Message.build(
    to="AGT3", fr="AGT2", msg_type="RES", priority="HIGH",
    actions=["VALD", "ROUT"],
    params=["findings:14_ips", "schema:threat_schema", "AGT3"],
    ctx_ref="ref#2"
)
print("[AGT2 -> AGT3]")
print(msg_2)
print()

# Agent 3 -> Orchestrator: Store and finalize
msg_3 = Message.build(
    to="ORCH", fr="AGT3", msg_type="FIN", priority="MED",
    actions=["STOR"],
    params=["key:threat_report", "val:14_blocked_ips"]
)
print("[AGT3 -> ORCH]")
print(msg_3)
print()

# Parse incoming message
parsed = Message.parse(msg_1)
print("Parsed msg_1:", parsed)
