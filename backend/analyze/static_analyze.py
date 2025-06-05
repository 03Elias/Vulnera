import importlib
from typing import List, Dict, Any


LANGUAGE_MODULE_MAP = {
    "Python": "analyze.rules.py_rules",
    "JavaScript": "analyze.rules.js_rules",
    "TypeScript": "analyze.rules.js_rules",
    "Java": "analyze.rules.java_rules",
    "C": "analyze.rules.c_rules",
    "C++": "analyze.rules.cpp_rules",
    "C#": "analyze.rules.c_sharp_rules",
    "Go": "analyze.rules.go_rules",
    "Rust": "analyze.rules.rust_rules",
    "HTML": "analyze.rules.html_rules",
    "CSS": "analyze.rules.css_rules",
    "SQL": "analyze.rules.sql_rules",
    "Elixir": "analyze.rules.elixir_rules",
    "JSON": "analyze.rules.json_rules",
    "Node": "analyze.rules.node_rules"
}


def static_analyze_entries(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enrich each entry with a 'static_findings' list based on language rules.
    """
    for entry in entries:
        lang = entry.get("language")
        module_path = LANGUAGE_MODULE_MAP.get(lang)
        if not module_path:
            entry["static_findings"] = []
            continue

        module = importlib.import_module(module_path)
        findings = module.find_issues(entry.get("code", ""))
        entry["static_findings"] = findings
    return entries
