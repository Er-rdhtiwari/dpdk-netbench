# Security Policy

## Overview

NetBench Copilot is designed with security and safety as core principles. This document outlines the security policies and practices implemented in the system.

## Human-in-the-Loop for System Changes

### BIOS Changes and Reboots

**Policy**: NetBench Copilot will NEVER automatically execute BIOS changes or system reboots.

**Implementation**:
1. Any tuning profile that includes BIOS changes or reboot recommendations is marked with `requires_approval: true`
2. The workflow checks for the presence of `NETBENCH_APPROVAL_TOKEN` in the environment
3. If the token is not present, the workflow stops and returns the manual steps to the user
4. The user must explicitly set the approval token to proceed

**Example**:
```yaml
# tuning_profile.yaml
requires_approval: true
approval_reason: "BIOS changes required: Enable IOMMU, disable C-states"

manual_steps:
  - "Enter BIOS setup"
  - "Navigate to Advanced > CPU Configuration"
  - "Enable IOMMU"
  - "Disable C-states (C1E, C6)"
  - "Save and reboot"
```

**To approve**:
```bash
export NETBENCH_APPROVAL_TOKEN="your-secret-token"
```

### Disruptive System Operations

The following operations require manual approval:
- BIOS configuration changes
- System reboots
- Kernel parameter changes requiring reboot
- Firmware updates
- Network interface resets

## Data Redaction

### Sensitive Information

NetBench Copilot automatically redacts sensitive information when exporting datasets:

**Redacted Data Types**:
1. **Hostnames**: Replaced with `HOST_<hash>`
2. **IP Addresses**: Replaced with `IP_<hash>`
3. **PCI Bus/Device/Function (BDF)**: Replaced with `PCI_<hash>`
4. **MAC Addresses**: Replaced with `MAC_<hash>`

**Implementation**:
```python
# Example redaction
original: "Running on server01.example.com (192.168.1.100)"
redacted: "Running on HOST_a1b2c3 (IP_d4e5f6)"

original: "NIC at 0000:3b:00.0"
redacted: "NIC at PCI_g7h8i9"
```

### Dataset Export

When exporting datasets for training:
- Redaction is enabled by default (`redact=True`)
- Redaction can be disabled only for internal use with explicit flag
- All exported datasets include a `redacted: true` flag in metadata

## API Key Management

### OpenAI API Key

**Storage**:
- API keys are stored in `.env` file (not committed to git)
- `.env` is listed in `.gitignore`
- `.env.example` provides template without actual keys

**Usage**:
- Keys are loaded via `pydantic-settings` from environment
- Keys are never logged or included in artifacts
- Keys are never sent to MCP tools or stored in database

**Best Practices**:
1. Use separate API keys for development and production
2. Rotate keys regularly
3. Use API key restrictions (IP allowlists, rate limits)
4. Monitor API usage for anomalies

## Audit Logging

### What is Logged

All tool executions are logged to SQLite with:
- Timestamp
- Tool name
- Request parameters (redacted)
- Response summary
- User identifier (if available)
- Success/failure status

### Log Retention

- Logs are stored in SQLite database
- Retention period: configurable (default: 90 days)
- Logs can be exported for external audit systems

### Log Access

- Logs are accessible only to authorized users
- Log queries are themselves logged
- Sensitive data in logs is redacted

## Tool Execution Safety

### MCP Tool Boundary

**Purpose**: Enforce deterministic, validated tool execution

**Safety Measures**:
1. **Schema Validation**: All tool requests/responses validated with Pydantic
2. **No Shell Injection**: Commands are constructed programmatically, not via string interpolation
3. **Path Validation**: File paths are validated and restricted to workspace
4. **Resource Limits**: Tool execution has timeouts and resource limits

### Command Generation

**Policy**: Commands are generated via deterministic tools, not free-form LLM output

**Implementation**:
1. LLM generates structured plan (YAML)
2. MCP `render_command` tool converts plan to commands
3. Commands are validated against benchmark-specific templates
4. No arbitrary shell commands are executed

**Example**:
```python
# SAFE: Deterministic command generation
def render_command(run_yaml: Dict, scenario: str) -> str:
    template = BENCHMARK_TEMPLATES[benchmark]
    return template.format(**run_yaml[scenario])

# UNSAFE: Free-form LLM command generation (NOT USED)
# llm.generate("Create a command to run testpmd")
```

## Grounding Enforcement

### Factual Claims

**Policy**: All factual claims about tuning, benchmarks, and parameters MUST be grounded in KB

**Implementation**:
1. Citations are required for all tuning recommendations
2. If information is not found in KB, output exactly: "NOT FOUND IN KB"
3. Grounding is validated in evaluation harness
4. Grounding ratio is tracked and reported

### Citation Tracking

Every response includes:
- Source file name
- Page numbers
- Document and chunk IDs
- Similarity scores
- Text snippets

## Network Security

### API Endpoints

**OpenAI API**:
- Uses HTTPS for all requests
- API key sent in Authorization header
- Requests are rate-limited
- Responses are validated

**MCP Server** (if deployed remotely):
- Use TLS for all connections
- Implement authentication (API keys or OAuth)
- Rate limiting per client
- Request size limits

## Vulnerability Reporting

### Reporting Process

If you discover a security vulnerability:

1. **DO NOT** open a public GitHub issue
2. Email: security@netbench.example.com
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

### Response Timeline

- **24 hours**: Initial acknowledgment
- **7 days**: Preliminary assessment
- **30 days**: Fix or mitigation plan
- **90 days**: Public disclosure (coordinated)

## Security Best Practices

### For Users

1. **API Keys**: Never commit API keys to version control
2. **PDFs**: Review PDFs before adding to KB (may contain sensitive info)
3. **Logs**: Sanitize logs before sharing externally
4. **Approval Token**: Keep approval token secret and rotate regularly
5. **Updates**: Keep dependencies updated for security patches

### For Developers

1. **Input Validation**: Validate all user inputs
2. **Output Sanitization**: Sanitize all outputs (especially commands)
3. **Least Privilege**: Run with minimum required permissions
4. **Dependency Scanning**: Regularly scan dependencies for vulnerabilities
5. **Code Review**: All changes require security review

## Compliance

### Data Privacy

- No personal data is collected by default
- User queries and responses are stored locally (SQLite)
- Dataset export includes redaction of sensitive information
- Users control all data storage and retention

### Regulatory Considerations

- **GDPR**: Users control their data; no data sent to third parties (except OpenAI API)
- **SOC 2**: Audit logging and access controls implemented
- **ISO 27001**: Security policies and procedures documented

## Security Updates

This security policy is reviewed and updated:
- Quarterly (scheduled review)
- After security incidents
- When new features are added
- Based on user feedback

Last updated: 2024-01-24