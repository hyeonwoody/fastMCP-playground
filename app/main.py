"""Core application logic"""
import os
import sys
from pathlib import Path
import uvicorn

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import tools.greet
import tools.ask
import app.lang_serve
from app.state import mcp
from app.state import api


@api.get("/health")
def health():
    return {"status": "ok"}


def main() -> None:
    mcp_app = mcp.http_app()
    mcp_app.mount("/api/v1", api)
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(mcp_app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
