import re
from typing import List, Dict, Any

PATTERNS = [
    "DROP",
    "DELETE",
    "INSERT",
    "UPDATE",
    "SELECT",
    "--",
    ";--",
    "' OR '1'='1",
    "\" OR \"1\"=\"1\"",
    "xp_cmdshell",
    "UNION SELECT",
    "INFORMATION_SCHEMA",
    "LOAD_FILE",
    "OUTFILE",
]

def find_issues(code: str) -> List[Dict[str, Any]]:
    findings = []
    for idx, line in enumerate(code.splitlines(), start=1):
        for pat in PATTERNS:
            if pat in line:
                findings.append({"pattern": pat, "line": idx, "context": line.strip()})
    return findings