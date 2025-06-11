# Keyword Categorization System

An AI-powered system that automatically categorizes pharmaceutical/medical keywords by country/region using OpenAI's GPT-4 model.

## Overview

This system takes a large CSV file containing pharmaceutical/medical keywords (many with violation patterns) and organizes them by appropriate countries based on language, regulatory context, and cultural usage patterns.

## What It Does

The system analyzes keywords and assigns them to the most appropriate country/region considering:

- **Language** (English, German, French, Spanish, etc.)
- **Regulatory context** (FDA vs EMA regulations)
- **Cultural/marketing terminology**
- **Medical/chemical terms** (often universal)
- **Regional slang or colloquialisms**

## Features

- **AI-Powered Analysis**: Uses OpenAI's GPT-4o model for intelligent categorization
- **Batch Processing**: Handles thousands of keywords efficiently with rate limiting
- **Multi-Country Support**: Categorizes for 20+ countries and regions
- **Duplicate Handling**: Automatically removes duplicates and sorts results
- **JSON Output**: Clean, structured output format

## Supported Countries/Regions

- **US** (United States - English)
- **UK** (United Kingdom - English)
- **CA** (Canada - English/French)
- **AU** (Australia - English)
- **DE** (Germany - German)
- **FR** (France - French)
- **ES** (Spain - Spanish)
- **IT** (Italy - Italian)
- **BR** (Brazil - Portuguese)
- **MX** (Mexico - Spanish)
- **JP** (Japan - Japanese)
- **IN** (India - English/Hindi)
- **CN** (China - Chinese)
- **RU** (Russia - Russian)
- **NL** (Netherlands - Dutch)
- **SE** (Sweden - Swedish)
- **PL** (Poland - Polish)
- **TR** (Turkey - Turkish)
- **SA** (Saudi Arabia - Arabic)
- **UAE** (United Arab Emirates - Arabic/English)
- **ALL** (Global/Universal terms)

## Input Data Format

The system expects a CSV file (`Global keywords list.csv`) with the following columns:
- `keyword`: The keyword to categorize
- `valid_country_code`: Existing country code (if any)
- `country`: Country name (for reference)

### Example Keywords
- Medical codes: `14500`, `16340`, `18650`
- Chemical compounds: `1-(2-Chloroethyl)-3-(4-methylcyclohexyl)-1-nitrosourea`
- Marketing terms: `[100%] Satisfaction Guaranteed`, `*FREE DELIVERY*`
- Drug names: `2 Day Diet - sibutramine`

## Setup & Installation

### Prerequisites
- Python 3.8 or higher
- OpenAI API key

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd keyword-categorizer
   ```

2. **Set up your OpenAI API key**
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

3. **Run the setup script**
   ```bash
   python run_setup.py
   ```

### Manual Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the main script**
   ```bash
   python main.py
   ```

## How It Works

1. **Data Loading**: Reads keywords from `Global keywords list.csv`
2. **Preprocessing**: Organizes keywords by existing country codes
3. **AI Analysis**: Uses OpenAI GPT-4o to categorize unassigned keywords
4. **Batch Processing**: Processes keywords in batches of 50 with rate limiting
5. **Output Generation**: Merges results and saves to `violation_patterns.json`

## Output

The system generates `violation_patterns.json` containing:
- Keywords organized by country code
- Alphabetically sorted within each country
- Deduplicated entries
- Clean, structured JSON format

## Configuration

- **Batch Size**: 50 keywords per API call (configurable in `main.py`)
- **Rate Limiting**: 1-second delay between batches
- **Model**: GPT-4o (best available model for accuracy)
- **Temperature**: 0.1 (low for consistency)

## Use Cases

This tool is particularly useful for:
- **Regulatory Compliance**: Understanding which keywords might trigger violations in different countries
- **Content Localization**: Adapting marketing materials for specific regions
- **Pharmaceutical Marketing**: Complying with country-specific advertising regulations
- **Medical Content Review**: Categorizing medical terminology by regional usage

## Files Structure

- `main.py`: Core categorization logic
- `run_setup.py`: Setup and installation script
- `Global keywords list.csv`: Input data (10,099+ keywords)
- `violation_patterns.json`: Output file (categorized keywords)
- `pyproject.toml`: Project configuration
- `requirements.txt`: Python dependencies

## API Usage

The system uses OpenAI's Chat Completions API with:
- Model: `gpt-4o`
- Temperature: `0.1`
- Max tokens: `4000`
- Role-based prompting for linguistic expertise

## Error Handling

- Graceful handling of API failures
- Batch retry logic
- JSON parsing validation
- Missing API key detection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Add your license information here]

## Support

For issues or questions, please [create an issue](link-to-issues) in the repository. 