import os
import asyncio
import json
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI

# Final LLM-based danger analysis module

def format_file_payload(entry: Dict[str, Any]) -> str:
    """
    Format the file-specific information into a prompt block.
    """
    parts = [
        f"Filename: {entry.get('filename')}",
        f"Folder: {entry.get('folder', '')}",
        f"Language: {entry.get('language')}",
        f"Static Findings: {entry.get('static_findings')}",
        f"File Summary: {entry.get('file_summary')}",
    ]
    # include project summary only if present
    if entry.get('project_summary'):
        parts.append(f"Project Summary: {entry['project_summary']}")
    parts.append("Code:")
    parts.append(entry.get('code', ''))
    return "\n".join(parts)

async def analyze_file(
    client: AsyncOpenAI,
    entry: Dict[str, Any],
    semaphore: asyncio.Semaphore,
    model: str = "gpt-4o",
) -> Dict[str, Any]:
    """
    Analyze a single file for actual danger using LLM.
    Adds 'danger' and 'reason'.
    """
    payload = format_file_payload(entry)
    prompt = (
        "You are a security expert reviewing source code. "
        "For the following file, determine if it poses a real security danger based on its code, static findings, and summaries. "
        "Respond with a JSON object containing 'danger' ('yes' or 'no') and 'reason' (a brief explanation, max 3 sentences)."  
        f"\n\n{payload}"
    )
    async with semaphore:
        resp = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a security analyst."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
    content = resp.choices[0].message.content.strip()

    
    if content.startswith("```"):
        
        lines = content.splitlines()
        
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        content = "\n".join(lines)

    
    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        
        return {"danger": "unknown", "reason": content}

    
    danger = result.get('danger', '').lower()
    reason = result.get('reason', '')
    return {"danger": danger, "reason": reason}

async def analyze_overall(
    client: AsyncOpenAI,
    entries: List[Dict[str, Any]],
    semaphore: asyncio.Semaphore,
    model: str = "gpt-4o",
) -> Dict[str, Any]:
    """
    Analyze the overall project danger.
    Returns JSON with 'overall_danger' and 'overall_reason'.
    """
    blocks = [format_file_payload(e) for e in entries]
    prompt = (
        "You are a security expert reviewing multiple code files. "
        "Based on the combined static findings and summaries, judge if the project as a whole poses a security danger. "
        "Respond with a JSON object containing 'overall_danger' ('yes' or 'no') and 'overall_reason' (a brief explanation, max 3 sentences)."  
        f"\n\n{'\n\n'.join(blocks)}"
    )
    async with semaphore:
        resp = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a security analyst."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
    content = resp.choices[0].message.content.strip()

    
    if content.startswith("```"):
        lines = content.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        content = "\n".join(lines)

    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        return {"overall_danger": "unknown", "overall_reason": content}

    return {
        "overall_danger": result.get('overall_danger', '').lower(),
        "overall_reason": result.get('overall_reason', '')
    }

async def analyze_all(
    entries: List[Dict[str, Any]],
    api_key: Optional[str] = None,
    max_concurrent: int = 5,
    model: str = "gpt-4o",
) -> List[Dict[str, Any]]:
    """
    Perform per-file and overall danger analysis.
    """
    key = api_key or os.getenv("OPENAI_API_KEY")
    client = AsyncOpenAI(api_key=key)
    semaphore = asyncio.Semaphore(max_concurrent)

    
    tasks = [analyze_file(client, e, semaphore, model) for e in entries]
    file_results = await asyncio.gather(*tasks)

    enriched = []
    for entry, fres in zip(entries, file_results):
        new_entry = entry.copy()
        new_entry.update(fres)
        enriched.append(new_entry)

    
    if len(entries) > 1:
        overall = await analyze_overall(client, entries, semaphore, model)
        enriched.append({"overall_analysis": overall})

    return enriched
