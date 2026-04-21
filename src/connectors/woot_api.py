import requests
import pandas as pd
import time

"""
This function retrieves amazon data via an undocumented woot endpoint (woot is a company bought by amazon).
To query for a certain product you have to enter the ASIN number of the product
The Exploit is documented under this url:
https://www.reddit.com/r/AmazonFBAOnlineRetail/comments/1rkd5oc/opensourced_an_amazon_review_scraper_576_reviews/
"""
def fetch_amazon_data(asin, limit=50):
    print(f"Requesting amazon data for '{asin}'...")
    
    url = f"https://www.woot.com/review/Reviews/{asin}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    results = []
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:

            data = response.json()
            
            reviews = data if isinstance(data, list) else data.get("Reviews", [])
            
            for rev in reviews:
                title = rev.get("Title", "")
                text = rev.get("ReviewText", rev.get("Text", ""))
                rating = rev.get("Rating", 0)
                
                results.append({
                    "platform": "Amazon (via Woot)",
                    "product_id": asin,
                    "text_content": f"{title} - {text}",
                    "engagement": rating, # Sterne 1-5
                    "url": f"https://www.amazon.com/dp/{asin}#customerReviews"
                })
                
                if len(results) >= limit:
                    break
        else:
            print(f"Request denied. Status Code: {response.status_code}")
            
    except Exception as e:
        print(f"Error occured. Error code: {e}")

    time.sleep(1)
    
    df = pd.DataFrame(results)
    return df