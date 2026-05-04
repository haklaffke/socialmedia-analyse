from connectors.reddit_api import fetch_reddit_data
from connectors.reddit_api import print_raw_reddit_json
from connectors.hackernews_api import fetch_hackernews_data
from connectors.youtube_api import fetch_youtube_data
from connectors.amazon_api import fetch_amazon_data
from processing.cleaner import clean_dataframe
from processing.absa_analyzer import apply_absa_to_dataframe
from processing.visualizer import consolidate_results
import pandas as pd

if __name__ == "__main__":
    searchquery = input("Enter a product name: ")
    limit_input = input("Enter a limit for the search results: ")
    limit = int(limit_input)

    print("Requesting Data\n")
      
    reddit_df = fetch_reddit_data(searchquery, limit)
    hackernews_df = fetch_hackernews_data(searchquery, limit)
    youtube_df = fetch_youtube_data(searchquery, limit)
    #amazon_df = fetch_amazon_data(searchquery, limit)

    print("\nRequest returned successfully:\n")

    print("------------------Reddit Data-------------------------------------------------------------------------------------------------------")
    if not reddit_df.empty:
        for index, row in reddit_df.iterrows():
            print(f"[{row['engagement']} Upvotes] {row['text_content'][:200]}")
    else:
        print("No results found for '{searchquery}'")

    print("------------------Hackernews Data---------------------------------------------------------------------------------------------------")
    if not hackernews_df.empty:
        for index, row in hackernews_df.iterrows():
            print(f"[{row['engagement']} Upvotes] {row['text_content'][:200]}")
    else:
        print("No results found for '{searchquery}'")

    print("------------------Youtube Data------------------------------------------------------------------------------------------------------")
    if not youtube_df.empty:
        for index, row in youtube_df.iterrows():
            print(f"[{row['engagement']} Upvotes] {row['text_content'][:200]}")
    else:
        print("No results found for '{searchquery}'")
    
    #print("------------------Amazon Data-------------------")
    #if not amazon_df.empty:
    #    for index, row in amazon_df.iterrows():
    #        print(f"[{row['engagement']} Upvotes] {row['text_content'][:200]}")
    #else:
    #    print("No results found for '{searchquery}'")

print("\n--- Starting Data Cleaning ---")
    
reddit_df = clean_dataframe(reddit_df)
hackernews_df = clean_dataframe(hackernews_df)
youtube_df = clean_dataframe(youtube_df)
#amazon_df = clean_dataframe(amazon_df)

reddit_df = apply_absa_to_dataframe(reddit_df)
hackernews_df = apply_absa_to_dataframe(hackernews_df)
youtube_df = apply_absa_to_dataframe(youtube_df)
#amazon_df = apply_absa_to_dataframe(amazon_df)

all_dfs = [reddit_df, hackernews_df, youtube_df]
master_df = pd.concat(all_dfs, ignore_index=True)
master_df.to_csv("absa_results.csv", index=False)

konsolidiert_df = consolidate_results(master_df)