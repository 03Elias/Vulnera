import re
from typing import List, Dict, Any

PATTERNS = [
    "eval",
    "Function",
    "setTimeout",
    "setInterval",
    "document.write",
    "innerHTML",
    "outerHTML",
    "localStorage",
    "sessionStorage",
    "fetch",
    "XMLHttpRequest",
    "WebSocket",
    "document.addEventListener('keydown'",
    "navigator.sendBeacon",
    "atob",
    "btoa",
]

def find_issues(code: str) -> List[Dict[str, Any]]:
    findings = []
    for idx, line in enumerate(code.splitlines(), start=1):
        for pat in PATTERNS:
            if pat in line:
                findings.append({
                    "pattern": pat,
                    "line": idx,
                    "context": line.strip()
                })
    return findings