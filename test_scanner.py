import sys
import os

# Dodaj główny katalog projektu do PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skaner-bukmacherow.core.calculator import remove_margin, calculate_ev, calculate_kelly, process_game

def test_math_logic():
    print("--- TEST LOGIKI MATEMATYCZNEJ ---")
    
    # 1. Test Pinnacle Margin Removal
    # Przykład: 1.95 | 3.40 | 4.10
    pinnacle_odds = [1.95, 3.40, 4.10]
    true_probs = remove_margin(pinnacle_odds)
    print(f"Kursy Pinnacle: {pinnacle_odds}")
    print(f"True Probabilities: {true_probs}")
    print(f"Suma Prob (powinna być 1.0): {sum(true_probs)}")
    
    # 2. Test EV
    # Jeśli True Prob wygranej to 0.48, a buk daje 2.20
    true_win_prob = true_probs[0]
    local_odds = 2.20
    ev = calculate_ev(true_win_prob, local_odds)
    print(f"Local Odds: {local_odds} | True Prob: {true_win_prob:.4f}")
    print(f"Obliczone EV: {ev*100:.2f}%")
    
    # 3. Test Kelly
    kelly = calculate_kelly(ev, local_odds)
    print(f"Kelly Stake (z ułamkiem i capem): {kelly}%")

def test_process_game():
    print("\n--- TEST PRZETWARZANIA MECZU (MOCK DATA) ---")
    mock_game = {
        'home_team': 'Legia Warszawa',
        'away_team': 'Lech Poznań',
        'commence_time': '2026-04-20T20:00:00Z',
        'bookmakers': [
            {
                'key': 'pinnacle',
                'title': 'Pinnacle',
                'markets': [{
                    'key': 'h2h',
                    'outcomes': [
                        {'name': 'Legia Warszawa', 'price': 2.0},
                        {'name': 'Lech Poznań', 'price': 3.5},
                        {'name': 'Draw', 'price': 3.5}
                    ]
                }]
            },
            {
                'key': 'sts_pl',
                'title': 'STS',
                'markets': [{
                    'key': 'h2h',
                    'outcomes': [
                        {'name': 'Legia Warszawa', 'price': 2.30}, # To jest VALUE!
                        {'name': 'Lech Poznań', 'price': 3.2},
                        {'name': 'Draw', 'price': 3.2}
                    ]
                }]
            }
        ]
    }
    
    # Konfiguracja tymczasowa dla testu
    import skaner-bukmacherow.config.settings as settings
    settings.TARGET_BOOKMAKERS = ['sts_pl']
    
    opps = process_game(mock_game)
    for o in opps:
        print(f"ZNALEZIONO: {o['game']} | {o['outcome']} @ {o['odds']} | EV: {o['ev']}% | Kelly: {o['kelly']}%")

if __name__ == "__main__":
    test_math_logic()
    test_process_game()
