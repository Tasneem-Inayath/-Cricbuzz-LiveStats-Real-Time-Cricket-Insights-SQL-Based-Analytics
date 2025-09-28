import requests
import streamlit as st
import threading, webbrowser
from datetime import datetime


# ----------------- API HEADERS -----------------
headers = {
    "x-rapidapi-key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
    "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

# ----------------- PLAYER SEARCH -----------------
def open_browser(url):
    webbrowser.open_new_tab(url)

# def fetch_url(searched_id):
#     info_url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{searched_id}"
#     try:
#         response = requests.get(info_url, headers=headers)
#         response.raise_for_status()
#         data = response.json()
#         player_url = data.get("appIndex", {}).get("webURL")
#         if player_url:
#             st.success(f"✅ Opening profile for player ID: {searched_id}...")
#             thread = threading.Thread(target=open_browser, args=(player_url,))
#             thread.start()
#         else:
#             st.error("❌ Profile URL not found.")
#     except requests.exceptions.RequestException as e:
#         st.error(f"Error fetching player profile: {e}")

def search(input_player):
    url = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/search"
    querystring = {"plrN": input_player}
    try:
        with st.spinner('Searching for players...'):
            response = requests.get(url, headers=headers, params=querystring)
            response.raise_for_status()
            response_json = response.json()
        players = response_json.get("player", [])
        st.session_state.results = [
            {"id": p.get("id"), "name": p.get("name"), "country": p.get("teamName", "Unknown")}
            for p in players
        ]

    except requests.exceptions.RequestException as e:
        st.error(f"Error during search: {e}")
        st.session_state.results = []
        return None

# ----------------- SERIES FETCH -----------------
def fetch_series(series_type: str):
    url = f"https://cricbuzz-cricket.p.rapidapi.com/series/v1/{series_type.capitalize()}"
    response = requests.get(url, headers=headers)
    data = response.json()
    list_of_series = []
    series_map = data.get("seriesMapProto", []) or data.get("seriesMap", [])
    for series_group in series_map:
        for s in series_group.get('series', []):
            season = datetime.fromtimestamp(int(s['startDt']) / 1000).year
            if season == 2025:
                list_of_series.append({"series_id": s['id'], "series_name": s['name']})
    return list_of_series

# ----------------- MATCH FORMAT -----------------
def get_match_format(series_id_to_check):
    url = f"https://cricbuzz-cricket.p.rapidapi.com/series/v1/{series_id_to_check}"
    response = requests.get(url, headers=headers)
    data = response.json()
    matches = []
    for item in data.get('matchDetails', []):
        match_map = item.get('matchDetailsMap', {}).get('match', [])
        for m in match_map:
            match_info = m.get('matchInfo', {})
            if match_info:
                matches.append({
                    'matchId': match_info.get('matchId'),
                    'seriesId': match_info.get('seriesId'),
                    'matchFormat': match_info.get('matchFormat')
                })
    if matches:
        return matches
    return [{'matchFormat': 'T20'}]

# ----------------- STATS FETCH -----------------
def fetch_most_runs(series_id, match_format):
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/series/{series_id}"
    response = requests.get(url, headers=headers, params={"statsType": "mostRuns"})
    data = response.json()
    dynamic_key = f"{match_format.lower()}StatsList"
    stats_list = data.get(dynamic_key, {})
    values = stats_list.get("values", [])
    runs_data = []
    for v in values:
        vals = v.get("values", [])
        runs_data.append({
            "Name": vals[1] if len(vals) > 1 else "-",
            "Matches": int(vals[2]) if len(vals) > 2 and vals[2].isdigit() else 0,
            "Innings": int(vals[3]) if len(vals) > 3 and vals[3].isdigit() else 0,
            "Runs": int(vals[4]) if len(vals) > 4 and vals[4].isdigit() else 0,
            "Average": float(vals[5]) if len(vals) > 5 and vals[5] not in ["-", None] else None,
        })
    return runs_data[:5]

def fetch_most_wickets(series_id, match_format):
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/series/{series_id}"
    response = requests.get(url, headers=headers, params={"statsType": "mostWickets"})
    data = response.json()
    dynamic_key = f"{match_format.lower()}StatsList"
    stats_list = data.get(dynamic_key, {})
    values = stats_list.get("values", [])
    wickets_data = []
    for v in values:
        vals = v.get("values", [])
        wickets_data.append({
            "Name": vals[1] if len(vals) > 1 else "-",
            "Matches": int(vals[2]) if len(vals) > 2 and vals[2].isdigit() else 0,
            "Overs": vals[3] if len(vals) > 3 else "-",
            "Wickets": int(vals[4]) if len(vals) > 4 and vals[4].isdigit() else 0,
            "Average": float(vals[5]) if len(vals) > 5 and vals[5] not in ["-", None] else None,
        })
    return sorted(wickets_data, key=lambda x: x["Wickets"], reverse=True)[:5]

def fetch_high_scores(series_id, match_format):
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/series/{series_id}"
    response = requests.get(url, headers=headers, params={"statsType": "highestScore"})
    data = response.json()
    dynamic_key = f"{match_format.lower()}StatsList"
    stats_list = data.get(dynamic_key, {})
    values = stats_list.get("values", [])
    high_scores_data = []
    for v in values:
        vals = v.get("values", [])
        high_scores_data.append({
            "Name": vals[1] if len(vals) > 1 else "-",
            "Runs": int(vals[2]) if len(vals) > 2 and vals[2].isdigit() else 0,
            "Balls": int(vals[3]) if len(vals) > 3 and vals[3].isdigit() else 0,
            "Innings": int(vals[4]) if len(vals) > 4 and vals[4].isdigit() else 0,
        })
    return sorted(high_scores_data, key=lambda x: x["Runs"], reverse=True)[:5]


def acq_details_of_player(player_id):
    import requests
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}"
    headers = {
            "x-rapidapi-key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
            "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
        }
    response = requests.get(url, headers=headers)
    data = response.json()
    detail_player =[]
    detail_player.append({
        "name":data.get('name','N/A'),
        "nickname":data.get('nickName','N/A'),
        "role":data.get('role','N/A'),
        "batting":data.get('bat','N/A'),
        "bowling":data.get('bowl','N/A'),
        "international_team":data.get('intlTeam','N/A'),
        "dob":data.get('DoB','N/A'),
        "birth_place":data.get('birthPlace','N/A'),
        "height":data.get("height",'N/A'),
        "teams_played":data.get('teams','N/A'),
        "web_url":data['appIndex']["webURL"]})

    return( detail_player)
def stat_batting(player_id):
    import requests

    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}/batting"
    headers = {
        "x-rapidapi-key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    return data
def stat_bowling(player_id):
    import requests

    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}/bowling"
    headers = {
        "x-rapidapi-key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    return data
def back_to_home():
    if st.button("🏠 Back to Home Page"):
        st.switch_page("pages/homepage.py")  