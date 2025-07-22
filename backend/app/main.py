# backend/app/main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import boto3
from botocore.client import Config
from pathlib import Path
import tempfile, uuid, os
from dotenv import load_dotenv

# ← thin wrapper that simply calls your original milestone5.py and
#    returns the Path of the processed .mp4
from run_m5 import run as run_milestone5     

# ──────────────────── 1.  ENV & S3 CLIENT ────────────────────
load_dotenv()                                                # .env in same folder

AWS_ACCESS_KEY_ID     = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET         = os.getenv("AWS_S3_BUCKET")           # e.g. speaksync-storage
AWS_REGION            = os.getenv("AWS_REGION", "us-east-2") # default

s3 = boto3.client(
    "s3",
    aws_access_key_id    = AWS_ACCESS_KEY_ID,
    aws_secret_access_key= AWS_SECRET_ACCESS_KEY,
    region_name          = AWS_REGION,
    config               = Config(signature_version="s3v4")
)

# ──────────────────── 2.  FAST‑API APP ───────────────────────
app = FastAPI()

# CORS so React (localhost:3000) can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["http://localhost:3000"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

@app.get("/")
def health():
    """Simple ping‑pong health‑check."""
    return {"status": "ok"}

# ──────────────────── 3.  MAIN ENDPOINT  ─────────────────────
@app.post("/process/")
async def process(file: UploadFile = File(...)):
    """
    1. Save the uploaded MP4 to a temp file
    2. Run the milestone5 pipeline (French audio + subtitles)
    3. Upload the processed video to S3
    4. Return a 1‑hour presigned download URL
    """
    try:
        # 1️⃣  save upload
        tmp_root = Path(tempfile.gettempdir())
        tmp_mp4  = tmp_root / f"{uuid.uuid4().hex}_{file.filename}"
        tmp_mp4.write_bytes(await file.read())

        # 2️⃣  milestone5 processing (returns Path to final mp4)
        final_mp4 = run_milestone5(tmp_mp4)

        # 3️⃣  upload to S3
        s3_key = f"translated/{final_mp4.name}"
        s3.upload_file(str(final_mp4), AWS_S3_BUCKET, s3_key)

        # 4️⃣  presign url
        url = s3.generate_presigned_url(
            "get_object",
            Params   = {"Bucket": AWS_S3_BUCKET, "Key": s3_key},
            ExpiresIn= 3600,          # 1 hour
        )

        return {"message": "success", "file_url": url}

    except Exception as exc:
        # bubble the error up so React shows “Upload failed – see console”
        return JSONResponse(status_code=500, content={"error": str(exc)})
