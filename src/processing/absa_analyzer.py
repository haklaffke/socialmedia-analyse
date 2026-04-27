import re
import pandas as pd

"""
Three categories of words to filter for: Keyords, Sentiments and Modifiers.
Keywords indicate on which part the feedback is focused (Battery, Display, etc).
Sentiments give different scores to different adjectives and therefore adds a value to them (good, bad, etc).
Modifiers multiply the sentiments by a factor (very good > good, etc) 
"""
ASPECT_KEYWORDS = {
    "General": [
        "phone", "iphone", "apple", "device", "smartphone", "laptop", "pc", "computer", 
        "macbook", "hp", "machine", "product", "buy", "purchase", "upgrade", 
        "tablet", "ipad", "notebook", "chromebook", "gadget", "samsung", "galaxy"
    ],
    "Battery": [
        "battery", "charge", "charging", "capacity", "power", "lifespan", "drain", 
        "charger", "plugged"
    ],
    "Display": [
        "screen", "display", "brightness", "colors", "touch", "pixel", "oled", "hz", 
        "refresh", "monitor", "panel", "glare", "bezel", "resolution"
    ],
    "Cost-Value": [
        "price", "cost", "sale", "budget", "expensive", "cheap", "value", "worth", 
        "discount", "$", "pay", "money", "deal", "overpriced", "bargain"
    ],
    "Processing": [
        "build", "material", "durable", "quality", "plastic", "titanium", "scratch", 
        "design", "feel", "keyboard", "trackpad", "touchpad", "hinge", "heavy", 
        "weight", "lightweight", "portable", "bulky", "sturdy", "flimsy", "glass", "pencil", "stylus", "pen"
    ],
    "Camera": [
        "camera", "photo", "video", "zoom", "lens", "pictures", "shot", "macro", 
        "webcam", "selfie", "faceid", "face"
    ],
    "Software": [
        "software", "ui", "ios", "windows", "macos", "ipados", "android", "linux", "ubuntu", 
        "distro", "kernel", "bug", "crash", "update", "performance", "speed", "processor", 
        "ram", "memory", "storage", "app", "apps", "bloatware", "stutter", "snappy", "chip", 
        "m1", "m2", "m3", "m4", "cpu", "gpu", "lag"
    ]
}

BASE_SENTIMENTS = {
    "catastrophe": -3, "garbage": -3, "trash": -3, "awful": -3, "worst": -3, 
    "hate": -3, "terrible": -3, "horrible": -3, "crap": -3, "scam": -3, 
    "waste": -3, "unusable": -3, "junk": -3,
    
    "overpriced": -2, "flimsy": -2, "overheating": -2, "bloatware": -2, 
    "ruined": -2, "annoying": -2, "frustrating": -2, "broken": -2,
    
    "bad": -1, "poor": -1, "weak": -1, "disappointing": -1, "useless": -1, 
    "worse": -1, "slow": -1, "laggy": -1, "loud": -1, "hot": -1, "stuck": -1, 
    "heavy": -1, "bulky": -1, "stutter": -1, "dim": -1, "glitchy": -1, "cheap": -1,
    
    "okay": 0, "average": 0, "fine": 0, "standard": 0, "normal": 0,
    
    "decent": 1, "good": 1, "solid": 1, "nice": 1, "better": 1, "well": 1, 
    "fast": 1, "smooth": 1, "snappy": 1, "lightweight": 1, "portable": 1, 
    "bright": 1, "sturdy": 1, "capable": 1, "clean": 1, "customizable": 1,
    
    "great": 2, "amazing": 2, "awesome": 2, "beautiful": 2, "love": 2, 
    "premium": 2, "bargain": 2, "gorgeous": 2, "responsive": 2,
    
    "perfect": 3, "fantastic": 3, "incredible": 3, "excellent": 3, "best": 3, 
    "flawless": 3, "unbeatable": 3
}

MODIFIERS = {
    "very": 2, "extremely": 2, "absolutely": 2, "totally": 2, "super": 2, "really": 2,
    "slightly": 0.5, "barely": 0.5,
    "not": -1, "no": -1, "never": -1
}

"""
Searching the strings for keywords, sentiments and modifiers and calculates a score. +/- 5.0 is max CAP
"""
def analyze_aspects_advanced(text):

    results = {aspect: 0.0 for aspect in ASPECT_KEYWORDS.keys()}
    
    if not isinstance(text, str) or not text.strip():
        return results

    text = text.lower()
    
    sentences = re.split(r'[!?;]|\.(?=\s)', text)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        found_aspects = []
        for aspect, keywords in ASPECT_KEYWORDS.items():
            if any(keyword in sentence for keyword in keywords):
                found_aspects.append(aspect)
                
        if found_aspects:
            satz_score = 0.0
            words = sentence.split()
            
            for i, word in enumerate(words):
                clean_word = re.sub(r'[^a-z]', '', word)
                
                if clean_word in BASE_SENTIMENTS:
                    score = BASE_SENTIMENTS[clean_word]
                    
                    if i > 0:
                        prev_word = re.sub(r'[^a-z]', '', words[i-1])
                        if prev_word in MODIFIERS:
                            score = score * MODIFIERS[prev_word]
                    
                    satz_score += score
            
            for aspect in found_aspects:
                results[aspect] += satz_score
                
    MAX_SCORE = 5.0
    MIN_SCORE = -5.0
    
    for aspect in results:
        if results[aspect] > MAX_SCORE:
            results[aspect] = MAX_SCORE
        elif results[aspect] < MIN_SCORE:
            results[aspect] = MIN_SCORE
            
    return results

"""
Applies the ABSA logic on the data frame and adds the results into a new collumn
"""
def apply_absa_to_dataframe(df):
    if df.empty:
        return df
        
    print(f"Running Advanced Aspect-Based Sentiment Analysis on {len(df)} rows...")
    
    absa_results = df['clean_text'].apply(analyze_aspects_advanced)
    
    absa_df = pd.DataFrame(absa_results.tolist())
    
    return pd.concat([df, absa_df], axis=1)