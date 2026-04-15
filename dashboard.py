import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from skaner_bukmacherow.config import settings
import os

# Konfiguracja strony
st.set_page_config(page_title="ValueBet Scanner Dashboard", layout="wide")

st.title("🚨 ValueBet Scanner - Real-time Dashboard")

def load_data():
    if not os.path.exists(settings.DB_PATH):
        return pd.DataFrame()
    
    conn = sqlite3.connect(settings.DB_PATH)
    query = "SELECT * FROM opportunities ORDER BY timestamp DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Sidebar z filtrami
st.sidebar.header("Filtry")
min_ev = st.sidebar.slider("Minimalne EV (%)", 0.0, 20.0, 3.0)
selected_bookmakers = st.sidebar.multiselect(
    "Wybierz bukmacherów", 
    options=['STS', 'Fortuna', 'Betclic', 'Unibet', 'Bwin', 'Betfair', 'William Hill'],
    default=['STS', 'Fortuna', 'Betclic']
)

# Ładowanie danych
df = load_data()

if df.empty:
    st.warning("Baza danych jest pusta lub jeszcze nie została utworzona. Uruchom skaner (main.py), aby zacząć zbierać dane.")
else:
    # Filtrowanie
    df_filtered = df[(df['ev'] >= min_ev)]
    
    # Statystyki na górze
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Wszystkie okazje", len(df))
    with col2:
        st.metric("Średnie EV", f"{df['ev'].mean():.2f}%")
    with col3:
        st.metric("Najwyższe EV", f"{df['ev'].max():.2f}%")
    with col4:
        st.metric("Ostatnia aktualizacja", df['timestamp'].iloc[0])

    # Główna tabela
    st.subheader("🔥 Aktywne okazje")
    st.dataframe(df_filtered[['timestamp', 'game', 'outcome', 'odds', 'bookmaker', 'ev', 'kelly']].style.highlight_max(subset=['ev'], color='lightgreen'), use_container_width=True)

    # Wykresy
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Rozkład EV")
        fig_hist = px.histogram(df, x="ev", nbins=20, title="Liczba okazji per poziom EV")
        st.plotly_chart(fig_hist, use_container_width=True)
        
    with col_chart2:
        st.subheader("Okazje per Bukmacher")
        bookie_counts = df['bookmaker'].value_counts().reset_index()
        bookie_counts.columns = ['bookmaker', 'count']
        fig_pie = px.pie(bookie_counts, values='count', names='bookmaker', title="Gdzie najczęściej pojawia się Value?")
        st.plotly_chart(fig_pie, use_container_width=True)

    # Historia czasowa
    st.subheader("📈 Trend pojawiania się okazji")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df_trend = df.resample('H', on='timestamp').count().rename(columns={'id': 'Liczba okazji'}).reset_index()
    fig_line = px.line(df_trend, x='timestamp', y='Liczba okazji', title="Liczba znalezionych okazji w czasie (per godzina)")
    st.plotly_chart(fig_line, use_container_width=True)

# Przycisk odświeżania
if st.button('Odśwież dane'):
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("Skaner używa Pinnacle jako wyznacznika True Probability. Dashboard odświeża się po kliknięciu przycisku lub zmianie filtrów.")
