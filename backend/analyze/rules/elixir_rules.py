import re
from typing import List, Dict, Any

PATTERNS = [
    "System.cmd",
    "Code.eval_string",
    "Code.eval_file",
    "File.read!",
    "File.write!",
    "Port.open",
    "eval",
    "apply",
    "spawn",
    "send",
    "IO.puts",
    "IO.gets",
]

def find_issues(code: str) -> List[Dict[str, Any]]:
    findings = []
    for idx, line in enumerate(code.splitlines(), start=1):
        for pat in PATTERNS:
            if pat in line:
                findings.append({"pattern": pat, "line": idx, "context": line.strip()})
    return findings
