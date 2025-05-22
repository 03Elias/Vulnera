# app/main.py

from fastapi import FastAPI, HTTPException, UploadFile, File
from dotenv import load_dotenv
from pathlib import Path
import shutil
import asyncio

from frs_scanner.scanner import scan_upload
from summarize_step.summarizer import summarize_all   # your summarizer.py module

load_dotenv()

app = FastAPI(
    title="FRS Scanner & Summarizer API",
    description="Upload code (or a zip) to scan for source files and/or generate summaries via GPT-4o",
)


@app.get("/", summary="API Root")
async def root():
    return {"message": "Welcome to the FRS Scanner & Summarizer API"}


@app.post(
    "/scan-upload/",
    summary="Upload a file or ZIP to scan for source files",
    response_model=list,
)
async def scan_upload_endpoint(file: UploadFile = File(...)):
    """
    Upload a single source file or a ZIP archive of a folder to scan.
    Returns a list of { filename, folder, language, code } objects.
    """
    temp_dir = Path("./temp_uploads")
    temp_dir.mkdir(exist_ok=True)
    temp_path = temp_dir / file.filename

    # save upload
    with temp_path.open("wb") as buf:
        shutil.copyfileobj(file.file, buf)

    try:
        results = scan_upload(temp_path, temp_dir)
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {e}")

    finally:
        # cleanup
        if temp_path.exists():
            temp_path.unlink()
        for child in temp_dir.iterdir():
            if child.is_dir() and child.name.startswith(temp_path.stem):
                shutil.rmtree(child)


@app.post(
    "/summarize-upload/",
    summary="Upload code (or ZIP) and get file + project summaries",
    response_model=list,
)
async def summarize_upload_endpoint(
    file: UploadFile = File(...),
    concurrency: int = 5,
    model: str = "gpt-4o",
):
    """
    Upload a single source file or a ZIP archive of a folder.
    - Scans for source files.
    - Summarizes each file (1–2 sentences) and the overall project (2–3 sentences).
    """
    temp_dir = Path("./temp_uploads")
    temp_dir.mkdir(exist_ok=True)
    temp_path = temp_dir / file.filename

    # save upload
    with temp_path.open("wb") as buf:
        shutil.copyfileobj(file.file, buf)

    try:
        # 1) scan for files
        entries = scan_upload(temp_path, temp_dir)

        # 2) run the summarizer (uses OPENAI_API_KEY from env)
        enriched = await summarize_all(
            entries,
            max_concurrent=concurrency,
            model=model,
        )

        return enriched

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {e}")

    finally:
        # cleanup
        if temp_path.exists():
            temp_path.unlink()
        for child in temp_dir.iterdir():
            if child.is_dir() and child.name.startswith(temp_path.stem):
                shutil.rmtree(child)
