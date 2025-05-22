import re
from typing import List, Dict, Any

PATTERNS = [
    "os.system",
    "subprocess.Popen",
    "eval",
    "exec",
    "pickle.loads",
    "input",
    "__import__",
    "open",
    "yaml.load",
    "shlex.split",
    "base64.b64decode",
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