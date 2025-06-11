import csv
import json
import os
from openai import OpenAI
from collections import defaultdict
import time

def load_csv_data(filename):
    """Load data from CSV file and organize by country code"""
    country_keywords = defaultdict(list)
    
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            keyword = row['keyword'].strip()
            country_code = row['valid_country_code'].strip()
            
            # Skip empty keywords
            if not keyword:
                continue
                
            # If country code exists, add to that country
            if country_code:
                country_keywords[country_code].append(keyword)
            else:
                # For keywords without country codes, we'll process them separately
                country_keywords['UNASSIGNED'].append(keyword)
    
    return country_keywords

def categorize_keywords_with_openai(keywords_batch, client):
    """Use OpenAI to categorize keywords by language/country"""
    
    # Create prompt for OpenAI
    prompt = f"""
You are a linguistics expert tasked with categorizing keywords by the most likely country/region where they would be used based on language, cultural context, and regulatory patterns.

Please analyze the following keywords and assign each one to the most appropriate country code from this list:
- US (United States - English)
- UK (United Kingdom - English) 
- CA (Canada - English/French)
- AU (Australia - English)
- DE (Germany - German)
- FR (France - French)
- ES (Spain - Spanish)
- IT (Italy - Italian)
- BR (Brazil - Portuguese)
- MX (Mexico - Spanish)
- JP (Japan - Japanese)
- IN (India - English/Hindi)
- CN (China - Chinese)
- RU (Russia - Russian)
- NL (Netherlands - Dutch)
- SE (Sweden - Swedish)
- PL (Poland - Polish)
- TR (Turkey - Turkish)
- SA (Saudi Arabia - Arabic)
- UAE (United Arab Emirates - Arabic/English)
- ALL (Global/Universal terms)

Consider:
1. Language of the keyword
2. Cultural/regulatory context (e.g., FDA vs EMA regulations)
3. Marketing terminology specific to regions
4. Chemical names and medical terms (often universal but may have regional preferences)
5. Slang or colloquial terms
6. Currency symbols or measurements

Keywords to categorize:
{chr(10).join(keywords_batch)}

Please respond with a JSON object where each keyword is a key and the country code is the value. Example:
{{
    "keyword1": "US",
    "keyword2": "DE",
    "keyword3": "ALL"
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Using the best available model
            messages=[
                {"role": "system", "content": "You are a linguistics and regulatory expert specializing in keyword categorization by country/region."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Low temperature for consistency
            max_tokens=4000
        )
        
        # Extract JSON from response
        content = response.choices[0].message.content.strip()
        
        # Find JSON in the response (in case there's extra text)
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        
        if start_idx != -1 and end_idx != -1:
            json_str = content[start_idx:end_idx]
            return json.loads(json_str)
        else:
            print(f"Warning: Could not extract JSON from response: {content[:200]}...")
            return {}
            
    except Exception as e:
        print(f"Error processing batch: {e}")
        return {}

def process_unassigned_keywords(unassigned_keywords, client, batch_size=50):
    """Process keywords that don't have country assignments"""
    categorized = {}
    
    # Process in batches to avoid token limits and rate limits
    for i in range(0, len(unassigned_keywords), batch_size):
        batch = unassigned_keywords[i:i + batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(unassigned_keywords) + batch_size - 1)//batch_size}")
        
        batch_result = categorize_keywords_with_openai(batch, client)
        categorized.update(batch_result)
        
        # Rate limiting - wait between batches
        time.sleep(1)
    
    return categorized

def merge_results(existing_keywords, new_categorizations):
    """Merge existing country-assigned keywords with newly categorized ones"""
    final_result = defaultdict(list)
    
    # Add existing keywords that already had country assignments
    for country_code, keywords in existing_keywords.items():
        if country_code != 'UNASSIGNED':
            final_result[country_code].extend(keywords)
    
    # Add newly categorized keywords
    for keyword, country_code in new_categorizations.items():
        final_result[country_code].append(keyword)
    
    # Convert to regular dict and sort keywords within each country
    final_dict = {}
    for country_code, keywords in final_result.items():
        # Remove duplicates and sort
        unique_keywords = sorted(list(set(keywords)))
        final_dict[country_code] = unique_keywords
    
    return final_dict

def main():
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Load CSV data
    print("Loading CSV data...")
    country_keywords = load_csv_data('Global keywords list.csv')
    
    print(f"Loaded keywords for {len(country_keywords)} categories")
    print(f"Keywords without country assignment: {len(country_keywords.get('UNASSIGNED', []))}")
    
    # Process unassigned keywords using OpenAI
    unassigned_keywords = country_keywords.get('UNASSIGNED', [])
    if unassigned_keywords:
        print(f"Processing {len(unassigned_keywords)} unassigned keywords with OpenAI...")
        new_categorizations = process_unassigned_keywords(unassigned_keywords, client)
    else:
        new_categorizations = {}
    
    # Merge results
    print("Merging results...")
    final_result = merge_results(country_keywords, new_categorizations)
    
    # Save to JSON file
    output_filename = 'violation_patterns.json'
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(final_result, f, indent=2, ensure_ascii=False)
    
    print(f"Results saved to {output_filename}")
    print(f"Total countries: {len(final_result)}")
    for country, keywords in final_result.items():
        print(f"  {country}: {len(keywords)} keywords")

if __name__ == "__main__":
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("Please set your OPENAI_API_KEY environment variable")
        print("You can set it by running: export OPENAI_API_KEY='your-api-key-here'")
        exit(1)
    
    main()
