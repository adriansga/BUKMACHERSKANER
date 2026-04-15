import time
import logging
import asyncio
import argparse
from ValueBetScanner.api.odds_fetcher import OddsFetcher
from ValueBetScanner.core.calculator import process_game
from ValueBetScanner.db.database_manager import DatabaseManager
from PROJEKTY.AKTYWNE.skaner-bukmacherow.db.supabase_manager import SupabaseManager
from ValueBetScanner.notifications.notifier import Notifier
from ValueBetScanner.config import settings
from PROJEKTY.AKTYWNE.skaner-bukmacherow.core.betting_bot import STSBettingBot
from PROJEKTY.AKTYWNE.skaner-bukmacherow.core.results_fetcher import ResultsFetcher

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)

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
    results_fetcher = ResultsFetcher()
    
    # Weryfikacja Cloud Sync
    if db_cloud.enabled:
        logging.info("✅ Supabase: Połączenie chmurowe AKTYWNE.")
    else:
        logging.warning("⚠️ Supabase: Brak połączenia chmurowego (sprawdź klucze w .env/Secrets).")
        
    if notifier.bot:
        logging.info("✅ Telegram: Bot AKTYWNY.")
    else:
        logging.warning("⚠️ Telegram: Bot NIEAKTYWNY.")
    
    sports_to_scan = [
        'soccer_poland_ekstraklasa', 
        'soccer_uefa_champs_league', 
        'soccer_england_premier_league', 
        'soccer_germany_bundesliga',
        'soccer_spain_la_liga'
    ]
    
    while True:
        try:
            # 1. SKANOWANIE NOWYCH OKAZJI
            for sport in sports_to_scan:
                logging.info(f"Skanowanie sportu: {sport}")
                data = fetcher.fetch_odds(sport)
                
                if not data:
                    continue
                
                for game in data:
                    opportunities = process_game(game)
                    for opp in opportunities:
                        # Zapisywanie (zwraca True jeśli nowa okazja)
                        is_new_local = db_local.save_opportunity(opp)
                        is_new_cloud = db_cloud.save_opportunity(opp)
                        
                        if is_new_local or is_new_cloud:
                            logging.info(f"NOWA OKAZJA: {opp['game']} | {opp['outcome']} @ {opp['odds']}")
                            await notifier.send_alert(opp)
                            
                            # Betting Bot (tylko jeśli mamy dane logowania)
                            if opp['bookmaker'] == 'STS' and settings.STS_USERNAME != "TWÓJ_LOGIN":
                                try:
                                    bet_bot.setup_driver(headless=True)
                                    if bet_bot.login():
                                        bet_bot.place_bet(opp['game'], opp['outcome'], opp['kelly'])
                                    bet_bot.close()
                                except Exception as e:
                                    logging.error(f"Błąd Betting Bota: {str(e)}")
                
                # Respektujemy limity zapytań
                remaining = fetcher.get_remaining_requests()
                logging.info(f"Pozostało zapytań API: {remaining}")
                await asyncio.sleep(2)

            # 2. SPRAWDZANIE WYNIKÓW (Raz na cykl)
            logging.info("Aktualizacja wyników meczów...")
            for sport in sports_to_scan:
                results_fetcher.fetch_and_update_results(sport)

            if args.once:
                logging.info("Opcja --once aktywna. Zakończono pracę.")
                break

            logging.info(f"Cykl zakończony. Czekam {settings.MIN_POLLING_INTERVAL}s...")
            await asyncio.sleep(settings.MIN_POLLING_INTERVAL)
            
        except Exception as e:
            logging.error(f"Błąd w pętli głównej: {str(e)}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
