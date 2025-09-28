import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import sys, os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.match_helpers import *

# API Setup
url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"
headers = {
    "x-rapidapi-key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
    "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}
response = requests.get(url, headers=headers)
data = response.json()

def render_dashboard_ui():
    st.set_page_config(page_title="Cricket Matches Dashboard", page_icon="🏏", layout="wide")
    st.title("🏏 Cricket Matches Dashboard")
    st.markdown("Catch **live, completed, and upcoming cricket matches** with detailed scorecards!")

    match_type = st.radio("Select Match Type", ["Live Matches", "Completed Matches", "Upcoming Matches"], horizontal=True)


    def render_selected_match(details, match_type):
        st.markdown(f"## 🔹 {details.get('desc', details.get('teams', 'Match'))}")

        # ----- MATCH INFO CARD -----
        match_datetime = details.get('date', 'N/A')
        try:
            from datetime import datetime
        # assuming details['date'] is ISO format like "2025-09-22T14:30:00Z"
            dt_obj = datetime.fromisoformat(match_datetime.replace('Z', '+00:00'))
            formatted_date = dt_obj.strftime("%A, %d %b %Y | %I:%M %p")
        except:
            formatted_date = match_datetime

        # Info box with match details
        st.markdown(f"""
        <div style="
            background-color: #E0F3FF;
            color: #0366d6;
            padding: 20px;
            border-radius: 15px;
            font-size: 16px;
            line-height: 1.5;
        ">
        <b>Format:</b> {details.get('match_format', 'N/A')}<br>
        <b>Venue:</b> {details.get('venue', 'N/A')}<br>
        <b>City:</b> {details.get('city', 'N/A')}<br>
        <b>Date & Time:</b> {formatted_date}<br>
        </div>
        """, unsafe_allow_html=True)


        # ----- LIVE MATCH -----
        if match_type == "live":
            team_scores = details['score'].split('|')  # split "team1_score | team2_score"
            team1_score = team_scores[0].strip()
            team2_score = team_scores[1].strip()
            col1, col2 = st.columns(2)
            st.markdown(f"""
            <div style="
                padding: 30px; 
                background-color: #d4edda; 
                color: #155724; 
                border-radius: 15px; 
                border: 2px solid #c3e6cb; 
                text-align: center;
                font-size: 24px;
                font-weight: bold;
            ">
                {details.get('status', 'N/A')}
            </div>
            """
            , unsafe_allow_html=True)
            # Blue styled boxes
            col1.write(details['team1'])
            col1.markdown(f"""
                <div style="
                    background-color: #007BFF;
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                    font-size: 20px;
                    font-weight: bold;">
                    {team1_score}
                </div>
            """, unsafe_allow_html=True)
            col2.write(details['team2'])
            col2.markdown(f"""
                <div style="
                    background-color: #007BFF;
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                    font-size: 20px;
                    font-weight: bold;">
                    {team2_score}
                </div>
            """, unsafe_allow_html=True) 
            if "innings_data" in details and st.button("📑 Show Detailed Live Scorecard"):
                for idx, inn in enumerate(details["innings_data"], 1):
                    st.markdown(f"## 🏏 Innings {idx}: {inn.get('team', 'Unknown Team')}")

                    # Use two columns
                    colA, colB = st.columns(2)

                    # Batting Table
                    with colA:
                        st.subheader("Batting")
                        batting_df = inn.get("batting")
                        if batting_df is not None and not batting_df.empty:
                            st.dataframe(
                                batting_df[["Batsman", "Runs", "Balls", "Fours", "Sixes"]],
                                use_container_width=True
                            )
                        else:
                            st.info("No batting data available")

                    # Bowling Table
                    with colB:
                        st.subheader("Bowling")
                        bowling_df = inn.get("bowling")
                        if bowling_df is not None and not bowling_df.empty:
                            st.dataframe(
                                bowling_df[["Bowler", "Overs", "Maidens", "Runs", "Wickets"]],
                                use_container_width=True
                            )
                        else:
                            st.info("No bowling data available")



        # ----- COMPLETED MATCH -----
        elif match_type == "completed":
            st.success(details["teams"])
            st.markdown(f"""
            <div style="
                padding: 30px; 
                background-color: #d4edda; 
                color: #155724; 
                border-radius: 15px; 
                border: 2px solid #c3e6cb; 
                text-align: center;
                font-size: 24px;
                font-weight: bold;
            ">
                {details.get('status', 'N/A')}
            </div>
            """
            , unsafe_allow_html=True)
            if "innings_data" in details and st.button("📑 Show Detailed Live Scorecard"):
                for idx, inn in enumerate(details["innings_data"], 1):
                    st.markdown(f"## 🏏 Innings {idx}: {inn.get('team', 'Unknown Team')}")

                    # Use two columns
                    colA, colB = st.columns(2)

                    # Batting Table
                    with colA:
                        st.subheader("Batting")
                        batting_df = inn.get("batting")
                        if batting_df is not None and not batting_df.empty:
                            st.dataframe(
                                batting_df[["Batsman", "Runs", "Balls", "Fours", "Sixes"]],
                                use_container_width=True
                            )
                        else:
                            st.info("No batting data available")

                    # Bowling Table
                    with colB:
                        st.subheader("Bowling")
                        bowling_df = inn.get("bowling")
                        if bowling_df is not None and not bowling_df.empty:
                            st.dataframe(
                                bowling_df[["Bowler", "Overs", "Maidens", "Runs", "Wickets"]],
                                use_container_width=True
                            )
                        else:
                            st.info("No bowling data available")


            if details.get("seriesId"):
                points_df = fetch_points_table(details["seriesId"])
                if not points_df.empty:
                    st.subheader("📊 Points Table")
                    st.dataframe(points_df)
                    if points_df["Points"].sum() > 0:
                        fig, ax = plt.subplots(figsize=(8,6))
                        colors = ["#FF5733", "#33FF57", "#3357FF", "#F0FF33", "#FF33F6", "#33FFF5"]  # repeated if needed                        
                        ax.bar(points_df["Team"], points_df["Points"], color=colors * (len(points_df)//len(colors)+1))
                        ax.set_xlabel("Team")
                        ax.set_ylabel("Points")
                        ax.set_title("Team Points Distribution")
                        ax.tick_params(axis="x", rotation=45)
                        st.pyplot(fig)

        # ----- UPCOMING MATCH -----
        elif match_type == "upcoming":
            st.subheader("Upcoming Match Details")
            st.markdown(f"""
            <div style="
                padding: 30px; 
                background-color: #d4edda; 
                color: #155724; 
                border-radius: 15px; 
                border: 2px solid #c3e6cb; 
                text-align: center;
                font-size: 24px;
                font-weight: bold;
            ">
                {details.get('status', 'N/A')}
            </div>
            """
            , unsafe_allow_html=True)

    # ------------------- LIVE -------------------
    if match_type == "Live Matches":
        live_matches = fetch_live_matches(data)
        if not live_matches:
            st.warning("No live matches currently.")
        else:
            selected_live = st.selectbox("Select a Live Match", [m['desc'] for m in live_matches])
            if selected_live:
                match = next((m for m in live_matches if m['desc'] == selected_live), None)
                details = fetch_live_match_details(data, match)
                if details:
                    render_selected_match(details, "live")

    # ------------------- COMPLETED -------------------
    elif match_type == "Completed Matches":
        completed_data = requests.get("https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent", headers=headers).json()
        completed_matches = fetch_completed_matches(completed_data)
        if not completed_matches:
            st.warning("No completed matches found.")
        else:
            selected_completed = st.selectbox("Select a Completed Match", [m['desc'] for m in completed_matches])
            if selected_completed:
                match = next((m for m in completed_matches if m['desc'] == selected_completed), None)
                details = fetch_completed_match_details(completed_data, match)
                if details:
                    render_selected_match(details, "completed")

    # ------------------- UPCOMING -------------------
    elif match_type == "Upcoming Matches":
        upcoming_matches = fetch_upcoming_matches()
        if not upcoming_matches:
            st.info("No upcoming matches.")
        else:
            selected_upcoming = st.selectbox("Select an Upcoming Match", [m['desc'] for m in upcoming_matches])
            if selected_upcoming:
                match = next((m for m in upcoming_matches if m['desc'] == selected_upcoming), None)
                if match:
                    render_selected_match(match, "upcoming")

render_dashboard_ui()
st.subheader("📱 About This Dashboard")
st.info("""
**Live Matches Page:**
- Real-time cricket match updates  
- Player scorecards & stats  
- Match summary & highlights  
- Auto-refresh option  
- Quick navigation to player profiles  
""")
back_to_home()
