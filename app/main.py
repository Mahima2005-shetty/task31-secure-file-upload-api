from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile


app = FastAPI(
    title="Secure File Upload API",
    description="A secure API for validating and storing file uploads.",
    version="1.0.0",
)


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".pdf",
    ".txt",
}

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "application/pdf",
    "text/plain",
}

BLOCKED_EXTENSIONS = {
    ".exe",
    ".bat",
    ".cmd",
    ".com",
    ".msi",
    ".scr",
    ".sh",
    ".ps1",
    ".vbs",
    ".js",
}

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def get_safe_extension(filename: str) -> str:
    """
    Extract only the file extension from the client filename.
    """
    return Path(filename).suffix.lower()


def validate_file_signature(file_bytes: bytes, extension: str) -> bool:
    """
    Perform a basic file-signature check for binary file types.
    """

    if extension == ".pdf":
        return file_bytes.startswith(b"%PDF")

    if extension == ".png":
        return file_bytes.startswith(b"\x89PNG\r\n\x1a\n")

    if extension in {".jpg", ".jpeg"}:
        return file_bytes.startswith(b"\xff\xd8\xff")

    # Plain text does not have a fixed binary signature.
    if extension == ".txt":
        return True

    return False


# --------------------------------------------------
# API endpoints
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Secure File Upload API is running",
        "docs": "/docs",
    }


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Securely upload a file after validating:
    - filename
    - extension
    - MIME type
    - file signature
    - file size
    """

    # ----------------------------------------------
    # 1. Check filename
    # ----------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    original_filename = Path(file.filename).name
    extension = get_safe_extension(original_filename)

    # ----------------------------------------------
    # 2. Block executable file types
    # ----------------------------------------------

    if extension in BLOCKED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Executable files are not allowed.",
        )

    # ----------------------------------------------
    # 3. Check allowed extension
    # ----------------------------------------------

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{extension}' is not allowed.",
        )

    # ----------------------------------------------
    # 4. Check MIME type
    # ----------------------------------------------

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Content type '{file.content_type}' is not allowed.",
        )

    # ----------------------------------------------
    # 5. Read first bytes for signature validation
    # ----------------------------------------------

    first_bytes = await file.read(16)

    if not first_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    if not validate_file_signature(first_bytes, extension):
        raise HTTPException(
            status_code=400,
            detail="File content does not match the declared file type.",
        )

    # ----------------------------------------------
    # 6. Generate a safe server-side filename
    # ----------------------------------------------

    safe_filename = f"{uuid4().hex}{extension}"
    destination = UPLOAD_DIR / safe_filename

    # ----------------------------------------------
    # 7. Save file while enforcing size limit
    # ----------------------------------------------

    total_size = len(first_bytes)

    try:
        with destination.open("wb") as output_file:
            output_file.write(first_bytes)

            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:
                    destination.unlink(missing_ok=True)

                    raise HTTPException(
                        status_code=413,
                        detail="File size exceeds the 5 MB limit.",
                    )

                output_file.write(chunk)

    except HTTPException:
        raise

    except Exception:
        destination.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail="An error occurred while saving the file.",
        )

    finally:
        await file.close()

    # ----------------------------------------------
    # 8. Return successful response
    # ----------------------------------------------

    return {
        "message": "File uploaded successfully.",
        "original_filename": original_filename,
        "stored_filename": safe_filename,
        "file_size": total_size,
        "content_type": file.content_type,
    }