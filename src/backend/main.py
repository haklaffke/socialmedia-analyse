from connectors.reddit_api import fetch_reddit_data, print_raw_reddit_json
from connectors.hackernews_api import fetch_hackernews_data
from connectors.youtube_api import fetch_youtube_data
from connectors.amazon_api import fetch_amazon_data
from processing.cleaner import clean_dataframe
from processing.absa_analyzer import apply_absa_to_dataframe
from processing.visualizer import consolidate_results
import pandas as pd
from fastapi import FastAPI

app = FastAPI()

@app.get("/{searchquery}/{limit}")
def read_item(searchquery: str, limit: int):

    print(f"Requesting Data for: {searchquery} with limit: {limit}\n")
    
    reddit_df = fetch_reddit_data(searchquery, limit)
    hackernews_df = fetch_hackernews_data(searchquery, limit)
    youtube_df = fetch_youtube_data(searchquery, limit)
    # amazon_df = fetch_amazon_data(searchquery, limit)

    print("\nRequest returned successfully:\n")

    if not reddit_df.empty:
        print(f"Reddit: {len(reddit_df)} rows found.")
    
    if not hackernews_df.empty:
        print(f"HackerNews: {len(hackernews_df)} rows found.")

    if not youtube_df.empty:
        print(f"YouTube: {len(youtube_df)} rows found.")

    print("\n--- Starting Data Cleaning & Analysis ---")
        
    reddit_df = clean_dataframe(reddit_df)
    hackernews_df = clean_dataframe(hackernews_df)
    youtube_df = clean_dataframe(youtube_df)

    reddit_df = apply_absa_to_dataframe(reddit_df)
    hackernews_df = apply_absa_to_dataframe(hackernews_df)
    youtube_df = apply_absa_to_dataframe(youtube_df)

    all_dfs = [reddit_df, hackernews_df, youtube_df]
    master_df = pd.concat(all_dfs, ignore_index=True)
    
    master_df.to_csv("absa_results.csv", index=False)

    consolidated_df = consolidate_results(master_df)

    return {
        "success": True, 
        "search_term": searchquery,
        "data": consolidated_df.to_dict(orient='records')
    }