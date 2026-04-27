import re
import pandas as pd

"""
Deleting new lines, extra spaces/tabs, trailing and leading whitespaces and links
"""
def clean_text(text):
    if not isinstance(text, str):
        return ""
    
    text = re.sub(r'\s+', ' ', text)
    
    text = re.sub(r'http\S+|www.\S+', '', text)
    
    return text.strip()

"""
Cleans the dataframe if not empty
"""
def clean_dataframe(df):
    if df.empty:
        return df
        
    print(f"Cleaning DataFrame with {len(df)} rows...")
    df['clean_text'] = df['text_content'].apply(clean_text)
    
    df = df[df['clean_text'] != ""]
    return df