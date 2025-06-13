import pandas as pd
import json
import os
from dotenv import load_dotenv
import requests
from typing import Dict, List, Any

# Load environment variables
load_dotenv()

class KeywordProcessor:
    def __init__(self):
        self.brain_api_key = os.getenv('BRAIN_API_KEY')
        self.brain_api_url = os.getenv('BRAIN_API_URL', 'https://brain-platform.pattern.com/api/v1/llms/invoke')  
        self.headers = {
            'Authorization': f'Bearer {self.brain_api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def read_keywords(self, file_path: str) -> pd.DataFrame:
        """Read the keywords CSV file"""
        return pd.read_csv(file_path)

    def process_with_brain_api(self, keyword: str, reason: str) -> dict:
        """Process keyword with Brain API"""
        try:
            prompt = f"Keyword: {keyword}\nReason: {reason}"
            payload = {
                "prompt": prompt,
                "model": "gpt-4.1"  
            }
            response = requests.post(
                self.brain_api_url,
                headers=self.headers,
                data=json.dumps(payload)
            )
            response.raise_for_status()
            # The Brain API returns the result in ['response']
            return {"response": response.json().get('response', '')}
        except Exception as e:
            print(f"Error processing keyword {keyword}: {str(e)}")
            return {}

    def create_country_json(self, df: pd.DataFrame) -> Dict[str, List[Dict[str, Any]]]:
        """Create JSON structure organized by country"""
        country_data = {}
        
        # Process each row
        for _, row in df.iterrows():
            keyword = row['Keyword']
            reason = row['Reason-to_Flag']
            country_code = row['Country_Code']
            
            # Process with Brain API
            brain_analysis = self.process_with_brain_api(keyword, reason)
            
            # Create keyword entry
            keyword_entry = {
                'keyword': keyword,
                'reason': reason,
                'analysis': brain_analysis
            }
            
            # Add to country data
            if country_code not in country_data:
                country_data[country_code] = []
            country_data[country_code].append(keyword_entry)
        
        return country_data

    def create_all_countries_json(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Create JSON structure for keywords that apply to all countries"""
        all_countries_data = []
        
        # Filter for ALL country code
        all_countries_df = df[df['Country_Code'] == 'ALL']
        
        for _, row in all_countries_df.iterrows():
            keyword = row['Keyword']
            reason = row['Reason-to_Flag']
            
            # Process with Brain API
            brain_analysis = self.process_with_brain_api(keyword, reason)
            
            keyword_entry = {
                'keyword': keyword,
                'reason': reason,
                'analysis': brain_analysis
            }
            all_countries_data.append(keyword_entry)
        
        return all_countries_data

    def create_country_csv(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create CSV structure with countries as columns"""
        # Pivot the data to get countries as columns
        country_pivot = df.pivot_table(
            index='Keyword',
            columns='Country_Code',
            values='Reason-to_Flag',
            aggfunc='first'
        ).reset_index()
        
        return country_pivot

    def process_and_save(self, input_file: str):
        """Main processing function"""
        # Read the input file
        df = self.read_keywords(input_file)
        
        # Create country-specific JSON
        country_json = self.create_country_json(df)
        with open('violation_patterns_by_country.json', 'w', encoding='utf-8') as f:
            json.dump(country_json, f, indent=2, ensure_ascii=False)
        
        # Create ALL countries JSON
        all_countries_json = self.create_all_countries_json(df)
        with open('violation_patterns_all_countries.json', 'w', encoding='utf-8') as f:
            json.dump(all_countries_json, f, indent=2, ensure_ascii=False)
        
        # Create country-specific CSV
        country_csv = self.create_country_csv(df)
        country_csv.to_csv('violation_patterns_by_country.csv', index=False)
        
        print("Processing complete! Files generated:")
        print("1. violation_patterns_by_country.json")
        print("2. violation_patterns_all_countries.json")
        print("3. violation_patterns_by_country.csv")

if __name__ == "__main__":
    processor = KeywordProcessor()
    processor.process_and_save('keywords.csv') 