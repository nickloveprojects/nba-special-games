import json

from fastapi import FastAPI, HTTPException, Response
from fastapi.staticfiles import StaticFiles

from . import config, output

app = FastAPI(title="NBA Special Games")


def _load(date: str | None):
    idx_file = config.OUT / "index.json"
    if not idx_file.exists():
        raise HTTPException(404, "No slate generated yet. Run: python -m app.cli run")
    idx = json.loads(idx_file.read_text())
    f = config.OUT / f"{date or idx['latest']}.json"
    if not f.exists():
        raise HTTPException(404, "No slate for that date")
    return json.loads(f.read_text())


@app.get("/api/slate")
def slate(date: str | None = None):
    return _load(date)


@app.get("/api/slate.csv")
def slate_csv(date: str | None = None):
    return Response(output.to_csv(_load(date)), media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=nba-special-games.csv"})


@app.get("/api/health")
def health():
    s = _load(None)
    return {"latest": s["date"], "generated_at": s["generated_at"], "warnings": len(s["warnings"])}


app.mount("/", StaticFiles(directory=config.WEB, html=True), name="web")
