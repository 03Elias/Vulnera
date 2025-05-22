import re
from typing import List, Dict, Any

PATTERNS = [
    "exec.Command",
    "os/exec",
    "ioutil.ReadFile",
    "ioutil.WriteFile",
    "net/http",
    "http.Get",
    "http.Post",
    "reflect.Value.Call",
    "unsafe.Pointer",
    "runtime.SetFinalizer",
]

def find_issues(code: str) -> List[Dict[str, Any]]:
    findings = []
    for idx, line in enumerate(code.splitlines(), start=1):
        for pat in PATTERNS:
            if pat in line:
                findings.append({"pattern": pat, "line": idx, "context": line.strip()})
    return findings
