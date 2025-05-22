import re
from typing import List, Dict, Any

PATTERNS = [
    "std::process::Command",
    "std::fs::read_to_string",
    "std::fs::write",
    "std::mem::transmute",
    "unsafe",
    "extern crate libc",
    "libloading::Library",
    "std::net::TcpStream",
]

def find_issues(code: str) -> List[Dict[str, Any]]:
    findings = []
    for idx, line in enumerate(code.splitlines(), start=1):
        for pat in PATTERNS:
            if pat in line:
                findings.append({"pattern": pat, "line": idx, "context": line.strip()})
    return findings
