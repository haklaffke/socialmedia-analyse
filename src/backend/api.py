"""
FastAPI service that exposes the analysis pipeline.

Start with:
    uvicorn api:app --host 0.0.0.0 --port 8000

Endpoints:
    GET  /health           -> liveness probe
    POST /analyze          -> trigger the pipeline (synchronous)
                              body: {"search_query": "iphone 15", "limit": 50}
    GET  /runs             -> list recent runs
"""
import os
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text

from db.database import engine, Base, SessionLocal
from db import models  # noqa: F401  (registers ORM models on Base.metadata)
from db.repository import save_run
from main import run_pipeline


app = FastAPI(
    title="Social Media ABSA API",
    description="Triggers the social-media analysis pipeline and persists results to Postgres.",
    version="1.0.0",
)


@app.on_event("startup")
def _startup() -> None:
    # Make sure the Postgres tables exist before any request hits the API.
    Base.metadata.create_all(engine)
    print("API ready. Waiting for POST /analyze ...")


class AnalyzeRequest(BaseModel):
    search_query: str = Field(..., min_length=1, description="Product name / keyword to analyse")
    limit: int = Field(50, gt=0, le=1000, description="Max number of items per platform")


class AnalyzeResponse(BaseModel):
    run_id: int
    search_query: str
    limit: int
    rows_persisted: int
    csv_path: Optional[str] = None


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    try:
        master_df = run_pipeline(req.search_query, req.limit)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {exc}") from exc

    # Persist CSV (mounted volume in docker-compose).
    output_dir = "output" if os.path.isdir("output") else "."
    csv_path: Optional[str] = os.path.join(output_dir, "absa_results.csv")
    try:
        master_df.to_csv(csv_path, index=False)
    except Exception as exc:
        print(f"Warning: could not write CSV: {exc}")
        csv_path = None

    run_id = save_run(master_df, req.search_query, req.limit)

    return AnalyzeResponse(
        run_id=run_id,
        search_query=req.search_query,
        limit=req.limit,
        rows_persisted=len(master_df),
        csv_path=csv_path,
    )


@app.get("/runs")
def list_runs(limit: int = 20) -> list[dict]:
    with SessionLocal() as session:
        rows = session.execute(
            text(
                "SELECT id, search_query, row_limit, created_at "
                "FROM analysis_runs ORDER BY id DESC LIMIT :n"
            ),
            {"n": limit},
        ).mappings().all()
        return [dict(r) for r in rows]


