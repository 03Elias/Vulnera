import re
from typing import List, Dict, Any

PATTERNS = [
    "Runtime.getRuntime().exec",
    "ProcessBuilder",
    "ObjectInputStream",
    "eval",
    "ScriptEngine.eval",
    "Class.forName",
    "setAccessible",
    "loadLibrary",
    "System.load",
    "FileOutputStream",
    "FileInputStream",
]

def find_issues(code: str) -> List[Dict[str, Any]]:
    findings = []
    for idx, line in enumerate(code.splitlines(), start=1):
        for pat in PATTERNS:
            if pat in line:
                findings.append({"pattern": pat, "line": idx, "context": line.strip()})
    return findings
