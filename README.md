# 🔐 Secure File Upload API

A secure REST API built with **Python and FastAPI** for validating and storing file uploads safely.

## 🚀 Features

- Secure file upload using FastAPI
- File extension validation
- MIME type validation
- File signature verification
- Maximum file size restriction of 5 MB
- Executable file blocking
- UUID-based secure filenames
- Dedicated upload storage
- Error handling and validation

## 🛡️ Allowed File Types

- `.jpg`
- `.jpeg`
- `.png`
- `.pdf`
- `.txt`

## 🔒 Security Measures

1. **Extension Validation**  
   Only approved file extensions are accepted.

2. **MIME Type Validation**  
   The uploaded content type is checked against allowed MIME types.

3. **File Signature Validation**  
   PDF, PNG and JPEG files are checked against their expected file signatures.

4. **Executable File Blocking**  
   Executable and script extensions such as `.exe`, `.bat`, `.cmd`, `.ps1`, `.js` and `.sh` are blocked.

5. **File Size Restriction**  
   Uploads are limited to **5 MB**.

6. **Secure File Names**  
   Uploaded files are stored using randomly generated UUID filenames instead of the original filename.

7. **Dedicated Storage**  
   Uploaded files are stored inside a controlled `uploads` directory.

## 🛠️ Technologies

- Python
- FastAPI
- Uvicorn
- python-multipart
- Git
- GitHub

## 📌 API Endpoint

### Upload File

```text
POST /upload

Example using curl:

curl -X POST "http://127.0.0.1:8000/upload" -F "file=@test.txt"
▶️ Run the Project

Activate the virtual environment:

.\venv\Scripts\Activate.ps1

Start the FastAPI server:

python -m uvicorn app.main:app --reload

API:

http://127.0.0.1:8000

Swagger documentation:

http://127.0.0.1:8000/docs
🧪 Testing
Test	Result
Valid .txt upload	✅ Passed
.exe upload	❌ Rejected
.zip upload	❌ Rejected
Empty file	❌ Rejected
Oversized file	❌ Rejected
Invalid file signature	❌ Rejected
📁 Project Structure
task31-secure-file-upload-api/
│
├── app/
│   ├── __init__.py
│   └── main.py
│
├── uploads/
│   └── .gitkeep
│
├── tests/
│   └── test_upload.py
│
├── .gitignore
├── README.md
└── requirements.txt
🎓 VEDA Technology

This project was developed as part of the VEDA Technology Level 2 Internship – Task 31.

👩‍💻 Author

Mahima M.