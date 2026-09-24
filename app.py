import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# Mipangilio ya Ukurasa
st.set_page_config(
    page_title="Monte Carlo Soccer Engine", page_icon="⚽", layout="wide"
)

# Custom CSS kufanya mwonekano ufanane na kadi za kwenye picha
st.markdown(
    """
    <style>
    .card-title {
        background-color: #1f2937;
        color: white;
        padding: 8px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
        font-size: 14px;
        margin-bottom: 10px;
    }
    .score-box {
        background-color: #10b981;
        color: white;
        padding: 6px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .score-box-yellow {
        background-color: #f59e0b;
        color: white;
        padding: 6px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .vip-card {
        background-color: #0f172a;
        border: 2px solid #3b82f6;
        border-radius: 10px;
        padding: 15px;
        color: white;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Header Bar
st.markdown(
    "<h2 style='text-align: center; color: #f59e0b;'>⚽ SPORTIVO TRINIDENSE VS CLUB GUARANI</h2>",
    unsafe_allow_html=True,
)

# Sidebar kwa ajili ya Mipangilio
st.sidebar.header("⚙️ Mipangilio ya Engine")
home_team = st.sidebar.text_input("Timu ya Nyumbani", "Sportivo Trinidense")
away_team = st.sidebar.text_input("Timu ya Ugenini", "Club Guarani")

home_xg = st.sidebar.number_input(
    f"xG ya {home_team}", min_value=0.0, max_value=10.0, value=1.2, step=0.1
)
away_xg = st.sidebar.number_input(
    f"xG ya {away_team}", min_value=0.0, max_value=10.0, value=1.5, step=0.1
)

simulations = st.sidebar.slider(
    "Simulations (Runs)",
    min_value=1000,
    max_value=100000,
    value=100000,
    step=10000,
)

# Monte Carlo Simulation Engine
np.random.seed(42)
home_goals = np.random.poisson(home_xg, simulations)
away_goals = np.random.poisson(away_xg, simulations)

# Kuhesabu Matokeo Makuu
home_wins = np.sum(home_goals > away_goals)
draws = np.sum(home_goals == away_goals)
away_wins = np.sum(away_goals > home_goals)

home_prob = (home_wins / simulations) * 100
draw_prob = (draws / simulations) * 100
away_prob = (away_wins / simulations) * 100

# Top 1 & Top 2 Layouts (Kama picha)
c1, c2 = st.columns(2)

with c1:
    st.markdown(
        "<div class='card-title'>📊 USAMBAZAJI WA UWEZEKANO</div>",
        unsafe_allow_html=True,
    )
    st.metric(f"{home_team.upper()} KUSHINDA", f"{home_prob:.1f}%")
    st.metric("SARE (X)", f"{draw_prob:.1f}%")
    st.metric(f"{away_team.upper()} KUSHINDA", f"{away_prob:.1f}%")

with c2:
    st.markdown(
        "<div class='card-title'>⭐ MATOKEO YANAYOWEZEKANA ZAIDI (CORRECT SCORES)</div>",
        unsafe_allow_html=True,
    )

    # Kuhesabu Correct Score Frequencies
    scores = {}
    for h, a in zip(home_goals, away_goals):
        score_str = f"{h}-{a}"
        scores[score_str] = scores.get(score_str, 0) + 1

    sorted_scores = sorted(
        scores.items(), key=lambda item: item[1], reverse=True
    )

    sc_col1, sc_col2 = st.columns(2)
    for idx, (score_val, count) in enumerate(sorted_scores[:6]):
        prob_val = (count / simulations) * 100
        box_class = (
            "score-box" if idx % 2 == 0 else "score-box-yellow"
        )  # Rangi tofauti
        target_col = sc_col1 if idx < 3 else sc_col2
        with target_col:
            st.markdown(
                f"<div class='{box_class}'>{score_val} : {prob_val:.1f}%</div>",
                unsafe_allow_html=True,
            )

st.divider()

# Bottom Layout: 5x5 Matrix & VIP Options
col_matrix, col_vip = st.columns([1, 1])

with col_matrix:
    st.markdown(
        "<div class='card-title'>📊 JEDWALI LA MATOKEO (5 x 5 GRID)</div>",
        unsafe_allow_html=True,
    )

    # Kutengeneza Matrix ya 0 hadi 4
    matrix_data = np.zeros((5, 5))
    for h in range(5):
        for a in range(5):
            count = np.sum((home_goals == h) & (away_goals == a))
            matrix_data[h, a] = (count / simulations) * 100

    matrix_df = pd.DataFrame(
        matrix_data,
        columns=["0", "1", "2", "3", "4"],
        index=["0", "1", "2", "3", "4"],
    )
    st.dataframe(
        matrix_df.style.background_gradient(cmap="Reds").format("{:.1f}%"),
        use_container_width=True,
    )

with col_vip:
    st.markdown(
        "<div class='card-title'>★ VIP OPTIONS & SUGGESTED BETS ★</div>",
        unsafe_allow_html=True,
    )

    btts_yes = np.sum((home_goals > 0) & (away_goals > 0)) / simulations * 100
    over25 = np.sum((home_goals + away_goals) > 2.5) / simulations * 100

    best_score = sorted_scores[0][0]

    st.write(
        f"🟢 **Safe Bet:** {'Away or Draw' if away_prob > home_prob else 'Home or Draw'}"
    )
    st.write(
        f"🟡 **Value Bet:** Over 2.5 Goals ({over25:.1f}%)"
        if over25 > 50
        else f"🟡 **Value Bet:** Under 2.5 Goals ({100-over25:.1f}%)"
    )
    st.write(f"🔥 **Correct Score Pick:** {best_score}")
    st.write(f"⚡ **BTTS (GG):** {btts_yes:.1f}%")

    st.progress(
        int(max(home_prob, away_prob, draw_prob)), text="VIP Confidence Level"
    )

# Footer Info
st.caption(
    f"Data Engine: Monte Carlo Simulation ({simulations:,} runs) | Powered by Python Streamlit"
)

