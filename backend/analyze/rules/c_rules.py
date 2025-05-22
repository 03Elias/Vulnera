import re
from typing import List, Dict, Any

PATTERNS = [
    "system",
    "popen",
    "exec",
    "execl",
    "execvp",
    "fopen",
    "fscanf",
    "gets",
    "scanf",
    "strcpy",
    "strcat",
    "sprintf",
    "printf",
    "fork",
    "dlopen",
]

def find_issues(code: str) -> List[Dict[str, Any]]:
    findings = []
    for idx, line in enumerate(code.splitlines(), start=1):
        for pat in PATTERNS:
            if re.search(r"\b" + re.escape(pat) + r"\b", line):
                findings.append({"pattern": pat, "line": idx, "context": line.strip()})
    return findings
