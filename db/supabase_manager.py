import logging
import os
from supabase import create_client, Client
from PROJEKTY.AKTYWNE.SKANER BUKMACHERÓW.config import settings

class SupabaseManager:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.enabled = self.url and self.key and "YOUR_" not in self.url
        
        if self.enabled:
            try:
                self.client: Client = create_client(self.url, self.key)
                logging.info("Połączono z Supabase (Cloud DB).")
            except Exception as e:
                logging.error(f"Błąd połączenia Supabase: {str(e)}")
                self.enabled = False

    def save_opportunity(self, opp):
        """Zapisuje okazję do Supabase."""
        if not self.enabled:
            return False
            
        try:
            data = {
                "commence_time": opp["commence_time"],
                "game": opp["game"],
                "bookmaker": opp["bookmaker"],
                "outcome": opp["outcome"],
                "odds": opp["odds"],
                "ev": opp["ev"],
                "kelly": opp["kelly"],
                "status": "pending"
            }
            
            # W Supabase używamy UPSERT lub INSERT
            # Sprawdzamy czy już nie istnieje (game+bookmaker+outcome+odds)
            self.client.table("opportunities").upsert(data, on_conflict="game,bookmaker,outcome,odds").execute()
            return True
        except Exception as e:
            logging.error(f"Błąd zapisu Supabase: {str(e)}")
            return False
