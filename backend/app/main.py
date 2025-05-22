# app/main.py

from fastapi import FastAPI, HTTPException, UploadFile, File
from dotenv import load_dotenv
from pathlib import Path
import shutil

from frs_scanner.file_recursive_scanner import scan_upload

load_dotenv()
app = FastAPI(title="FRS Scanner API",
    description="API to recursively scan source code files for malicious patterns"
)

@app.post("/scan-upload/", summary="Upload a file or zip of a folder")
async def scan_upload_endpoint(file: UploadFile = File(...)):
    """
    Upload a single source file or ZIP archive of a folder to scan.
    - **file**: uploaded source file or ZIP of multiple files.
    """
    # Prepare temp dir
    temp_dir = Path("./temp_uploads")
    temp_dir.mkdir(exist_ok=True)
    temp_path = temp_dir / file.filename

    # Save upload
    with temp_path.open("wb") as buf:
        shutil.copyfileobj(file.file, buf)

    try:
        results = scan_upload(temp_path, temp_dir)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {e}")
    finally:
        # Cleanup: remove file and any extracted folder
        if temp_path.exists():
            temp_path.unlink()
        # Remove any extracted dirs
        for child in temp_dir.iterdir():
            if child.is_dir() and child.name.startswith(temp_path.stem):
                shutil.rmtree(child)
