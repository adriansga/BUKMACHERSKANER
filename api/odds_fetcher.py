import requests
import time
import logging
from config import settings

class OddsFetcher:
    def __init__(self):
        self.api_key = settings.ODDS_API_KEY
        self.base_url = settings.BASE_URL
        self.requests_remaining = 500 # Default fallback

    def fetch_odds(self, sport="soccer_poland_extraklasa"):
        """Pobiera kursy dla danego sportu."""
        url = f"{self.base_url}/{sport}/odds/"
        params = {
            'apiKey': self.api_key,
            'regions': settings.REGIONS,
            'markets': settings.MARKETS,
            'oddsFormat': 'decimal'
        }
        
        try:
            response = requests.get(url, params=params)
            
            # Aktualizacja liczników na podstawie nagłówków API
            self.requests_remaining = int(response.headers.get('x-requests-remaining', self.requests_remaining))
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                logging.warning("Rate limit przekroczony. Czekam...")
                return None
            else:
                logging.error(f"Błąd API: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Wyjątek podczas pobierania kursów: {str(e)}")
            return None

    def get_remaining_requests(self):
        return self.requests_remaining
