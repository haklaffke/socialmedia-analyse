import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
"""
This function retrieves youtube comments under the top 2 review videos for the entered search query.
To use it you must create your own 'Youtube Data API v3 Key' via https://console.cloud.google.com
"""
def fetch_youtube_data(product_name, limit=50):
    
    print(f"Requesting youtube data for '{product_name}'...")
    
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("Error: YOUTUBE_API_KEY is missing in .env file.")
        return pd.DataFrame()

    results = []
    
    search_url = "https://www.googleapis.com/youtube/v3/search"
    search_params = {
        "part": "snippet",
        "q": f"{product_name} review",
        "type": "video",
        "maxResults": 2, 
        "key": api_key
    }
    
    search_response = requests.get(search_url, params=search_params)
    
    if search_response.status_code == 200:
        search_data = search_response.json()
        
        video_ids = [item["id"]["videoId"] for item in search_data.get("items", [])]
        
        comments_per_video = max(1, limit // len(video_ids)) if video_ids else limit
        
        for video_id in video_ids:
            comments_url = "https://www.googleapis.com/youtube/v3/commentThreads"
            comments_params = {
                "part": "snippet",
                "videoId": video_id,
                "maxResults": comments_per_video,
                "order": "relevance", 
                "textFormat": "plainText",
                "key": api_key
            }
            
            comments_response = requests.get(comments_url, params=comments_params)
            
            if comments_response.status_code == 200:
                comments_data = comments_response.json()
                threads = comments_data.get("items", [])
                
                for thread in threads:
                    comment = thread["snippet"]["topLevelComment"]["snippet"]
                    
                    results.append({
                        "platform": "YouTube",
                        "product_id": product_name,
                        "text_content": comment.get("textDisplay", ""),
                        "engagement": comment.get("likeCount", 0),
                        "url": f"https://www.youtube.com/watch?v={video_id}&lc={thread['id']}"
                    })
            else:
                print(f"Error while connecting to comments API. Error code: {comments_response.status_code}")
    else:
        print(f"Error while connecting to search API. Error code: {search_response.status_code}")

    df = pd.DataFrame(results)
    return df