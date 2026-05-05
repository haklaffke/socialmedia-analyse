import os
import requests
import pandas as pd
import time
from dotenv import load_dotenv

load_dotenv()

"""
Amazon Api via RapidAPI (100 Requests per month)
If the Rate Limit is reached we have to create a new account to get a new api Key
"""
def fetch_amazon_data(product_name, limit=20):
    print(f"Requesting amazon data for '{product_name}'")
    
    api_key = os.getenv("RAPIDAPI_KEY")
    host = "real-time-amazon-data.p.rapidapi.com"
    
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": host
    }

    search_url = f"https://{host}/search"
    search_params = {"query": product_name, "country": "US", "category_id": "aps"}

    try:
        search_response = requests.get(search_url, headers=headers, params=search_params)
        if search_response.status_code != 200:
            return pd.DataFrame()
        
        products = search_response.json().get("data", {}).get("products", [])
        if not products:
            return pd.DataFrame()

        sorted_products = sorted(products, key=lambda x: int(x.get('product_num_reviews') or 0), reverse=True)
        target_asin = sorted_products[0].get("asin")
        
        print(f"Selected ASIN: {target_asin} | Collecting up to {limit} reviews...")

        results = []
        current_page = 1
        
        while len(results) < limit:
            print(f"  -> Fetching page {current_page}...")
            
            reviews_url = f"https://{host}/product-reviews"
            reviews_params = {
                "asin": target_asin,
                "country": "US",
                "sort_by": "TOP_REVIEWS",
                "page": str(current_page)
            }
            
            response = requests.get(reviews_url, headers=headers, params=reviews_params)
            
            if response.status_code == 200:
                raw_reviews = response.json().get("data", {}).get("reviews", [])
                
                if not raw_reviews:
                    print("  -> No more reviews available on Amazon.")
                    break
                    
                for rev in raw_reviews:
                    results.append({
                        "platform": "Amazon",
                        "product_id": product_name,
                        "text_content": f"{rev.get('review_title', '')}: {rev.get('review_comment', '')}",
                        "engagement": rev.get("review_star_rating", 0),
                        "url": rev.get("review_link", f"https://www.amazon.com/dp/{target_asin}")
                    })
                    if len(results) >= limit:
                        break
                
                current_page += 1
                time.sleep(0.5) 
            else:
                print(f"  -> Error on page {current_page}. Code: {response.status_code}")
                break
        
        print(f"Successfully collected {len(results)} reviews total.")
        return pd.DataFrame(results)
            
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()
