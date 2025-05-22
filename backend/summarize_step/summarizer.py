# summarizer.py

import asyncio
import json
import os
from typing import List, Dict, Any, Optional

from openai import AsyncOpenAI

# Summarizer module for enriching FRS scanner output with LLM-generated summaries

async def summarize_file(
    client: AsyncOpenAI,
    entry: Dict[str, Any],
    semaphore: asyncio.Semaphore,
    model: str = "gpt-4o",
) -> str:
    """
    Summarize a single file's code in 1-2 sentences.
    """
    filename = entry.get("filename", "<unknown>")
    code = entry.get("code", "")
    prompt = (
        f"Summarize the intention and functionality of the following code file '{filename}' in 1-2 sentences:\n\n{code}"
    )
    async with semaphore:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes code."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
    return response.choices[0].message.content.strip()

async def summarize_project(
    client: AsyncOpenAI,
    entries: List[Dict[str, Any]],
    semaphore: asyncio.Semaphore,
    model: str = "gpt-4o",
) -> str:
    """
    Summarize the overall project context given all files.
    """
    combined_blocks = [f"File: {e['filename']}\n{e.get('code','')}" for e in entries]
    prompt = (
        "Given the following code files, summarize the overall project context and functionality in 2-3 sentences:\n\n"
        + "\n\n".join(combined_blocks)
    )
    async with semaphore:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes codebases."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
    return response.choices[0].message.content.strip()

async def summarize_all(
    entries: List[Dict[str, Any]],
    api_key: Optional[str] = None,
    max_concurrent: int = 5,
    model: str = "gpt-4o",
) -> List[Dict[str, Any]]:
    """
    Enrich each file entry with file_summary and, if multiple files, project_summary.
    """
    key = api_key or os.getenv("OPENAI_API_KEY")
    client = AsyncOpenAI(api_key=key)
    semaphore = asyncio.Semaphore(max_concurrent)

    # Summarize each file in parallel
    file_tasks = [summarize_file(client, e, semaphore, model) for e in entries]
    file_summaries = await asyncio.gather(*file_tasks)

    # Only summarize project if more than one file
    project_summary: Optional[str] = None
    if len(entries) > 1:
        project_summary = await summarize_project(client, entries, semaphore, model)

    # Attach summaries and return
    enriched: List[Dict[str, Any]] = []
    for entry, fs in zip(entries, file_summaries):
        new_entry = entry.copy()
        new_entry["file_summary"] = fs
        if project_summary is not None:
            new_entry["project_summary"] = project_summary
        enriched.append(new_entry)

    return enriched


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Summarize files and project from FRS JSON output using OpenAI GPT-4o"
    )
    parser.add_argument(
        "--input-json", required=True, help="Path to input JSON file"
    )
    parser.add_argument(
        "--output-json", required=False, help="Where to write enriched JSON"
    )
    parser.add_argument(
        "--api-key", required=False, help="OpenAI API key (or set env)"
    )
    parser.add_argument(
        "--concurrency", type=int, default=5, help="Max concurrent API calls"
    )
    parser.add_argument(
        "--model", default="gpt-4o", help="OpenAI model to use"
    )
    args = parser.parse_args()

    with open(args.input_json, "r", encoding="utf-8") as f:
        entries = json.load(f)

    enriched = asyncio.run(
        summarize_all(
            entries,
            api_key=args.api_key,
            max_concurrent=args.concurrency,
            model=args.model,
        )
    )

    output_str = json.dumps(enriched, indent=2)
    if args.output_json:
        with open(args.output_json, "w", encoding="utf-8") as f:
            f.write(output_str)
        print(f"Enriched output written to {args.output_json}")
    else:
        print(output_str)
