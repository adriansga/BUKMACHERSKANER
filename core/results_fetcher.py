import requests
import logging
from PROJEKTY.AKTYWNE.skaner_bukmacherow.config import settings
from PROJEKTY.AKTYWNE.skaner_bukmacherow.db.supabase_manager import SupabaseManager

class ResultsFetcher:
    def __init__(self):
        self.api_key = settings.ODDS_API_KEY
        self.base_url = settings.BASE_URL
        self.db = SupabaseManager()

    def fetch_and_update_results(self, sport="soccer_poland_ekstraklasa"):
        """Pobiera wyniki dla sportu i aktualizuje bazę."""
        url = f"{self.base_url}/{sport}/scores/"
        params = {
            'apiKey': self.api_key,
            'daysFrom': 3 # Sprawdzaj wyniki z ostatnich 3 dni
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                return
                
            scores = response.json()
            for score in scores:
                if score['completed']:
                    self.process_completed_game(score)
        except Exception as e:
            logging.error(f"Błąd pobierania wyników: {str(e)}")

    def process_completed_game(self, score):
        """Analizuje wynik i aktualizuje statusy w DB."""
        game_name = f"{score['home_team']} vs {score['away_team']}"
        
        # Wyznacz wynik (1, X, 2)
        home_score = int(score['scores'][0]['score'])
        away_score = int(score['scores'][1]['score'])
        
        if home_score > away_score:
            winner = "Home"
        elif away_score > home_score:
            winner = "Away"
        else:
            winner = "Draw"
            
        logging.info(f"Mecz zakończony: {game_name} | Wynik: {home_score}:{away_score} ({winner})")
        
        # Aktualizacja w Supabase (wszystkie zakłady na ten mecz)
        # Status 'won' dla trafionych, 'lost' dla nietrafionych
        try:
            # Zakłady wygrane
            self.db.client.table("opportunities")\
                .update({"status": "won"})\
                .eq("game", game_name)\
                .eq("outcome", winner)\
                .execute()
            
            # Zakłady przegrane
            self.db.client.table("opportunities")\
                .update({"status": "lost"})\
                .eq("game", game_name)\
                .neq("outcome", winner)\
                .execute()
        except Exception as e:
            logging.error(f"Błąd aktualizacji statusów wyników: {str(e)}")
