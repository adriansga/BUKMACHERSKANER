import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PROJEKTY.AKTYWNE.skanerbukmacherow.config import settings
import os

class STSBettingBot:
    def __init__(self):
        self.username = os.getenv("STS_USERNAME")
        self.password = os.getenv("STS_PASSWORD")
        self.driver = None

    def setup_driver(self, headless=True):
        options = Options()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def login(self):
        """Logowanie do STS."""
        try:
            self.driver.get("https://www.sts.pl/")
            # Kliknij "Zaloguj"
            wait = WebDriverWait(self.driver, 10)
            login_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn-login")))
            login_btn.click()
            
            # Wpisz dane (jeśli hasło nie jest domyślne)
            if self.username != "TWÓJ_LOGIN" and self.password != "TWOJE_HASŁO":
                user_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
                pass_input = self.driver.find_element(By.NAME, "password")
                
                user_input.send_keys(self.username)
                pass_input.send_keys(self.password)
                self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
                logging.info("Zalogowano pomyślnie do STS.")
                return True
            else:
                logging.warning("Brak danych logowania do STS. Logowanie pominięte (tryb symulacji).")
                return False
        except Exception as e:
            logging.error(f"Błąd logowania STS: {str(e)}")
            return False

from thefuzz import fuzz

    def place_bet(self, game_name, outcome_name, stake):
        """
        Logika stawiania zakładu na STS z inteligentnym dopasowaniem i wyborem kursu.
        """
        try:
            logging.info(f"Proces STS: Szukam meczu '{game_name}' dla typu '{outcome_name}'")
            
            # 1. Mapowanie typu zakładu na pozycję przycisku (0=1, 1=X, 2=2)
            outcome_map = {"Home": 0, "Draw": 1, "Away": 2}
            # Jeśli nazwy w API są inne, robimy mapowanie pomocnicze
            if outcome_name not in outcome_map:
                # Prosta heurystyka dla nazw zespołów
                if "draw" in outcome_name.lower() or outcome_name.lower() == "x":
                    target_idx = 1
                elif game_name.split(" vs ")[0] in outcome_name:
                    target_idx = 0
                else:
                    target_idx = 2
            else:
                target_idx = outcome_map[outcome_name]
            
            # 2. Szukaj meczu w STS
            search_query = game_name.split(" vs ")[0]
            self.driver.get(f"https://www.sts.pl/szukaj/?q={search_query}")
            wait = WebDriverWait(self.driver, 10)
            
            # 3. Wybierz najlepszy wynik
            results = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".search-results .event-row")))
            best_match = None
            highest_score = 0
            
            for res in results:
                score = fuzz.partial_ratio(game_name, res.text)
                if score > highest_score and score > 80:
                    highest_score = score
                    best_match = res
            
            if not best_match:
                logging.error(f"Nie znaleziono meczu '{game_name}' w STS.")
                return False
                
            best_match.click()
            
            # 4. Wybierz kurs (1, X, 2)
            # W STS na stronie meczu główne kursy są w sekcji .bet-btns lub podobnej
            # Wybieramy przycisk na podstawie indeksu (target_idx)
            odds_buttons = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".bet-btn")))
            
            if len(odds_buttons) >= 3:
                logging.info(f"Klikam w kurs: {target_idx} (Typ: {outcome_name})")
                odds_buttons[target_idx].click()
                
                # 5. Wpisz stawkę w kuponie (pojawia się po kliknięciu kursu)
                time.sleep(2) # Czekamy na animację kuponu
                stake_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.coupon-stake-input")))
                stake_input.clear()
                stake_input.send_keys(str(stake))
                
                logging.info(f"✅ KUPON PRZYGOTOWANY: {game_name} | Typ: {outcome_name} | Stawka: {stake}")
                
                # 6. POTWIERDZENIE (TYLKO DLA CIEBIE DO ODBLOKOWANIA)
                # if settings.REAL_BETTING_ENABLED:
                #     self.driver.find_element(By.CSS_SELECTOR, ".place-bet-button").click()
                
                return True
            else:
                logging.error("Nie znaleziono przycisków kursu na stronie meczu.")
                return False
            
        except Exception as e:
            logging.error(f"Błąd Betting Bota na STS: {str(e)}")
            return False

    def close(self):
        if self.driver:
            self.driver.quit()
