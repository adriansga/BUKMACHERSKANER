import time
import logging
import asyncio
from ValueBetScanner.api.odds_fetcher import OddsFetcher
from ValueBetScanner.core.calculator import process_game
from ValueBetScanner.db.database_manager import DatabaseManager
from ValueBetScanner.notifications.notifier import Notifier
from ValueBetScanner.config import settings

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)

import argparse
from PROJEKTY.AKTYWNE.SKANER BUKMACHERÓW.db.supabase_manager import SupabaseManager

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Wykonaj jeden skan i wyjdź")
    args = parser.parse_args()

    logging.info("--- SKANER VALUE BETÓW URUCHOMIONY ---")
    
    fetcher = OddsFetcher()
    db_local = DatabaseManager()
    db_cloud = SupabaseManager()
    notifier = Notifier()
    bet_bot = STSBettingBot()
    
    sports_to_scan = [
        'soccer_poland_ekstraklasa', 'soccer_uefa_champs_league', 
        'soccer_england_premier_league', 'soccer_germany_bundesliga'
    ]
    
    while True:
        try:
            for sport in sports_to_scan:
                data = fetcher.fetch_odds(sport)
                if not data: continue
                
                for game in data:
                    opportunities = process_game(game)
                    for opp in opportunities:
                        # Zapis lokalny
                        new_local = db_local.save_opportunity(opp)
                        # Zapis chmurowy
                        new_cloud = db_cloud.save_opportunity(opp)
                        
                        if new_local or new_cloud:
                            await notifier.send_alert(opp)
                            if opp['bookmaker'] == 'STS' and settings.STS_USERNAME != "TWÓJ_LOGIN":
                                try:
                                    bet_bot.setup_driver(headless=True)
                                    if bet_bot.login():
                                        bet_bot.place_bet(opp['game'], opp['outcome'], opp['kelly'])
                                    bet_bot.close()
                                except Exception as e:
                                    logging.error(f"Błąd Betting Bota: {str(e)}")
            
            if args.once:
                logging.info("Opcja --once aktywna. Zakończono skanowanie.")
                break

            logging.info("Koniec cyklu. Czekam 60 sekund...")
            await asyncio.sleep(60) 
                
                # Respektujemy limity zapytań
                remaining = fetcher.get_remaining_requests()
                logging.info(f"Pozostało zapytań API: {remaining}")
                
                # Krótka pauza między sportami
                await asyncio.sleep(5)
            
            # Główna pauza pętli - ZMNIEJSZONA DLA TESTÓW (Częste odświeżanie)
            logging.info("Koniec cyklu. Czekam 60 sekund...")
            await asyncio.sleep(60) 
            
        except Exception as e:
            logging.error(f"Błąd w pętli głównej: {str(e)}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
