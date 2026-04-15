import os
from dotenv import load_dotenv

# Wczytujemy zmienne z pliku .env
load_dotenv()

# API Keys
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "YOUR_KEY_HERE")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TOKEN_HERE")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID_HERE")

# Stałe rynkowe
MIN_EV_PERCENTAGE = 0.03  # Szukamy min. 3% przewagi
TARGET_BOOKMAKERS = ['betclic', 'unibet', 'bwin', 'sts_pl', 'fortuna', 'betfair_ex', 'williamhill']
PINNACLE_KEY = 'pinnacle' # Klucz Pinnacle w The-Odds-API

# Zarządzanie limitami
BASE_URL = "https://api.the-odds-api.com/v4/sports"
REGIONS = "eu" # Europa dla lokalnych buków
MARKETS = "h2h" # Rynek 1X2
MIN_POLLING_INTERVAL = 60 # Testowo: 1 minuta

# Zarządzanie kapitałem
KELLY_FRACTION = 0.25 # 1/4 Kelly'ego dla bezpieczeństwa
MAX_STAKE_PERCENT = 0.05 # Max 5% bankrollu na jeden zakład

# Ścieżki
DB_PATH = "PROJEKTY/AKTYWNE/SKANER BUKMACHERÓW/db/tracker.db"
LOG_FILE = "PROJEKTY/AKTYWNE/SKANER BUKMACHERÓW/logs/scanner.log"
