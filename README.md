# Keyword Compliance Analysis System

A Python-based system that processes and analyzes compliance-related keywords using AI, organizing them by country and providing detailed analysis.

## Overview

This system takes a list of flagged keywords and their compliance information, processes them through an AI analysis pipeline, and generates structured outputs for compliance checking across different international markets.

## Features

- **AI-Powered Analysis**: Uses Brain API for intelligent keyword analysis
- **Batch Processing**: Efficiently processes keywords in batches of 10
- **Parallel Processing**: Uses ThreadPoolExecutor for improved performance
- **Error Handling**: Includes retry logic and fallback mechanisms
- **International Compliance**: Organizes keywords by country/region
- **Structured Outputs**: Generates both JSON and CSV formats

## Prerequisites

- Python 3.x
- Brain API client (`brain_platform_client`)
- Required Python packages (install via pip):
  ```
  pip install pandas
  python-dotenv
  pydantic
  brain-platform-client
  ```

## Installation

1. Clone the repository:
   ```bash
   git clone [repository-url]
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file with:
   ```
   BRAIN_API_KEY=your_api_key_here
   ```

## Usage

1. Prepare your input file:
   - Create a CSV file named `keywords.csv`
   - Required columns: 
     - `Keyword`
     - `Reason_to_Flag`
     - `Country_Code`
     - `Valid_Country_Codes`
     - `Country`
     - `Compliance_Region`

2. Run the processor:
   ```bash
   python process_keywords.py
   ```

## Output Files

### 1. JSON Output (`violation_patterns_optimized.json`)
```json
{
  "US": ["keyword1", "keyword2"],
  "UK": ["keyword3", "keyword4"],
  "ALL": ["global_keyword1", "global_keyword2"]
}
```

### 2. CSV Output (`violation_patterns_optimized.csv`)
A detailed spreadsheet containing:
- Keyword information
- Reasons for flagging
- AI analysis
- Country-specific applicability

## Code Structure

- `process_keywords.py`: Main processing script
  - `KeywordProcessor`: Main class handling the processing
  - `KeywordAnalysis`: Pydantic model for structured responses
  - Batch processing and analysis functions

## Processing Flow

1. **Input Processing**
   - Reads keywords.csv
   - Validates input data
   - Handles missing values and data cleanup

2. **AI Analysis**
   - Batches keywords for efficient processing
   - Sends to Brain API for analysis
   - Handles structured responses and fallbacks

3. **Output Generation**
   - Creates country-organized JSON
   - Generates detailed CSV with analysis
   - Handles special cases (ALL countries, region-specific)

## Statistics

The system processes:
- ~10,000+ keywords
- Multiple country codes
- Global and region-specific patterns
- Compliance reasons and analysis

## Error Handling

- Retry mechanism for API calls
- Fallback to JSON mode if structured output fails
- NaN value handling in country codes
- Invalid data filtering

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request



