"""
Brain API client for keyword categorization.
"""

import os
import requests
from typing import Dict, Optional, List

class BrainClient:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Brain API client.
        
        Args:
            api_key: The API key for authentication. If not provided, will try to get from environment.
        """
        self.api_key = api_key or os.getenv('BRAIN_API_KEY')
        if not self.api_key:
            raise ValueError("API key must be provided either directly or through BRAIN_API_KEY environment variable")
        
        self.base_url = "https://api.brain.com/v1"  # Replace with actual API endpoint
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def categorize_keyword(self, keyword: str, country_code: Optional[str] = None) -> Dict:
        """Categorize a keyword for a specific country.
        
        Args:
            keyword: The keyword to categorize
            country_code: Optional country code for country-specific categorization
            
        Returns:
            Dict containing category and confidence score
        """
        # TODO: Implement actual API call
        # For now, return a mock response
        return {
            "category": "general",
            "confidence": 0.95
        }
    
    def get_supported_countries(self) -> List[str]:
        """Get list of supported countries.
        
        Returns:
            List of country codes
        """
        # TODO: Implement actual API call
        # For now, return a mock list
        return ["US", "UK", "CA", "AU", "DE", "FR", "ES", "IT"] 