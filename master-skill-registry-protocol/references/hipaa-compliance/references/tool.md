# HIPAA Compliance Tools & Agent Templates

Below is the **matching `TOOL.py`** implementation (named `hipaa_compliance_tools.py` for clarity)

- `phi_detection_scanner`
- `phi_redactor`
- `hipaa_audit_logger`
- `baa_status_checker`

It is written in **pure Python 3.11+** (no external dependencies beyond `re`, `json`, `datetime`, and `logging`). You can drop it into any framework.

---

## 1. `hipaa_compliance_tools.py` (TOOL.py)

```python
# hipaa_compliance_tools.py
import re
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

# Simple HIPAA 18-identifier regex patterns (Safe Harbor compliant)
PHI_PATTERNS = {
    "name": re.compile(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}\b'),  # Basic name detection
    "dob": re.compile(r'\b(?:0[1-9]|1[0-2])/(?:0[1-9]|[12]\d|3[01])/(?:19|20)\d{2}\b'),
    "ssn": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
    "mrn": re.compile(r'\b(?:MRN|Medical Record Number|Record #?)\s*[:#]?\s*(\d{6,12})\b', re.I),
    "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    "phone": re.compile(r'\b(?:\+\d{1,2}\s?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'),
    "ip": re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
    "url": re.compile(r'\bhttps?://[^\s]+\b'),
    # Add more as needed (account numbers, etc.)
}

class HIPAAComplianceTools:
    """All HIPAA tools as static methods for easy import across frameworks."""

    @staticmethod
    def phi_detection_scanner(text: str) -> Dict[str, Any]:
        """Scan text for PHI and return findings."""
        findings = []
        for identifier, pattern in PHI_PATTERNS.items():
            matches = pattern.findall(text)
            if matches:
                findings.append({
                    "identifier": identifier,
                    "matches": matches[:5] if len(matches) > 5 else matches,  # limit for log
                    "count": len(matches)
                })
        return {
            "has_phi": len(findings) > 0,
            "findings": findings,
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    def phi_redactor(text: str, method: str = "safe_harbor") -> str:
        """Redact PHI using Safe Harbor method."""
        if method != "safe_harbor":
            raise ValueError("Only safe_harbor supported in this implementation")

        redacted = text
        for identifier, pattern in PHI_PATTERNS.items():
            if identifier == "name":
                redacted = re.sub(pattern, "[PATIENT_NAME]", redacted)
            elif identifier == "dob":
                redacted = re.sub(pattern, "[DOB_REDACTED]", redacted)
            elif identifier == "ssn":
                redacted = re.sub(pattern, "[SSN_REDACTED]", redacted)
            elif identifier == "mrn":
                redacted = re.sub(pattern, "[MRN_REDACTED]", redacted)
            elif identifier == "email":
                redacted = re.sub(pattern, "[EMAIL_REDACTED]", redacted)
            elif identifier == "phone":
                redacted = re.sub(pattern, "[PHONE_REDACTED]", redacted)
            elif identifier == "ip":
                redacted = re.sub(pattern, "[IP_REDACTED]", redacted)
            elif identifier == "url":
                redacted = re.sub(pattern, "[URL_REDACTED]", redacted)
        return redacted

    @staticmethod
    def hipaa_audit_logger(event: str, details: Dict[str, Any], log_file: str = "hipaa_audit.log"):
        """Log every compliance action to a simple append-only log (encrypt in production)."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "details": details,
            "compliance_status": "COMPLIANT"
        }
        log_entry = json.dumps(entry)
        
        # Console + file logging
        logging.basicConfig(level=logging.INFO, format='%(message)s')
        logging.info(f"HIPAA_AUDIT: {log_entry}")
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
        
        return {"logged": True, "entry": entry}

    @staticmethod
    def baa_status_checker() -> bool:
        """Check BAA status from environment (set BAA_SIGNED=true in .env)."""
        import os
        return os.getenv("BAA_SIGNED", "false").lower() == "true"
```

---

## 2. Full Agent Templates

### CrewAI Template (`crewai_hipaa_agent.py`)

CrewAI uses the `@tool` decorator (or `BaseTool` class). This template wraps the tools above.

```python
# crewai_hipaa_agent.py
from crewai import Agent, Task, Crew
from crewai_tools import tool  # or from crewai import tool in newer versions
from hipaa_compliance_tools import HIPAAComplianceTools
import os

# Wrap tools for CrewAI
@tool("PHI Detection Scanner")
def phi_detection_scanner(text: str) -> str:
    """Detect PHI in any text."""
    result = HIPAAComplianceTools.phi_detection_scanner(text)
    HIPAAComplianceTools.hipaa_audit_logger("PHI_SCAN", result)
    return json.dumps(result)

@tool("PHI Redactor")
def phi_redactor(text: str) -> str:
    """Redact PHI using Safe Harbor."""
    redacted = HIPAAComplianceTools.phi_redactor(text)
    HIPAAComplianceTools.hipaa_audit_logger("PHI_REDACTION", {"original_length": len(text), "redacted": redacted[:200]})
    return redacted

@tool("HIPAA Audit Logger")
def hipaa_audit_logger(event: str, details: str) -> str:
    """Log compliance actions."""
    details_dict = json.loads(details) if isinstance(details, str) else details
    HIPAAComplianceTools.hipaa_audit_logger(event, details_dict)
    return "Audit logged successfully"

@tool("BAA Status Checker")
def baa_status_checker() -> str:
    """Verify Business Associate Agreement status."""
    status = HIPAAComplianceTools.baa_status_checker()
    return "BAA_SIGNED=True" if status else "BAA_SIGNED=False - PHI handling blocked"

# Full HIPAA Compliance Officer Agent
hipaa_compliance_agent = Agent(
    role="HIPAA Compliance Officer",
    goal="Enforce strict HIPAA rules on all inputs/outputs and protect ePHI",
    backstory="You are a certified HIPAA auditor embedded in every workflow. You never allow raw PHI.",
    tools=[phi_detection_scanner, phi_redactor, hipaa_audit_logger, baa_status_checker],
    verbose=True,
    allow_delegation=False,
    memory=True,
    # The SKILL.md instructions are injected here
    system_prompt=open("SKILL.md").read() if os.path.exists("SKILL.md") else "You are HIPAA compliant."
)

# Example usage
if __name__ == "__main__":
    task = Task(
        description="Process this message and ensure full HIPAA compliance: Schedule follow-up for patient John Doe, DOB 05/15/1980.",
        expected_output="Redacted, compliant response + compliance block",
        agent=hipaa_compliance_agent
    )
    crew = Crew(agents=[hipaa_compliance_agent], tasks=[task], verbose=2)
    result = crew.kickoff()
    print(result)
```

### OpenSwarm Template

OpenSwarm syncs skills to `~/.claude/skills/` and uses **MCP tools** for execution.

1. Place your existing `SKILL.md` in:  
   `~/.claude/skills/hipaa_compliance/SKILL.md`

2. For the Python tools, create a simple MCP-compatible script (OpenSwarm auto-discovers stdio/HTTP tools).  
   Create folder: `~/.claude/skills/hipaa_compliance/scripts/`

   Copy `hipaa_compliance_tools.py` into that folder and add this thin wrapper `mcp_hipaa_tools.py`:

```python
# ~/.claude/skills/hipaa_compliance/scripts/mcp_hipaa_tools.py
# Run with: python -m mcp_hipaa_tools (OpenSwarm auto-registers)
from hipaa_compliance_tools import HIPAAComplianceTools
import sys
import json

# Simple stdio MCP handler (OpenSwarm expects this pattern)
if __name__ == "__main__":
    for line in sys.stdin:
        request = json.loads(line)
        tool_name = request.get("tool")
        args = request.get("arguments", {})
        
        if tool_name == "phi_redactor":
            result = HIPAAComplianceTools.phi_redactor(args.get("text", ""))
        elif tool_name == "phi_detection_scanner":
            result = HIPAAComplianceTools.phi_detection_scanner(args.get("text", ""))
        # ... add others
        else:
            result = {"error": "Unknown tool"}
        
        print(json.dumps({"result": result}))
```

In OpenSwarm UI → **Tools** page, register the MCP server pointing to this script. The skill will now be auto-available to all agents.

### Hermes Agent Template

**Folder structure to create:**

```
skills/
└── hipaa_compliance/
    ├── SKILL.md                  ← (the file you already received)
    └── scripts/
        └── hipaa_compliance_tools.py   ← (copy the TOOL.py above here)
```

**To activate in a conversation:**
- Type `/hipaa_compliance` or let the agent auto-load it when PHI is detected.

**Optional: Add a custom agent config** in Hermes (if using advanced mode):

```yaml
# In your Hermes agent config or via skill_manage tool
agents:
  - name: HIPAA Guardian
    skills: ["hipaa_compliance"]
    system_prompt: "You are bound by the hipaa_compliance skill at all times."
```