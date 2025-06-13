import pandas as pd
import json
import os
from dotenv import load_dotenv
from brain_api import BrainClient
from collections import defaultdict
import time

# Load environment variables from .env file
load_dotenv()

def load_csv_data(filename):
    """Load data from CSV file using pandas"""
    try:
        df = pd.read_csv(filename)
        return df
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return None

def process_keywords(df):
    """Process keywords and organize them by country and global status"""
    # Initialize dictionaries for results
    country_keywords = defaultdict(list)
    global_keywords = []
    
    # Process each row
    for _, row in df.iterrows():
        keyword = str(row['Keyword']).strip()
        reason = str(row['Reason-to_Flag']).strip()
        country_code = str(row['Country_Code']).strip()
        
        # Skip empty keywords
        if not keyword:
            continue
            
        # Create keyword entry with reason
        keyword_entry = {
            'keyword': keyword,
            'reason': reason
        }
        
        # If country code is ALL, add to global keywords
        if country_code == 'ALL':
            global_keywords.append(keyword_entry)
        else:
            # Add to specific country
            country_keywords[country_code].append(keyword_entry)
    
    return country_keywords, global_keywords

def save_results(country_keywords, global_keywords):
    """Save results to JSON and CSV files"""
    # Save country-specific keywords to JSON
    with open('country_keywords.json', 'w', encoding='utf-8') as f:
        json.dump(country_keywords, f, indent=2, ensure_ascii=False)
    
    # Save global keywords to JSON
    with open('global_keywords.json', 'w', encoding='utf-8') as f:
        json.dump({'ALL': global_keywords}, f, indent=2, ensure_ascii=False)
    
    # Create and save country-specific CSV files
    for country_code, keywords in country_keywords.items():
        df = pd.DataFrame(keywords)
        df.to_csv(f'keywords_{country_code}.csv', index=False)
    
    # Create and save global keywords CSV
    global_df = pd.DataFrame(global_keywords)
    global_df.to_csv('keywords_ALL.csv', index=False)

def main():
    # Initialize Brain API client
    client = BrainClient(api_key=os.getenv('BRAIN_API_KEY'))
    
    # Load CSV data
    print("Loading CSV data...")
    df = load_csv_data('keywords.csv')
    
    if df is None:
        print("Failed to load CSV data. Exiting...")
        return
    
    print(f"Loaded {len(df)} keywords")
    
    # Process keywords
    print("Processing keywords...")
    country_keywords, global_keywords = process_keywords(df)
    
    # Save results
    print("Saving results...")
    save_results(country_keywords, global_keywords)
    
    # Print summary
    print("\nProcessing Summary:")
    print(f"Total countries with keywords: {len(country_keywords)}")
    print(f"Global keywords (ALL): {len(global_keywords)}")
    
    for country, keywords in country_keywords.items():
        print(f"  {country}: {len(keywords)} keywords")

if __name__ == "__main__":
    # Check if Brain API key is set
    if not os.getenv('BRAIN_API_KEY'):
        print("Please set your BRAIN_API_KEY environment variable")
        print("You can set it by running: export BRAIN_API_KEY='your-api-key-here'")
        exit(1)
    
    main()
