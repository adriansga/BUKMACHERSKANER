import sqlite3
import logging
from skaner_bukmacherow.config import settings

class DatabaseManager:
    def __init__(self):
        self.db_path = settings.DB_PATH
        self.init_db()

    def init_db(self):
        """Tworzy tabelę jeśli nie istnieje."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS opportunities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    commence_time TEXT,
                    game TEXT,
                    bookmaker TEXT,
                    outcome TEXT,
                    odds REAL,
                    ev REAL,
                    kelly REAL,
                    status TEXT DEFAULT 'pending'
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Błąd bazy danych: {str(e)}")

    def save_opportunity(self, opp):
        """Zapisuje znalezioną okazję."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Sprawdź czy już nie mamy tej samej okazji (duplikaty)
            cursor.execute('''
                SELECT id FROM opportunities 
                WHERE game = ? AND bookmaker = ? AND outcome = ? AND odds = ?
            ''', (opp['game'], opp['bookmaker'], opp['outcome'], opp['odds']))
            
            if cursor.fetchone() is None:
                cursor.execute('''
                    INSERT INTO opportunities (commence_time, game, bookmaker, outcome, odds, ev, kelly)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (opp['commence_time'], opp['game'], opp['bookmaker'], opp['outcome'], opp['odds'], opp['ev'], opp['kelly']))
                conn.commit()
                conn.close()
                return True
            
            conn.close()
            return False
        except Exception as e:
            logging.error(f"Błąd zapisu okazji: {str(e)}")
            return False
