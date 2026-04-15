import logging
from config import settings

def remove_margin(odds_list):
    """
    Zdejmuje marżę za pomocą metody proporcjonalnej.
    odds_list: lista kursów [1, X, 2]
    Zwraca: listę prawdopodobieństw (True Probabilities) sumujących się do 1.0.
    """
    try:
        if not odds_list or any(o <= 0 for o in odds_list):
            return None
            
        implied_probs = [1/o for o in odds_list]
        margin_sum = sum(implied_probs)
        
        # Proportional Margin Method (Shin/Multiplicative)
        true_probs = [p / margin_sum for p in implied_probs]
        return true_probs
    except Exception as e:
        logging.error(f"Błąd podczas usuwania marży: {str(e)}")
        return None

def calculate_ev(true_prob, local_odds):
    """Oblicza Expected Value (EV)."""
    return (true_prob * local_odds) - 1

def calculate_kelly(ev, local_odds, bankroll=1000):
    """Oblicza ułamkową stawkę Kelly'ego."""
    if ev <= 0:
        return 0
    
    # Kelly % = (((B * P) - Q) / B) gdzie B = (odds - 1)
    kelly_full = (ev / (local_odds - 1))
    kelly_fractional = kelly_full * settings.KELLY_FRACTION
    
    # Zabezpieczenie: Max stake
    stake_percent = min(kelly_fractional, settings.MAX_STAKE_PERCENT)
    return round(stake_percent * 100, 2) # Zwraca % bankrollu

def process_game(game_data):
    """
    Analizuje dane jednego meczu w poszukiwaniu Value Betów.
    """
    opportunities = []
    bookmakers = game_data.get('bookmakers', [])
    pinnacle_odds = None
    
    # 1. Znajdź kursy Pinnacle
    for bm in bookmakers:
        if bm['key'] == settings.PINNACLE_KEY:
            # Zakładamy rynek H2H (1X2)
            for market in bm['markets']:
                if market['key'] == 'h2h':
                    pinnacle_odds = {outcome['name']: outcome['price'] for outcome in market['outcomes']}
                    break
            break
    
    if not pinnacle_odds:
        return [] # Brak Pinnacle = brak True Prob

    # 2. Oblicz True Prob z Pinnacle (zakładając standardową kolejność 1, X, 2 lub 1, 2)
    outcomes = list(pinnacle_odds.keys())
    odds_values = [pinnacle_odds[o] for o in outcomes]
    true_probs_list = remove_margin(odds_values)
    
    if not true_probs_list:
        return []
        
    true_probs = dict(zip(outcomes, true_probs_list))

    # 3. Szukaj value u lokalnych bukmacherów
    for bm in bookmakers:
        if bm['key'] == settings.PINNACLE_KEY or bm['key'] not in settings.TARGET_BOOKMAKERS:
            continue
            
        for market in bm['markets']:
            if market['key'] == 'h2h':
                for outcome in market['outcomes']:
                    name = outcome['name']
                    price = outcome['price']
                    
                    if name in true_probs:
                        ev = calculate_ev(true_probs[name], price)
                        
                        if ev >= settings.MIN_EV_PERCENTAGE:
                            kelly_stake = calculate_kelly(ev, price)
                            
                            opportunities.append({
                                'game': f"{game_data['home_team']} vs {game_data['away_team']}",
                                'commence_time': game_data['commence_time'],
                                'bookmaker': bm['title'],
                                'outcome': name,
                                'odds': price,
                                'ev': round(ev * 100, 2),
                                'kelly': kelly_stake
                            })
    
    return opportunities
