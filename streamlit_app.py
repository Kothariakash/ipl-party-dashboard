import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

st.set_page_config(layout="wide")

# Load data
@st.cache_data
def load_data(_file_mod_time):
    # _file_mod_time parameter invalidates cache when files change
    final_df = pd.read_excel("final_output.xlsx")
    detailed_df = pd.read_excel("detailed_output.xlsx")
    return final_df, detailed_df

# Get file modification time to invalidate cache when files change
final_mtime = os.path.getmtime("final_output.xlsx")
final_df, detailed_df = load_data(final_mtime)

final_df, detailed_df = load_data()

# Title
st.title("IPL Fantasy Points Dashboard")

# Tabs
tab1, tab2 = st.tabs(["Leaderboards", "Granular Reports"])

with tab1:
    st.header("Leaderboards")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Batting Leaderboard")
        batting_leaders = final_df.groupby("Participant")["Batting Points"].sum().reset_index().sort_values("Batting Points", ascending=False)
        fig_bat = px.bar(batting_leaders, x="Participant", y="Batting Points", title="Batting Points Leaderboard")
        st.plotly_chart(fig_bat)
        st.dataframe(batting_leaders)

    with col2:
        st.subheader("Bowling Leaderboard")
        bowling_leaders = final_df.groupby("Participant")["Bowling Points"].sum().reset_index().sort_values("Bowling Points", ascending=False)
        fig_bowl = px.bar(bowling_leaders, x="Participant", y="Bowling Points", title="Bowling Points Leaderboard")
        st.plotly_chart(fig_bowl)
        st.dataframe(bowling_leaders)

with tab2:
    st.header("Match-wise Granular Report")

    matches = detailed_df["Match"].unique()
    selected_match = st.selectbox("Select Match", matches)

    if selected_match:
        match_details = detailed_df[detailed_df["Match"] == selected_match]
        # Plot first
        fig = px.bar(match_details, x="Participant", y="Points", color="Type", title=f"Points Breakdown for {selected_match}")
        st.plotly_chart(fig)
        # Then data
        st.dataframe(match_details)