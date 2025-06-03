

import re
from typing import List, Dict, Any


NODE_SUSPICIOUS_PATTERNS = [
    r"child_process\.exec",      
    r"child_process\.spawn",     
    r"require\s*\(\s*['\"]child_process['\"]\s*\)", 
    r"require\s*\(\s*['\"]fs['\"]\s*\)",             
    r"process\.env",             
    r"eval\s*\(",               
    r"Buffer\.from\s*\(",        
    r"setTimeout\s*\(",          
    r"setInterval\s*\(",
    r"new Buffer",               
    r"dlopen",                   
    r"require\s*\(\s*['\"].+\.so['\"]\s*\)",  
]

def find_issues(code: str) -> List[Dict[str, Any]]:
    """
    Treat the .node file as text, and run a bunch of regex checks for
    suspicious Node‐style calls or references to child_process, fs, eval, etc.
    Return a list of { pattern, line, context } findings.
    """
    findings: List[Dict[str, Any]] = []
    lines = code.splitlines()
    for idx, line in enumerate(lines, start=1):
        for pat in NODE_SUSPICIOUS_PATTERNS:
            if re.search(pat, line):
                findings.append({
                    "pattern": pat,
                    "line": idx,
                    "context": line.strip()
                })
    return findings
