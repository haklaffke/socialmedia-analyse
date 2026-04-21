from connectors.reddit_api import fetch_reddit_data
from connectors.reddit_api import print_raw_reddit_json
from connectors.hackernews_api import fetch_hackernews_data
from connectors.youtube_api import fetch_youtube_data
from connectors.amazon_api import fetch_amazon_data

if __name__ == "__main__":
    searchquery = input("Enter a product name: ")
    limit_input = input("Enter a limit for the search results: ")
    limit = int(limit_input)
    
    print("Requesting Data\n")
      
    reddit_df = fetch_reddit_data(searchquery, limit)
    hackernews_df = fetch_hackernews_data(searchquery, limit)
    youtube_df = fetch_youtube_data(searchquery, limit)
    amazon_df = fetch_amazon_data(searchquery, limit)

    print("\nRequest returned successfully:\n")

    print("------------------Reddit Data-------------------")
    if not reddit_df.empty:
        for index, row in reddit_df.iterrows():
            print(f"[{row['engagement']} Upvotes] {row['text_content'][:200]}")
    else:
        print("No results found for '{searchquery}'")

    print("------------------Hackernews Data-------------------")
    if not hackernews_df.empty:
        for index, row in hackernews_df.iterrows():
            print(f"[{row['engagement']} Upvotes] {row['text_content'][:200]}")
    else:
        print("No results found for '{searchquery}'")

    print("------------------Youtube Data-------------------")
    if not youtube_df.empty:
        for index, row in youtube_df.iterrows():
            print(f"[{row['engagement']} Upvotes] {row['text_content'][:200]}")
    else:
        print("No results found for '{searchquery}'")
    
    print("------------------Amazon Data-------------------")
    if not amazon_df.empty:
        for index, row in amazon_df.iterrows():
            print(f"[{row['engagement']} Upvotes] {row['text_content'][:200]}")
    else:
        print("No results found for '{searchquery}'")
