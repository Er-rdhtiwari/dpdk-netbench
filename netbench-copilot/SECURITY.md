# Security

## Human-in-the-loop for BIOS changes

BIOS changes and reboot steps are never executed automatically. Any tuning profile that includes BIOS or reboot
recommendations is marked `requires_approval: true` and the workflow halts unless `NETBENCH_APPROVAL_TOKEN` is set.

## Redaction

Dataset export removes hostnames, IP addresses, and PCI BDF identifiers using deterministic regex redaction.

## Audit Logging

All artifacts are written to `out/` and can be stored alongside the SQLite run store for auditability.

## Safe Tool Policies

Commands are generated only through deterministic MCP tools with schema validation. If KB grounding fails, the system
returns `NOT FOUND IN KB` and does not emit commands.
