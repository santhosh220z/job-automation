from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import asyncio
import json
from datetime import datetime, timezone

from src.main import run, check_replies
from src.tracking.sheets import get_applications
from src.config import SEARCH_KEYWORDS, SEARCH_LOCATION, MAX_APPLICATIONS_PER_RUN

APP_DIR = Path(__file__).parent

app = FastAPI(title="Job Apply Automation")

app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(APP_DIR / "templates"))

_log_queues: list[asyncio.Queue] = []


def _broadcast_log(msg: str):
    now = datetime.now(timezone.utc).strftime("%H:%M:%S")
    line = f"[{now}] {msg}"
    for q in _log_queues:
        try:
            q.put_nowait(line)
        except asyncio.QueueFull:
            _log_queues.remove(q)


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    apps = get_applications()
    stats = {
        "total": len(apps),
        "applied": sum(1 for a in apps if a.get("Status", "").lower() == "applied"),
        "replied": sum(1 for a in apps if a.get("Status", "").lower() == "replied"),
        "interview": sum(1 for a in apps if a.get("Status", "").lower() == "interview"),
    }
    return templates.TemplateResponse("index.html", {
        "request": request,
        "keywords": ",".join(SEARCH_KEYWORDS),
        "location": SEARCH_LOCATION,
        "max_apps": MAX_APPLICATIONS_PER_RUN,
        "applications": apps,
        "stats": stats,
    })


@app.get("/api/applications")
async def api_applications():
    apps = get_applications()
    return {"applications": apps, "count": len(apps)}


@app.get("/api/log-stream")
async def log_stream(request: Request):
    queue: asyncio.Queue = asyncio.Queue(maxsize=100)
    _log_queues.append(queue)

    async def event_generator():
        try:
            yield "event: connected\ndata: {}\n\n"
            while True:
                if await request.is_disconnected():
                    break
                try:
                    line = await asyncio.wait_for(queue.get(), timeout=30)
                    yield f"data: {json.dumps({'line': line})}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            if queue in _log_queues:
                _log_queues.remove(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/run")
async def api_run(
    background_tasks: BackgroundTasks,
    keywords: str = Form(""),
    location: str = Form(""),
    max_apps: int = Form(10),
    linkedin: str = Form("on"),
    indeed: str = Form("on"),
    wellfound: str = Form("on"),
):
    platforms = []
    if linkedin == "on":
        platforms.append("LinkedIn")
    if indeed == "on":
        platforms.append("Indeed")
    if wellfound == "on":
        platforms.append("Wellfound")

    if not platforms:
        return {"error": "No platforms selected"}

    _broadcast_log("=== Run triggered from Web UI ===")

    async def task():
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: run(
                keywords=keywords.strip() or None,
                location=location.strip() or None,
                max_apps=max_apps,
                platforms=platforms,
                on_log=_broadcast_log,
            ),
        )
        _broadcast_log("=== Run finished, checking replies ===")
        await loop.run_in_executor(
            None,
            lambda: check_replies(on_log=_broadcast_log),
        )
        _broadcast_log("=== All done ===")

    background_tasks.add_task(task)
    return {"status": "started"}


@app.post("/api/check-replies")
async def api_check_replies(background_tasks: BackgroundTasks):
    _broadcast_log("=== Manual Gmail check ===")

    async def task():
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: check_replies(on_log=_broadcast_log),
        )
        _broadcast_log("=== Reply check done ===")

    background_tasks.add_task(task)
    return {"status": "started"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.web.app:app", host="0.0.0.0", port=8000, reload=False)