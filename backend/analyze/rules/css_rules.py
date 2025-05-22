import re
from typing import List, Dict, Any

# Revised CSS patterns using regex to capture variations like url("javascript:")
PATTERNS = [
    r"expression\(",
    r"url\(\s*['\"]?javascript:",
    r"behavior:",
    r"-moz-binding",
]

def find_issues(code: str) -> List[Dict[str, Any]]:
    """
    Scan CSS code for potentially dangerous patterns, case-insensitive.
    """
    findings: List[Dict[str, Any]] = []
    for idx, line in enumerate(code.splitlines(), start=1):
        for pat in PATTERNS:
            if re.search(pat, line, re.IGNORECASE):
                findings.append({
                    "pattern": pat,
                    "line": idx,
                    "context": line.strip()
                })
    return findings
