#!/usr/bin/env python
"""Start the web dashboard for Job Apply Automation."""

import uvicorn
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main():
    print("Starting Job Apply Automation dashboard at http://localhost:8000")
    uvicorn.run(
        "src.web.app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()