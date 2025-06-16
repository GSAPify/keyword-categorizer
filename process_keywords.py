import pandas as pd
import json
import os
from dotenv import load_dotenv
from typing import Dict, List, Any, Tuple
import concurrent.futures
import time
from pydantic import BaseModel
from brain_platform_client.brain_api import BrainApi

# Load environment variables
load_dotenv()

class KeywordAnalysis(BaseModel):
    """Pydantic model for structured keyword analysis response"""
    analyses: List[Dict[str, str]]

class KeywordProcessor:
    def __init__(self):
        self.brain_api = BrainApi()
        self.batch_size = 10  # Process 10 keywords per API call
        self.max_retries = 3

    def read_keywords(self, file_path: str) -> pd.DataFrame:
        """Read the keywords CSV file"""
        return pd.read_csv(file_path)

    def create_batch_prompt(self, keyword_data: List[Dict]) -> str:
        """Create a batch prompt for multiple keywords"""
        prompt = "You are a helpful assistant that analyzes keywords and their reasons for flagging. Your task is to analyze each keyword and provide a brief analysis.\n\n"
        prompt += "Keywords to analyze:\n\n"
        
        for i, data in enumerate(keyword_data, 1):
            prompt += f"{i}. Keyword: {data['keyword']}\n"
            prompt += f"   Reason: {data['reason']}\n"
            if data.get('valid_country_codes'):
                prompt += f"   Valid Country Codes: {data['valid_country_codes']}\n"
            if data.get('country'):
                prompt += f"   Country: {data['country']}\n"
            if data.get('compliance_region'):
                prompt += f"   Compliance Region: {data['compliance_region']}\n"
            if data.get('country_code'):
                prompt += f"   Country Code: {data['country_code']}\n"
            prompt += "\n"
        
        prompt += "Respond with JSON in the following format:\n"
        prompt += "{\n"
        prompt += '  "analyses": [\n'
        prompt += '    {"keyword": "keyword1", "analysis": "analysis text"},\n'
        prompt += '    {"keyword": "keyword2", "analysis": "analysis text"}\n'
        prompt += '  ]\n'
        prompt += "}"
        return prompt

    def process_batch_with_brain_api(self, keyword_batch: List[Dict]) -> Dict[str, str]:
        """Process a batch of keywords with Brain API using the new client"""
        analyses = {}
        
        for attempt in range(self.max_retries):
            try:
                prompt = self.create_batch_prompt(keyword_batch)
                
                print(f"Sending batch request for {len(keyword_batch)} keywords (attempt {attempt + 1})")
                
                # Use the new BrainApi client with structured output
                response_payload = self.brain_api.invoke_llm(
                    prompt=prompt,
                    response_format=KeywordAnalysis,
                )
                
                # Parse the structured response
                try:
                    keyword_analysis = KeywordAnalysis.model_validate_json(response_payload.response)
                    
                    for analysis in keyword_analysis.analyses:
                        keyword = analysis.get('keyword', '').strip()
                        analysis_text = analysis.get('analysis', '')
                        if keyword:
                            analyses[keyword] = analysis_text
                    
                    print(f"Successfully processed batch of {len(keyword_analysis.analyses)} keywords")
                    return analyses
                    
                except Exception as parse_error:
                    print(f"Failed to parse structured response: {str(parse_error)}")
                    # Fallback: try JSON mode
                    response_payload = self.brain_api.invoke_llm(
                        prompt=prompt,
                        response_format="json_object",
                    )
                    
                    parsed_response = json.loads(response_payload.response)
                    if 'analyses' in parsed_response:
                        for analysis in parsed_response['analyses']:
                            keyword = analysis.get('keyword', '').strip()
                            analysis_text = analysis.get('analysis', '')
                            if keyword:
                                analyses[keyword] = analysis_text
                        print(f"Successfully processed batch with JSON fallback")
                        return analyses
                    else:
                        print(f"JSON response missing 'analyses' key")
                        for data in keyword_batch:
                            analyses[data['keyword']] = "Analysis failed: Invalid response format"
                        return analyses
                
            except Exception as e:
                print(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        # If all attempts failed, return empty analyses
        print(f"Failed to process batch after {self.max_retries} attempts")
        return {data['keyword']: "Analysis failed" for data in keyword_batch}

    def process_keywords_in_batches(self, df: pd.DataFrame) -> Dict[str, str]:
        """Process all keywords in batches"""
        all_analyses = {}
        
        # Prepare keyword data
        keyword_data = []
        for _, row in df.iterrows():
            keyword_data.append({
                'keyword': row['Keyword'],
                'reason': row['Reason_to_Flag'],
                'country_code': row.get('Country_Code', ''),
                'valid_country_codes': row.get('Valid_Country_Codes', ''),
                'country': row.get('Country', ''),
                'compliance_region': row.get('Compliance _Region', '')
            })
        
        # Split into batches
        batches = [keyword_data[i:i + self.batch_size] 
                  for i in range(0, len(keyword_data), self.batch_size)]
        
        print(f"Processing {len(keyword_data)} keywords in {len(batches)} batches")
        
        # Process batches with limited concurrency
        def process_single_batch(batch):
            return self.process_batch_with_brain_api(batch)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            batch_results = list(executor.map(process_single_batch, batches))
        
        # Combine all results
        for batch_result in batch_results:
            all_analyses.update(batch_result)
        
        return all_analyses

    def create_optimized_json_and_csv(self, df: pd.DataFrame, analyses: Dict[str, str]) -> Tuple[Dict, pd.DataFrame]:
        """Create both JSON and CSV structures with country headers"""
        
        # Get unique countries (excluding 'ALL' and NaN values)
        countries = sorted([country for country in df['Country_Code'].unique() 
                          if pd.notna(country) and country != 'ALL'])
        
        # Initialize simple JSON structure with country codes as keys
        json_structure = {}
        
        # Initialize country sections in JSON with empty arrays
        for country in countries:
            json_structure[country] = []
        
        # Add special section for ALL countries
        json_structure["ALL"] = []
        
        # Prepare CSV data
        csv_data = []
        
        # Process ALL countries keywords
        all_countries_df = df[df['Country_Code'] == 'ALL']
        for _, row in all_countries_df.iterrows():
            keyword = row['Keyword']
            reason = row['Reason_to_Flag']
            analysis = analyses.get(keyword, "No analysis available")
            
            # Add keyword to ALL section in JSON
            json_structure["ALL"].append(keyword)
            
            # For CSV, add to data with 'ALL' marked in all country columns
            csv_row = {"Keyword": keyword, "Reason": reason, "Analysis": analysis}
            for country in countries:
                csv_row[country] = "ALL"
            csv_data.append(csv_row)
        
        # Process country-specific keywords (excluding 'ALL' and NaN values)
        country_specific_df = df[(df['Country_Code'] != 'ALL') & (pd.notna(df['Country_Code']))]
        for _, row in country_specific_df.iterrows():
            keyword = row['Keyword']
            reason = row['Reason_to_Flag']
            country = row['Country_Code']
            analysis = analyses.get(keyword, "No analysis available")
            
            # Add keyword to specific country array in JSON
            if country in json_structure:
                json_structure[country].append(keyword)
            
            # For CSV, create row with country marked
            csv_row = {"Keyword": keyword, "Reason": reason, "Analysis": analysis}
            for c in countries:
                csv_row[c] = "YES" if c == country else ""
            csv_data.append(csv_row)
        
        # Create DataFrame for CSV
        csv_df = pd.DataFrame(csv_data)
        
        return json_structure, csv_df

    def process_and_save(self, input_file: str):
        """Main processing function with batching"""
        print("Starting keyword processing with batching...")
        
        # Read the input file
        df = self.read_keywords(input_file)
        print(f"Loaded {len(df)} keywords from {input_file}")
        
        # Process all keywords in batches
        analyses = self.process_keywords_in_batches(df)
        print(f"Completed analysis for {len(analyses)} keywords")
        
        # Create optimized JSON and CSV structures
        json_structure, csv_df = self.create_optimized_json_and_csv(df, analyses)
        
        # Save JSON file
        with open('violation_patterns_optimized.json', 'w', encoding='utf-8') as f:
            json.dump(json_structure, f, indent=2, ensure_ascii=False)
        
        # Save CSV file
        csv_df.to_csv('violation_patterns_optimized.csv', index=False)
        
        # Print statistics
        all_countries_count = len(json_structure["ALL"])
        country_specific_count = sum(len(keywords) for country, keywords in json_structure.items() if country != "ALL")
        
        print("\nProcessing complete! Files generated:")
        print("1. violation_patterns_optimized.json")
        print("2. violation_patterns_optimized.csv")
        print(f"\nStatistics:")
        print(f"- Keywords applicable to ALL countries: {all_countries_count}")
        print(f"- Country-specific keywords: {country_specific_count}")
        print(f"- Countries covered: {list(json_structure.keys())}")

if __name__ == "__main__":
    processor = KeywordProcessor()
    processor.process_and_save('keywords.csv') 