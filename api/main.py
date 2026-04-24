from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from tftp.TftpClient import TftpClient

app = FastAPI(title="TFTP API", version="0.1.0")

class TransferRequest(BaseModel):
    host: str
    port: int = Field(default=69, ge=1, le=65535)
    remote_filename: str
    local_path: str


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "tftp-api",
        "timestamp": _utc_now(),
    }


@app.post("/upload")
def upload_file(request: TransferRequest) -> dict:
    local_path = Path(request.local_path).expanduser().resolve()
    if not local_path.exists() or not local_path.is_file():
        raise HTTPException(status_code=400, detail="local_path must be an existing file")

    client = TftpClient(request.host, request.port)

    try:
        with local_path.open("rb") as file_handle:
            client.upload(request.remote_filename, file_handle, timeout=3, retries=1)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "ok": True,
        "message": "Upload complete",
        "host": request.host,
        "port": request.port,
        "remote_filename": request.remote_filename,
        "local_path": str(local_path),
    }


@app.post("/download")
def download_file(request: TransferRequest) -> dict:
    local_path = Path(request.local_path).expanduser().resolve()
    local_path.parent.mkdir(parents=True, exist_ok=True)

    client = TftpClient(request.host, request.port)

    try:
        client.download(request.remote_filename, output=str(local_path))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "ok": True,
        "message": "Download complete",
        "host": request.host,
        "port": request.port,
        "remote_filename": request.remote_filename,
        "local_path": str(local_path),
    }