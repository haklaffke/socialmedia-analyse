import requests
import pandas as pd
import re

"""
This function retrieves the top comments for the entered product by using the official hacker news api
"""
def fetch_hackernews_data(product_name, limit=50):
    print(f"Requesting hacker news data for '{product_name}'...")
    
    url = f"http://hn.algolia.com/api/v1/search?query={product_name}&hitsPerPage={limit}"
    
    response = requests.get(url)
    results = []
    
    if response.status_code == 200:
        data = response.json()
        hits = data.get("hits", [])
        
        for hit in hits:
            text = hit.get("title", "")
            
            if not text and hit.get("comment_text"):
                text = hit.get("comment_text")
                text = re.sub(r'<[^>]+>', ' ', text)
                
            results.append({
                "platform": "Hacker News",
                "product_id": product_name,
                "text_content": text,
                "engagement": hit.get("points", 0) or 0, # Upvotes
                "url": f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
            })
    else:
        print(f"Error while connecting. Error code: {response.status_code}")
            
    df = pd.DataFrame(results)
    return df