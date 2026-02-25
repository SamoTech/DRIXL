"""
DRIXL Network Monitor Example
MikroTik-style network monitoring agent pipeline using DRIXL.

Pipeline: Monitor -> Diagnose -> Action -> Report
"""

from drixl import Message, ContextStore

store = ContextStore()
store.set("ref#1", "Network: MikroTik RouterOS - ether2 interface")
store.set("ref#2", "Action rules: throttle if bandwidth > 90%, block if flagged > 3x")
store.set("ref#3", "Report format: {ip, action, reason, timestamp}")

# Monitor -> Diagnose: High bandwidth alert
alert_msg = Message.build(
    to="DIAGNOSE", fr="MONITOR", msg_type="REQ", priority="HIGH",
    actions=["ANLY"],
    params=["interface:ether2", "usage:95pct", "top_user:192.168.1.45"],
    ctx_ref="ref#1"
)
print("[MONITOR -> DIAGNOSE]")
print(alert_msg)
print()

# Diagnose -> Action: Throttle recommendation
diag_msg = Message.build(
    to="ACTION", fr="DIAGNOSE", msg_type="RES", priority="HIGH",
    actions=["EXEC"],
    params=["throttle", "ip:192.168.1.45", "limit:5M/5M", "confidence:0.92"],
    ctx_ref="ref#2"
)
print("[DIAGNOSE -> ACTION]")
print(diag_msg)
print()

# Action -> Report: Confirm action taken
report_msg = Message.build(
    to="REPORT", fr="ACTION", msg_type="FIN", priority="MED",
    actions=["STOR", "NTFY"],
    params=["action:throttle_applied", "ip:192.168.1.45", "result:success"],
    ctx_ref="ref#3"
)
print("[ACTION -> REPORT]")
print(report_msg)
