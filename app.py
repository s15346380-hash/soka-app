import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Football Monte Carlo Simulator", layout="wide")

st.title("⚽ Dashboard ya Uchambuzi wa Soka (Monte Carlo)")
st.write("Tumia mfumo huu kuigiza matokeo ya mechi kulingana na takwimu za Expected Goals (xG).")

st.sidebar.header("⚙️ Mipangilio ya Mechi")
team_home = st.sidebar.text_input("Timu ya Nyumbani", "Sportivo Trinidense")
team_away = st.sidebar.text_input("Timu ya Ugenini", "Club Guarani")

xg_home = st.sidebar.number_input("xG Nyumbani", min_value=0.1, max_value=5.0, value=1.85, step=0.05)
xg_away = st.sidebar.number_input("xG Ugenini", min_value=0.1, max_value=5.0, value=1.10, step=0.05)

simulations = st.sidebar.select_slider(
    "Idadi ya Simulizi (Simulations)",
    options=[1000, 10000, 50000, 100000],
    value=100000
)

home_goals = np.random.poisson(xg_home, simulations)
away_goals = np.random.poisson(xg_away, simulations)

home_wins = np.sum(home_goals > away_goals) / simulations * 100
draws = np.sum(home_goals == away_goals) / simulations * 100
away_wins = np.sum(home_goals < away_goals) / simulations * 100

st.subheader(f"📊 Usambazaji wa Uwezekano: {team_home} vs {team_away}")
col1, col2, col3 = st.columns(3)

col1.metric(f"Ushindi wa {team_home}", f"{home_wins:.1f}%")
col2.metric("Sare (X)", f"{draws:.1f}%")
col3.metric(f"Ushindi wa {team_away}", f"{away_wins:.1f}%")

st.markdown("---")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📈 Over / Under Goals")
    total_goals = home_goals + away_goals
    over_15 = np.sum(total_goals > 1.5) / simulations * 100
    over_25 = np.sum(total_goals > 2.5) / simulations * 100
    over_35 = np.sum(total_goals > 3.5) / simulations * 100
    
    df_ou = pd.DataFrame({
        "Soko": ["Over 1.5", "Over 2.5", "Over 3.5"],
        "Uwezekano (%)": [over_15, over_25, over_35]
    })
    
    fig_ou = px.bar(df_ou, x="Soko", y="Uwezekano (%)", color="Soko", text_auto=".1f")
    st.plotly_chart(fig_ou, use_container_width=True)

with col_right:
    st.subheader("🎯 Matrix ya Matokeo (Heatmap Score %)")
    max_goals = 4
    score_matrix = np.zeros((max_goals + 1, max_goals + 1))
    
    for h, a in zip(home_goals, away_goals):
        if h <= max_goals and a <= max_goals:
            score_matrix[h, a] += 1
            
    score_matrix = (score_matrix / simulations) * 100
    
    fig_heatmap = px.imshow(
        score_matrix,
        labels=dict(x=f"Mabao ya {team_away}", y=f"Mabao ya {team_home}", color="Uwezekano %"),
        x=[str(i) for i in range(max_goals + 1)],
        y=[str(i) for i in range(max_goals + 1)],
        text_auto=".1f",
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
