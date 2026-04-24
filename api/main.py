from fastapi import FastAPI
from datetime import datetime, timezone

app = FastAPI(title="TFTP API", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "tftp-api",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }