import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

st.set_page_config(layout="wide")

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data(_file_mod_time):
    # Cache invalidation when file changes
    final_df = pd.read_excel("final_output.xlsx")
    detailed_df = pd.read_excel("detailed_output.xlsx")
    return final_df, detailed_df

# Get file modification time
final_mtime = os.path.getmtime("final_output.xlsx")

final_df, detailed_df = load_data(final_mtime)

# =========================================================
# TITLE
# =========================================================

st.title("IPL Fantasy Points Dashboard")

# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3 = st.tabs([
    "Leaderboards",
    "Granular Reports",
    "Overall Participant Report"
])

# =========================================================
# TAB 1 - LEADERBOARDS
# =========================================================

with tab1:

    st.header("Leaderboards")

    col1, col2 = st.columns(2)

    # =====================================================
    # BATTING LEADERBOARD
    # =====================================================

    with col1:

        st.subheader("Batting Leaderboard")

        batting_leaders = (
            final_df.groupby("Participant")["Batting Points"]
            .sum()
            .reset_index()
            .sort_values("Batting Points", ascending=False)
        )

        fig_bat = px.bar(
            batting_leaders,
            x="Participant",
            y="Batting Points",
            text="Batting Points",
            color="Batting Points",
            title="Batting Points Leaderboard"
        )

        fig_bat.update_layout(height=500)

        st.plotly_chart(fig_bat, use_container_width=True)

        st.dataframe(batting_leaders, use_container_width=True)

    # =====================================================
    # BOWLING LEADERBOARD
    # =====================================================

    with col2:

        st.subheader("Bowling Leaderboard")

        bowling_leaders = (
            final_df.groupby("Participant")["Bowling Points"]
            .sum()
            .reset_index()
            .sort_values("Bowling Points", ascending=False)
        )

        fig_bowl = px.bar(
            bowling_leaders,
            x="Participant",
            y="Bowling Points",
            text="Bowling Points",
            color="Bowling Points",
            title="Bowling Points Leaderboard"
        )

        fig_bowl.update_layout(height=500)

        st.plotly_chart(fig_bowl, use_container_width=True)

        st.dataframe(bowling_leaders, use_container_width=True)

# =========================================================
# TAB 2 - GRANULAR REPORT
# =========================================================

with tab2:

    st.header("Match-wise Granular Report")

    matches = detailed_df["Match"].unique()

    selected_match = st.selectbox(
        "Select Match",
        matches
    )

    if selected_match:

        match_details = detailed_df[
            detailed_df["Match"] == selected_match
        ]

        # =================================================
        # MATCH BAR CHART
        # =================================================

        fig = px.bar(
            match_details,
            x="Participant",
            y="Points",
            color="Type",
            title=f"Points Breakdown for {selected_match}",
            hover_data=["Player Name", "Pick"]
        )

        fig.update_layout(height=600)

        st.plotly_chart(fig, use_container_width=True)

        # =================================================
        # DATAFRAME
        # =================================================

        st.dataframe(match_details, use_container_width=True)

# =========================================================
# TAB 3 - OVERALL PARTICIPANT REPORT
# =========================================================

with tab3:

    st.header("Overall Participant Analytics")

    participants = sorted(detailed_df["Participant"].unique())

    selected_participant = st.selectbox(
        "Select Participant",
        participants
    )

    participant_df = detailed_df[
        detailed_df["Participant"] == selected_participant
    ].copy()

    # =====================================================
    # KPI METRICS
    # =====================================================

    total_points = participant_df["Points"].sum()

    batting_points = participant_df[
        participant_df["Type"] == "Batting"
    ]["Points"].sum()

    bowling_points = participant_df[
        participant_df["Type"] == "Bowling"
    ]["Points"].sum()

    total_picks = participant_df.shape[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Points", total_points)
    col2.metric("Batting Points", batting_points)
    col3.metric("Bowling Points", bowling_points)
    col4.metric("Total Picks", total_picks)

    st.markdown("---")

    # =====================================================
    # BATTING VS BOWLING
    # =====================================================

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Batting vs Bowling Contribution")

        type_summary = (
            participant_df.groupby("Type")["Points"]
            .sum()
            .reset_index()
        )

        fig_pie = px.pie(
            type_summary,
            names="Type",
            values="Points",
            hole=0.4,
            title="Contribution Split"
        )

        fig_pie.update_layout(height=500)

        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:

        st.subheader("Type-wise Points")

        fig_type = px.bar(
            type_summary,
            x="Type",
            y="Points",
            text="Points",
            color="Type",
            title="Batting vs Bowling Points"
        )

        fig_type.update_layout(height=500)

        st.plotly_chart(fig_type, use_container_width=True)

    # =====================================================
    # PLAYER CONTRIBUTION
    # =====================================================

    st.subheader("Player Contribution Summary")

    player_summary = (
        participant_df.groupby(
            ["Player Name", "Type"]
        )["Points"]
        .sum()
        .reset_index()
        .sort_values("Points", ascending=False)
    )

    fig_player = px.bar(
        player_summary,
        x="Player Name",
        y="Points",
        color="Type",
        text="Points",
        title="Player-wise Contribution"
    )

    fig_player.update_layout(
        xaxis_tickangle=-45,
        height=600
    )

    st.plotly_chart(fig_player, use_container_width=True)

    st.dataframe(player_summary, use_container_width=True)

    # =====================================================
    # POSITION ANALYSIS
    # =====================================================

    st.subheader("Position-wise Analysis")

    # Extract numeric position from Pick
    participant_df["Position"] = (
        participant_df["Pick"]
        .str.extract(r'(\d+)')
    )

    position_summary = (
        participant_df.groupby(
            ["Position", "Type"]
        )["Points"]
        .sum()
        .reset_index()
    )

    # =====================================================
    # BAR + PIE CHARTS
    # =====================================================

    col1, col2, col3 = st.columns(3)

    # =====================================================
    # BAR CHART
    # =====================================================

    with col1:

        fig_position = px.bar(
            position_summary,
            x="Position",
            y="Points",
            color="Type",
            barmode="group",
            text="Points",
            title="Position-wise Points"
        )

        fig_position.update_layout(height=500)

        st.plotly_chart(fig_position, use_container_width=True)

    # =====================================================
    # BATTING POSITION PIE
    # =====================================================

    with col2:

        batting_position = (
            position_summary[
                position_summary["Type"] == "Batting"
            ]
        )

        fig_batting_pie = px.pie(
            batting_position,
            names="Position",
            values="Points",
            hole=0.4,
            title="Batting Position Contribution"
        )

        fig_batting_pie.update_layout(height=500)

        st.plotly_chart(fig_batting_pie, use_container_width=True)

    # =====================================================
    # BOWLING POSITION PIE
    # =====================================================

    with col3:

        bowling_position = (
            position_summary[
                position_summary["Type"] == "Bowling"
            ]
        )

        fig_bowling_pie = px.pie(
            bowling_position,
            names="Position",
            values="Points",
            hole=0.4,
            title="Bowling Position Contribution"
        )

        fig_bowling_pie.update_layout(height=500)

        st.plotly_chart(fig_bowling_pie, use_container_width=True)

    # =====================================================
    # MATCH-WISE PERFORMANCE
    # =====================================================

    st.subheader("Match-wise Performance")

    match_summary = (
        participant_df.groupby("Match")["Points"]
        .sum()
        .reset_index()
    )

    fig_match = px.line(
        match_summary,
        x="Match",
        y="Points",
        markers=True,
        text="Points",
        title="Points Across Matches"
    )

    fig_match.update_layout(height=500)

    st.plotly_chart(fig_match, use_container_width=True)

    # =====================================================
    # TOP PICKS
    # =====================================================

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Top Picks")

        top_picks = (
            participant_df
            .sort_values("Points", ascending=False)
            .head(10)
        )

        fig_top = px.bar(
            top_picks,
            x="Player Name",
            y="Points",
            color="Type",
            text="Points",
            title="Best Performing Picks"
        )

        fig_top.update_layout(
            xaxis_tickangle=-45,
            height=500
        )

        st.plotly_chart(fig_top, use_container_width=True)

    with col2:

        st.subheader("Low Performing Picks")

        low_picks = (
            participant_df
            .sort_values("Points", ascending=True)
            .head(10)
        )

        fig_low = px.bar(
            low_picks,
            x="Player Name",
            y="Points",
            color="Type",
            text="Points",
            title="Lowest Performing Picks"
        )

        fig_low.update_layout(
            xaxis_tickangle=-45,
            height=500
        )

        st.plotly_chart(fig_low, use_container_width=True)

    # =====================================================
    # HEATMAP
    # =====================================================

    st.subheader("Player vs Match Heatmap")

    heatmap_df = participant_df.pivot_table(
        index="Player Name",
        columns="Match",
        values="Points",
        aggfunc="sum",
        fill_value=0
    )

    fig_heat = px.imshow(
        heatmap_df,
        text_auto=True,
        aspect="auto",
        title="Player Performance Heatmap"
    )

    fig_heat.update_layout(height=700)

    st.plotly_chart(fig_heat, use_container_width=True)

    # =====================================================
    # MATCH-WISE PLAYER CONTRIBUTION
    # =====================================================

    st.subheader("Match-wise Player Contribution")

    fig_match_player = px.bar(
        participant_df,
        x="Match",
        y="Points",
        color="Player Name",
        barmode="stack",
        title="Player Contribution Across Matches",
        hover_data=["Pick", "Type"]
    )

    fig_match_player.update_layout(height=700)

    st.plotly_chart(fig_match_player, use_container_width=True)

    # =====================================================
    # COMPLETE DETAILED TABLE
    # =====================================================

    st.subheader("Complete Detailed Report")

    st.dataframe(
        participant_df.sort_values(
            "Points",
            ascending=False
        ),
        use_container_width=True,
        height=700
    )