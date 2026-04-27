import numpy as np
import matplotlib.pyplot as plt

"""
Summarizes the score per plattform and filters out comments without a value/opinion (score of 0)
"""
def consolidate_results(df):

    print("Consolidating the results...")
    
    aspects = ["General", "Battery", "Display", "Cost-Value", "Processing", "Camera", "Software"]
    
    analysis_df = df.copy()
    
    # Replacing 0.0 with NaN so it does not influence the score calculation later on
    analysis_df[aspects] = analysis_df[aspects].replace(0.0, np.nan)
    
    # Calculating the mean per category
    summary = analysis_df.groupby('platform')[aspects].mean()
    
    # Filling the 0.0 Scores back in and rounding the numbers to look prettier
    summary = summary.round(2).fillna(0)
    
    print("\n--- Results ---")
    print(summary.to_string())
    print("-" * 50)
    
    return summary