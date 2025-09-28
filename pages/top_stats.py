import pandas as pd
import altair as alt
import sys,os
import streamlit as st
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.stat_helpers import *
# ----------------- STREAMLIT UI -----------------
st.set_page_config(page_title="🏏 Cricbuzz Stats Dashboard", page_icon="🏏")
st.title("🏏 Cricbuzz Stats Dashboard 🌈")

# --- Player Search ---
st.subheader("🔎 Player Search")
if 'results' not in st.session_state:
    st.session_state.results = []

player_name = st.text_input("Enter player name")
if st.button("Search Player"):
    if player_name.strip():
        search(player_name)
        if st.session_state.get("results"):
            results = st.session_state.results
    
            selected_id = None  # default

            if len(results) > 1:
                options = {f"{p['name']} ({p['country']})": p["id"] for p in results}
                selected_label = st.selectbox("Select Player", ["Select a player"] + list(options.keys()))
                if selected_label != "Select a player":
                    selected_id = options[selected_label]
            elif len(results) == 1:
                selected_id = results[0]["id"]

            if selected_id:
                detailed_p = acq_details_of_player(selected_id)
                p = detailed_p[0]
                st.title(p['name'])
                st.markdown(f"**Nickname:** {p['nickname']}")
                st.markdown("---")
                st.header("Personal Information")
                tab1, tab2, tab3 = st.tabs(["📊 Profile", "🏏 Batting Stats", "⚾ Bowling Stats"])
                with tab1:
                    col_cricket, col_personal, col_teams = st.columns(3)

                    with col_cricket:
                        st.subheader("🏏 Cricket Details")
                        st.markdown(f"**Role:** {p['role']}")
                        st.markdown(f"**Batting:** {p['batting']}")
                        st.markdown(f"**Bowling:** {p['bowling']}")
                        st.markdown(f"**International Team:** {p['international_team']}")

                    with col_personal:
                        st.subheader("👤 Personal Details")
                        st.markdown(f"**Date of Birth:** {p['dob']}")
                        st.markdown(f"**Birth Place:** {p['birth_place']}")
                        st.markdown(f"**Height:** {p['height']}")

                    with col_teams:
                        st.subheader("🏆 Teams Played For")
                        teams = p['teams_played']
                        list_played = teams.split(',') if teams else []
                        for t in list_played:
                            st.markdown(f"- {t}")
                with tab2:
                        batting_stats = stat_batting(selected_id)
                        st.header("🏏 Batting Career Statistics")
                        st.subheader("📊 Career Overview")

                        col_test, col_odi, col_t20, col_ipl = st.columns(4)
                        columns = [col_test, col_odi, col_t20, col_ipl]
                        headers = batting_stats["headers"][1:]  # Test, ODI, T20, IPL
                        rows = batting_stats["values"]

                        # Populate columns
                        for col_idx, col in enumerate(columns):
                            with col:
                                st.subheader(headers[col_idx])
                                for row in rows:
                                    stat_name = row["values"][0]        # Matches, Runs, Average...
                                    stat_value = row["values"][col_idx + 1]  # column value
                                    st.markdown(f"**{stat_name}**")
                                    st.markdown(stat_value)
                                    st.markdown("<br>", unsafe_allow_html=True)
                with tab3:
                        bowling_stats = stat_bowling(selected_id)
                        st.header("🏏 Bowling Career Statistics")
                        st.subheader("📊 Career Overview")

                        col_test, col_odi, col_t20, col_ipl = st.columns(4)
                        columns = [col_test, col_odi, col_t20, col_ipl]
                        headers = bowling_stats["headers"][1:]  # Test, ODI, T20, IPL
                        rows = bowling_stats["values"]

                        # Populate columns
                        for col_idx, col in enumerate(columns):
                            with col:
                                st.subheader(headers[col_idx])
                                for row in rows:
                                    stat_name = row["values"][0]        # Matches, Runs, Average...
                                    stat_value = row["values"][col_idx + 1]  # column value
                                    st.markdown(f"**{stat_name}**")
                                    st.markdown(stat_value)
                                    st.markdown("<br>", unsafe_allow_html=True)



                # Horizontal line for separation
                st.markdown("---")

                # External link
                st.markdown(f"**Open link for more info:** [{p['web_url']}]({p['web_url']})")




# --- Series Stats ---
st.subheader("📈 Series Stats")
series_type = st.selectbox("Select Series Type", ["International", "League", "Domestic", "Women", "All"])
all_series = fetch_series(series_type)

if all_series:
    series_options = {s["series_name"]: s["series_id"] for s in all_series}
    series_name = st.selectbox("Select a Series", list(series_options.keys()))
    series_id = series_options[series_name]
    match_format = get_match_format(series_id)[0]['matchFormat']
    st.info(f"Detected Match Format: **{match_format}** 🎯")

    # Fetch stats
    most_runs = fetch_most_runs(series_id, match_format)
    high_scores = fetch_high_scores(series_id, match_format)
    most_wickets = fetch_most_wickets(series_id, match_format)

    # Display side by side
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🏏 Top Batting Stats")
        st.table(most_runs)
        st.markdown("### 🔥 Highest Scores")
        st.table(high_scores)
    with col2:
        st.markdown("### 🎯 Top Bowling Stats")
        st.table(most_wickets)

    # --- Colorful Charts ---
    if most_runs:
        df_runs = pd.DataFrame(most_runs)
        st.markdown("### 📊 Top Run Scorers 🌟")
        chart1 = alt.Chart(df_runs).mark_bar(color='#1f77b4').encode(
            x=alt.X('Name', sort='-y'),
            y='Runs',
            tooltip=['Name','Runs','Matches','Average']
        )
        st.altair_chart(chart1, use_container_width=True)

    if most_wickets:
        df_wickets = pd.DataFrame(most_wickets)
        st.markdown("### 📊 Top Wicket Takers 🏹")
        chart2 = alt.Chart(df_wickets).mark_bar(color='#ff7f0e').encode(
            x=alt.X('Name', sort='-y'),
            y='Wickets',
            tooltip=['Name','Wickets','Matches','Average']
        )
        st.altair_chart(chart2, use_container_width=True)

else:
    st.warning("No series found for selected type.")
st.subheader("📱 About This Dashboard")
st.info("""
**Top Stats Page:**
- Highest run scorers & strike rates  
- Best bowling performances  
- Player comparisons  
- Team-wise top performers  
- Season-wise trends  
""")
back_to_home()