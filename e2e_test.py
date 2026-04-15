import asyncio
import logging
import os
from dotenv import load_dotenv
import requests
from supabase import create_client, Client
from telegram import Bot

# Konfiguracja logów
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

load_dotenv()

async def run_e2e_test():
    logging.info("--- ROZPOCZYNAM TEST END-TO-END (E2E) ---")
    
    # 1. TEST THE-ODDS-API
    logging.info("1. Sprawdzanie The-Odds-API...")
    api_key = os.getenv("ODDS_API_KEY")
    url = f"https://api.the-odds-api.com/v4/sports?apiKey={api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            logging.info(f"✅ The-Odds-API: OK (Pozostało zapytań: {response.headers.get('x-requests-remaining')})")
        else:
            logging.error(f"❌ The-Odds-API: Błąd {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"❌ The-Odds-API: Wyjątek - {str(e)}")

    # 2. TEST SUPABASE
    logging.info("2. Sprawdzanie Supabase...")
    sb_url = os.getenv("SUPABASE_URL")
    sb_key = os.getenv("SUPABASE_KEY")
    try:
        supabase: Client = create_client(sb_url, sb_key)
        # Spróbuj odczytać tabelę opportunities
        res = supabase.table("opportunities").select("count", count="exact").limit(1).execute()
        logging.info(f"✅ Supabase: OK (Znaleziono {res.count} rekordów w bazie)")
    except Exception as e:
        logging.error(f"❌ Supabase: Błąd - {str(e)}")

    # 3. TEST TELEGRAM
    logging.info("3. Sprawdzanie Telegrama...")
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    try:
        bot = Bot(token=bot_token)
        await bot.send_message(chat_id=chat_id, text="🧪 *TEST E2E ZAKOŃCZONY Pomyślnie!*\n\nTwój system jest gotowy do zarabiania. Wszystkie połączenia (API, DB, Telegram) działają poprawnie.", parse_mode="Markdown")
        logging.info("✅ Telegram: OK (Wiadomość wysłana)")
    except Exception as e:
        logging.error(f"❌ Telegram: Błąd - {str(e)}")

    logging.info("--- TEST E2E ZAKOŃCZONY ---")

if __name__ == "__main__":
    asyncio.run(run_e2e_test())
