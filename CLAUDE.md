# CLAUDE.md - ValueBet Scanner & Betting Bot

## 📝 PROJEKT: skaner-bukmacherow (ValueBet & Surebet)
Automatyczny system skanujący rynki sportowe (The-Odds-API), porównujący kursy z Pinnacle (True Probability) i wykrywający okazje Expected Value (EV) u lokalnych bukmacherów (STS, Fortuna, etc.).

---

## 🏗️ ARCHITEKTURA (Mapa projektu)
- `/api/odds_fetcher.py` - Komunikacja z The-Odds-API (H2H, 1X2).
- `/core/calculator.py` - Silnik matematyczny (Shin Margin Removal, EV, Kelly Criterion).
- `/core/betting_bot.py` - Automatyzacja przeglądarki (Selenium) do stawiania zakładów w STS.
- `/db/supabase_manager.py` - Integracja z bazą danych Supabase (Cloud Sync).
- `/db/database_manager.py` - Lokalna baza SQLite (Backup).
- `/notifications/notifier.py` - Integracja z Telegramem (Alerty 24/7).
- `/dashboard.py` - Interfejs webowy (Streamlit).
- `main.py` - Główny silnik (Daemon/GitHub Actions).

---

## 🚀 KOMENDY STARTOWE
- `python main.py` - Uruchomienie skanera lokalnie (pętla).
- `python main.py --once` - Jeden skan (używane w GitHub Actions).
- `streamlit run dashboard.py` - Uruchomienie dashboardu.
- `./deploy.sh` - Automatyczny push zmian na GitHub (Vibe Coding).

---

## 🔒 WYMAGANE KLUCZE (Environment Variables / Secrets)
Aby system działał w chmurze (GitHub/Vercel), muszą być ustawione te klucze:
1. `ODDS_API_KEY` - Klucz z the-odds-api.com.
2. `TELEGRAM_BOT_TOKEN` - Token od @BotFather.
3. `TELEGRAM_CHAT_ID` - Twoje ID z @userinfobot (8792648650).
4. `SUPABASE_URL` - URL projektu (fojdukxqzvwpoagktysu.supabase.co).
5. `SUPABASE_KEY` - Service Role Key (sb_secret_...).
6. `STS_USERNAME` - Twój login do STS.
7. `STS_PASSWORD` - Twoje hasło do STS.

---

## 💡 ZASADY ROZWOJU (Dla AI)
1. **Pinnacle to Wyrocznia:** Zawsze używaj kursów Pinnacle do obliczania True Prob.
2. **Bezpieczeństwo Kapitału:** Stawki zawsze obliczaj ułamkowym Kellym (0.25).
3. **Fuzzy Matching:** Nazwy zespołów dopasowuj biblioteką `thefuzz` (min 80% dopasowania).
4. **Cloud First:** Priorytetem jest zapis do Supabase i powiadomienia na Telegram.
5. **Vibe Coding:** Po każdej zmianie wykonaj `./deploy.sh`, aby zaktualizować GitHub i Vercel.

---

## 🚀 TODO DLA KOLEJNYCH AGENTÓW (Priorytety):
1. **[ ] Results Fetcher:** Dodać moduł sprawdzający wyniki meczów i aktualizujący status w Supabase (win/loss).
2. **[ ] Surebet Engine:** Dodać wykrywanie arbitrażu międzbukmacherskiego.
3. **[ ] STS Verification:** Po wpisaniu hasła przez Adriana, przetestować logowanie i przygotowanie kuponu "na żywo".
4. **[ ] Vercel Polish:** Przetłumaczyć dashboard na polski i dodać wykresy realnego zysku.
