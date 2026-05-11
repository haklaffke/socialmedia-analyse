import pandas as pd

from .database import SessionLocal
from .models import AnalysisRun, Post, AspectScore

ASPECTS = ["General", "Battery", "Display", "Cost-Value", "Processing", "Camera", "Software"]


def _to_int(value, default=0):
    try:
        if value is None or pd.isna(value):
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


"""
Persists a complete pipeline run into Postgres.
- Creates one analysis_runs row.
- Creates one posts row per DataFrame row.
- Creates one aspect_scores row per (post, aspect) where the score is a valid number.
Returns the new run_id.
"""
def save_run(master_df: pd.DataFrame, search_query: str, row_limit: int) -> int:
    if master_df is None or master_df.empty:
        print("save_run: empty DataFrame, nothing to persist.")
        return -1

    print(f"Persisting {len(master_df)} rows into Postgres...")

    with SessionLocal() as session:
        run = AnalysisRun(search_query=search_query, row_limit=row_limit)
        session.add(run)
        session.flush()  # populate run.id

        for _, row in master_df.iterrows():
            post = Post(
                run_id=run.id,
                platform=row.get("platform"),
                product_id=str(row.get("product_id", "") or ""),
                text_content=row.get("text_content"),
                clean_text=row.get("clean_text"),
                engagement=_to_int(row.get("engagement")),
                url=row.get("url"),
            )
            session.add(post)
            session.flush()  # populate post.id

            for aspect in ASPECTS:
                if aspect not in row.index:
                    continue
                value = row[aspect]
                if pd.isna(value):
                    continue
                session.add(AspectScore(
                    post_id=post.id,
                    run_id=run.id,
                    platform=post.platform,
                    aspect=aspect,
                    score=float(value),
                ))

        session.commit()
        print(f"Run persisted with id={run.id}")
        return run.id


