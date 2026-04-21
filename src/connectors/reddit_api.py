import json
import requests
import pandas as pd
import time  # <-- NEU: Wichtig für die Pausen zwischen den Abfragen!

"""
This function retrieves reddit comments searched by the entered keyword.
It uses pagination (the 'after' token) to bypass the 100-request limit.
"""
def fetch_reddit_data(product_name, limit=100):

    print(f"Requesting reddit data for '{product_name}'... (Target: {limit} results)")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) UniProjekt_AnalyseTool/1.0"
    }
    
    results = []
    after_token = None
    
    # Solange wir unser Ziel-Limit noch nicht erreicht haben...
    while len(results) < limit:
        # Berechnen, wie viele wir noch brauchen (aber nie mehr als 100 auf einmal anfragen)
        request_limit = min(100, limit - len(results))
        
        url = f"https://www.reddit.com/search.json?q={product_name}&limit={request_limit}"
        
        # Wenn wir einen Token haben, hängen wir ihn an (für Seite 2, 3, 4...)
        if after_token:
            url += f"&after={after_token}"
            
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            posts = data.get("data", {}).get("children", [])
            
            # Wenn Reddit keine Posts mehr zurückgibt, sind wir am absoluten Ende
            if not posts:
                print("Keine weiteren Ergebnisse bei Reddit gefunden.")
                break
                
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
                
                # Mitten in der Schleife abbrechen, falls wir exakt das Limit erreicht haben
                if len(results) >= limit:
                    break
            
            # Den Token für die nächste Seite holen
            after_token = data.get("data", {}).get("after")
            
            # Wenn 'after' leer ist, gibt es keine nächste Seite mehr
            if not after_token:
                break
                
            # --- DER WICHTIGSTE TEIL: SPAM-SCHUTZ ---
            print(f"Gefunden: {len(results)}... Lade nächste Seite...")
            time.sleep(1.5)  # 1,5 Sekunden warten, um Error 429 zu vermeiden!
            
        else:
            print(f"Error while connecting. Error code: {response.status_code}")
            break
            
    print(f"✅ Reddit Download abgeschlossen. {len(results)} Posts gesammelt.")
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