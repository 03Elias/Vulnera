import re
from typing import List, Dict, Any

PATTERNS = [
    "System.Diagnostics.Process",
    "Process.Start",
    "Assembly.Load",
    "Assembly.LoadFrom",
    "File.ReadAllText",
    "File.WriteAllText",
    "WebClient.DownloadString",
    "HttpWebRequest",
    "Eval",
    "ExecuteScalar",
    "ExecuteReader",
]

def find_issues(code: str) -> List[Dict[str, Any]]:
    findings = []
    for idx, line in enumerate(code.splitlines(), start=1):
        for pat in PATTERNS:
            if pat in line:
                findings.append({"pattern": pat, "line": idx, "context": line.strip()})
    return findings
