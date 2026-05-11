import os
import sys
import pandas as pd
from dotenv import load_dotenv
from connectors.reddit_api import fetch_reddit_data
from connectors.hackernews_api import fetch_hackernews_data
from connectors.youtube_api import fetch_youtube_data
# from connectors.amazon_api import fetch_amazon_data  # currently disabled
from processing.cleaner import clean_dataframe
from processing.absa_analyzer import apply_absa_to_dataframe
from processing.visualizer import consolidate_results
from db.database import engine, Base
from db import models  # noqa: F401  (registers ORM models on Base.metadata)
from db.repository import save_run


def _get_param(env_name: str, prompt: str) -> str:
    """Read a parameter from env first, fall back to interactive input (TTY only)."""
    value = os.getenv(env_name)
    if value:
        return value
    if sys.stdin.isatty():
        return input(prompt)
    raise RuntimeError(
        f"Missing parameter: set environment variable {env_name} "
        f"(no interactive TTY available)."
    )


def run_pipeline(searchquery: str, limit: int) -> pd.DataFrame:
    print("Requesting Data\n")

    reddit_df = fetch_reddit_data(searchquery, limit)
    hackernews_df = fetch_hackernews_data(searchquery, limit)
    youtube_df = fetch_youtube_data(searchquery, limit)
    # amazon_df = fetch_amazon_data(searchquery, limit)

    print("\nRequest returned successfully:\n")

    for label, df in [
        ("Reddit", reddit_df),
        ("Hackernews", hackernews_df),
        ("Youtube", youtube_df),
    ]:
        print(f"------------------{label} Data------------------")
        if df is not None and not df.empty:
            for _, row in df.iterrows():
                print(f"[{row['engagement']} Upvotes] {row['text_content'][:200]}")
        else:
            print(f"No results found for '{searchquery}'")

    print("\n--- Starting Data Cleaning ---")
    reddit_df = clean_dataframe(reddit_df)
    hackernews_df = clean_dataframe(hackernews_df)
    youtube_df = clean_dataframe(youtube_df)

    reddit_df = apply_absa_to_dataframe(reddit_df)
    hackernews_df = apply_absa_to_dataframe(hackernews_df)
    youtube_df = apply_absa_to_dataframe(youtube_df)

    return pd.concat([reddit_df, hackernews_df, youtube_df], ignore_index=True)


if __name__ == "__main__":
    searchquery = _get_param("SEARCH_QUERY", "Enter a product name: ")
    limit = int(_get_param("SEARCH_LIMIT", "Enter a limit for the search results: "))

    master_df = run_pipeline(searchquery, limit)

    # Persist CSV. Uses ./output (mounted volume in Docker) when present,
    # otherwise the current working directory.
    output_dir = "output" if os.path.isdir("output") else "."
    csv_path = os.path.join(output_dir, "absa_results.csv")
    master_df.to_csv(csv_path, index=False)
    print(f"Wrote {csv_path}")

    # Make sure the Postgres tables exist, then persist the current run.
    Base.metadata.create_all(engine)
    run_id = save_run(master_df, searchquery, limit)
    print(f"Stored pipeline run in Postgres with id={run_id}")

    consolidate_results(master_df)
