import json
from typing import List, Dict, Any

SUSPICIOUS_SCRIPT_PATTERNS = [
    "rm ",
    "curl ",
    "wget ",
    "bash ",
    "powershell ",
    "npm install -g",   
    "chown ",
    "chmod ",
    "docker ",
]

def find_issues(code: str) -> List[Dict[str, Any]]:
    """
    Attempt to parse the JSON. Then inspect well‐known sections (e.g. "scripts") to find risky commands.
    Returns a list of findings like:
      { "pattern": "rm ", "context": "rm -rf /", "keyPath": "scripts.start" }
    """
    findings: List[Dict[str, Any]] = []
    try:
        parsed = json.loads(code)
    except Exception:
        
        return findings

   
    scripts = parsed.get("scripts", {})
    if isinstance(scripts, dict):
        for script_name, script_value in scripts.items():
            if not isinstance(script_value, str):
                continue
            for pat in SUSPICIOUS_SCRIPT_PATTERNS:
                if pat in script_value:
                    findings.append({
                        "pattern": pat,
                        "context": f'scripts.{script_name}: {script_value}',
                        "keyPath": f"scripts.{script_name}"
                    })
   
    def _recurse(obj: Any, key_path: str = ""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                _recurse(v, f"{key_path}.{k}" if key_path else k)
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                _recurse(item, f"{key_path}[{idx}]")
        elif isinstance(obj, str):
            for pat in SUSPICIOUS_SCRIPT_PATTERNS:
                if pat in obj:
                    findings.append({
                        "pattern": pat,
                        "context": f"{key_path}: {obj}",
                        "keyPath": key_path
                    })
       

    _recurse(parsed, "")
    return findings
