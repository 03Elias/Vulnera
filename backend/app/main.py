# app/main.py

from fastapi import FastAPI, HTTPException, UploadFile, File
from dotenv import load_dotenv
from pathlib import Path
import shutil
import asyncio
from fastapi.middleware.cors import CORSMiddleware

from frs_scanner.scanner import scan_upload
from analyze.static_analyze import static_analyze_entries
from summarize_step.summarizer import summarize_all
from analyze.llm_analyze import analyze_all

load_dotenv()

app = FastAPI(
    title="FRS Scanner Suite API",
    description="Upload code (or a ZIP) to scan for source files, perform static analysis, generate summaries, or full danger analysis",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # your React dev server
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.get("/", summary="API Root")
async def root():
    return {"message": "Welcome to the FRS Scanner Suite API"}

@app.post(
    "/scan-upload/",
    summary="Scan for source files",
    response_model=list,
)
async def scan_upload_endpoint(file: UploadFile = File(...)):
    temp_dir = Path("./temp_uploads"); temp_dir.mkdir(exist_ok=True)
    temp_path = temp_dir / file.filename
    with temp_path.open("wb") as buf:
        shutil.copyfileobj(file.file, buf)
    try:
        entries = scan_upload(temp_path, temp_dir)
        return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {e}")
    finally:
        if temp_path.exists(): temp_path.unlink()
        for child in temp_dir.iterdir():
            if child.is_dir() and child.name.startswith(temp_path.stem): shutil.rmtree(child)

@app.post(
    "/static-analyze-upload/",
    summary="Static analysis of source files",
    response_model=list,
)
async def static_analyze_upload_endpoint(file: UploadFile = File(...)):
    temp_dir = Path("./temp_uploads"); temp_dir.mkdir(exist_ok=True)
    temp_path = temp_dir / file.filename
    with temp_path.open("wb") as buf:
        shutil.copyfileobj(file.file, buf)
    try:
        entries = scan_upload(temp_path, temp_dir)
        analyzed = static_analyze_entries(entries)
        return analyzed
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Static analysis failed: {e}")
    finally:
        if temp_path.exists(): temp_path.unlink()
        for child in temp_dir.iterdir():
            if child.is_dir() and child.name.startswith(temp_path.stem): shutil.rmtree(child)

@app.post(
    "/summarize-upload/",
    summary="LLM-based summarization of code",
    response_model=list,
)
async def summarize_upload_endpoint(
    file: UploadFile = File(...),
    concurrency: int = 5,
    model: str = "gpt-4o",
):
    temp_dir = Path("./temp_uploads"); temp_dir.mkdir(exist_ok=True)
    temp_path = temp_dir / file.filename
    with temp_path.open("wb") as buf:
        shutil.copyfileobj(file.file, buf)
    try:
        entries = scan_upload(temp_path, temp_dir)
        enriched = await summarize_all(
            entries,
            max_concurrent=concurrency,
            model=model,
        )
        return enriched
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {e}")
    finally:
        if temp_path.exists(): temp_path.unlink()
        for child in temp_dir.iterdir():
            if child.is_dir() and child.name.startswith(temp_path.stem): shutil.rmtree(child)

@app.post(
    "/analyze-upload/",
    summary="Full LLM-based danger analysis of source files",
    response_model=list,
)
async def analyze_upload_endpoint(
    file: UploadFile = File(...),
    concurrency: int = 5,
    model: str = "gpt-4o",
):
    temp_dir = Path("./temp_uploads"); temp_dir.mkdir(exist_ok=True)
    temp_path = temp_dir / file.filename
    with temp_path.open("wb") as buf:
        shutil.copyfileobj(file.file, buf)
    try:
        # 1) scan
        entries = scan_upload(temp_path, temp_dir)
        # 2) static analysis
        entries = static_analyze_entries(entries)
        # 3) summarization (adds file_summary and project_summary)
        entries = await summarize_all(
            entries,
            max_concurrent=concurrency,
            model=model,
        )
        # 4) LLM danger analysis
        results = await analyze_all(
            entries,
            max_concurrent=concurrency,
            model=model,
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk analysis failed: {e}")
    finally:
        if temp_path.exists(): temp_path.unlink()
        for child in temp_dir.iterdir():
            if child.is_dir() and child.name.startswith(temp_path.stem): shutil.rmtree(child)
