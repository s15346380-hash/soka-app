import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# Setup ya ukurasa
st.set_page_config(
    page_title="Uchambuzi wa Soka (Monte Carlo)", page_icon="⚽", layout="wide"
)

st.title("⚽ Dashboard ya Uchambuzi wa Soka (Monte Carlo)")
st.write(
    "Tumia mfumo huu kuigiza matokeo ya mechi kulingana na takwimu za Expected Goals (xG)."
)

# Sidebar kwa ajili ya kuingiza data
st.sidebar.header("⚙️ Mipangilio ya Mechi")

home_team = st.sidebar.text_input("Timu ya Nyumbani (Home)", "Home Team")
away_team = st.sidebar.text_input("Timu ya Ugenini (Away)", "Away Team")

home_xg = st.sidebar.number_input(
    f"xG ya {home_team}", min_value=0.0, max_value=10.0, value=1.5, step=0.1
)
away_xg = st.sidebar.number_input(
    f"xG ya {away_team}", min_value=0.0, max_value=10.0, value=1.1, step=0.1
)

simulations = st.sidebar.slider(
    "Idadi ya Simulations",
    min_value=1000,
    max_value=50000,
    value=10000,
    step=1000,
)

# Monte Carlo Simulation
np.random.seed(42)
home_goals = np.random.poisson(home_xg, simulations)
away_goals = np.random.poisson(away_xg, simulations)

# Kuhesabu matokeo
home_wins = np.sum(home_goals > away_goals)
draws = np.sum(home_goals == away_goals)
away_wins = np.sum(away_goals > home_goals)

home_prob = (home_wins / simulations) * 100
draw_prob = (draws / simulations) * 100
away_prob = (away_wins / simulations) * 100

# Kuhesabu Both Teams to Score (GG / NG)
btts_yes = np.sum((home_goals > 0) & (away_goals > 0))
btts_no = simulations - btts_yes

btts_yes_prob = (btts_yes / simulations) * 100
btts_no_prob = (btts_no / simulations) * 100

# Kuhesabu Implied Odds (1 / Probability)
home_odds = round(100 / home_prob, 2) if home_prob > 0 else 0.0
draw_odds = round(100 / draw_prob, 2) if draw_prob > 0 else 0.0
away_odds = round(100 / away_prob, 2) if away_prob > 0 else 0.0

# Kugawa safu (Columns) kwa Onyesho
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"📊 Uwezekano na Implied Odds: {home_team} vs {away_team}")

    m1, m2, m3 = st.columns(3)
    m1.metric(f"Ushindi wa {home_team}", f"{home_prob:.1f}%", f"Odds: {home_odds}")
    m2.metric("Sare (X)", f"{draw_prob:.1f}%", f"Odds: {draw_odds}")
    m3.metric(f"Ushindi wa {away_team}", f"{away_prob:.1f}%", f"Odds: {away_odds}")

    # Chati ya Matokeo
    results_df = pd.DataFrame(
        {
            "Matokeo": [
                f"Ushindi wa {home_team}",
                "Sare",
                f"Ushindi wa {away_team}",
            ],
            "Uwezekano (%)": [home_prob, draw_prob, away_prob],
        }
    )

    fig = px.bar(
        results_df,
        x="Matokeo",
        y="Uwezekano (%)",
        text="Uwezekano (%)",
        color="Matokeo",
        color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c"],
    )
    fig.update_traces(
        texttemplate="%{text:.1f}%", textposition="outside", showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🎯 Soko la BTTS (GG / NG)")
    b1, b2 = st.columns(2)
    b1.metric("GG (Zote Kufunga)", f"{btts_yes_prob:.1f}%")
    b2.metric("NG (Isiwe GG)", f"{btts_no_prob:.1f}%")

    # Pakua Ripoti ya CSV
    st.subheader("📥 Pakua Ripoti")

    summary_data = pd.DataFrame(
        {
            "Kipengele": [
                f"Ushindi wa {home_team}",
                "Sare (X)",
                f"Ushindi wa {away_team}",
                "GG (Both Teams Score)",
                "NG (No Both Teams Score)",
            ],
            "Uwezekano (%)": [
                round(home_prob, 2),
                round(draw_prob, 2),
                round(away_prob, 2),
                round(btts_yes_prob, 2),
                round(btts_no_prob, 2),
            ],
            "Implied Odds": [
                home_odds,
                draw_odds,
                away_odds,
                (
                    round(100 / btts_yes_prob, 2)
                    if btts_yes_prob > 0
                    else "N/A"
                ),
                round(100 / btts_no_prob, 2) if btts_no_prob > 0 else "N/A",
            ],
        }
    )

    csv = summary_data.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📄 Pakua Ripoti (CSV)",
        data=csv,
        file_name=f"uchambuzi_{home_team}_vs_{away_team}.csv",
        mime="text/csv",
    )

