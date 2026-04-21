import json

import requests
import pandas as pd

"""
This function retrieves the top reddit comments searched by the entered keyword.
The search is done by using the 'search.json' query in the search url, which dumps the response as a usable json object
"""
def fetch_reddit_data(product_name, limit=100):

    print(f"Requesting reddit data for '{product_name}'...")
    
    url = f"https://www.reddit.com/search.json?q={product_name}&limit={limit}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) UniProjekt_AnalyseTool/1.0"
    }
    
    response = requests.get(url, headers=headers)
    results = []
    
    if response.status_code == 200:
        data = response.json()
        posts = data.get("data", {}).get("children", [])
        
        for post in posts:
            post_data = post["data"]

            text = post_data.get("title", "") + " - " + post_data.get("selftext", "")
            
            results.append({
                "platform": "Reddit",
                "product_id": product_name,
                "text_content": text,
                "engagement": post_data.get("score", 0), # Upvotes
                "url": "https://reddit.com" + post_data.get("permalink", "")
            })
    else:
        print(f"Error while connecting. Error code: {response.status_code}")
            
    df = pd.DataFrame(results)
    return df

def print_raw_reddit_json(product_name, limit=1):    
    url = f"https://www.reddit.com/search.json?q={product_name}&limit={limit}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) UniProjekt_AnalyseTool/1.0"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        raw_data = response.json()

        formated_json = json.dumps(raw_data, indent=4, ensure_ascii=False)
        
        print(formated_json)
        
    else:
        print(f"Error while connecting. Error Code: {response.status_code}")