import numpy as np
import pandas as pd

def calculate_weight(score):
    """
    Berechnet das Gewicht eines Kommentars anhand der Interaktionen.
    Positiv = Logarithmischer Boost (z.B. 100 Upvotes -> ~5.6 Gewicht).
    Negativ = Starke Abwertung (z.B. -9 Downvotes -> 0.1 Gewicht).
    """
    if pd.isna(score):
        return 1.0
        
    try:
        score = float(score)
    except (ValueError, TypeError):
        return 1.0
        
    if score >= 0:
        return np.log1p(score) + 1.0
    else:
        # Bei negativem Score: 1 / (Betrag des Scores + 1)
        return 1.0 / (abs(score) + 1.0)

"""
Summarizes the score per plattform and weights them based on engagement.
Filters out comments without a value/opinion (score of 0).
"""
def consolidate_results(df):

    print("\n📊 Consolidating the results with engagement weighting...")
    
    aspects = ["General", "Battery", "Display", "Cost-Value", "Processing", "Camera", "Software"]
    
    analysis_df = df.copy()
    
    # 1. Die neue Gewichts-Spalte berechnen
    analysis_df['weight'] = analysis_df['engagement'].apply(calculate_weight)
    
    weighted_results = []
    
    # 2. Für jede Plattform einzeln den gewichteten Durchschnitt berechnen
    for platform in analysis_df['platform'].unique():
        platform_df = analysis_df[analysis_df['platform'] == platform]
        platform_scores = {'platform': platform}
        
        for aspect in aspects:
            # Nur Zeilen nehmen, in denen der Aspekt auch bewertet wurde (also nicht 0.0 ist)
            valid_rows = platform_df[platform_df[aspect] != 0.0]
            
            if not valid_rows.empty:
                # Gewichteter Durchschnitt: (Score * Gewicht) / Summe aller Gewichte
                weighted_avg = np.average(valid_rows[aspect], weights=valid_rows['weight'])
                platform_scores[aspect] = weighted_avg
            else:
                platform_scores[aspect] = np.nan
                
        weighted_results.append(platform_scores)
        
    # 3. In einen schönen DataFrame umwandeln
    summary = pd.DataFrame(weighted_results).set_index('platform')
    
    # Filling the 0.0 Scores back in and rounding the numbers to look prettier
    summary = summary.round(2).fillna(0)
    
    print("\n--- 📈 WEIGHTED RESULTS PER PLATFORM ---")
    print(summary.to_string())
    print("-" * 50)

    return summary