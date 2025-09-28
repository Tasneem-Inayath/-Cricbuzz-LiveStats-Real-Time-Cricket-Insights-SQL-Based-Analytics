
import requests
import pandas as pd
import streamlit as st
# API setup
url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent"
headers = {
	"x-rapidapi-key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
	"x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}


response = requests.get(url, headers=headers)
data = response.json()



# ----------------- Helpers -----------------
def fetch_completed_matches(data1):
    completed_matches = []
    for match_type in data1.get('typeMatches', []):
        for series in match_type.get('seriesMatches', []):
            if 'seriesAdWrapper' in series:
                series_id = series['seriesAdWrapper']['seriesId']
                for match in series['seriesAdWrapper']['matches']:
                    info = match['matchInfo']
                    desc = f"{info['team1']['teamName']} vs {info['team2']['teamName']} - {info.get('matchDesc','')}"
                    match_id = info.get('matchId', None)
                    completed_matches.append({"desc": desc, "matchId": match_id, "seriesId": series_id})
    return completed_matches


import datetime

def fetch_completed_match_details(data1, selected_match):
    import datetime
    desc = selected_match["desc"]
    match_id = selected_match["matchId"]

    for match_type in data1.get('typeMatches', []):
        for series in match_type.get('seriesMatches', []):
            if 'seriesAdWrapper' in series:
                for match in series['seriesAdWrapper']['matches']:
                    info = match['matchInfo']
                    score = match.get('matchScore', {})
                    curr_desc = f"{info['team1']['teamName']} vs {info['team2']['teamName']} - {info.get('matchDesc','')}"
                    series_id = series['seriesAdWrapper'].get("seriesId")
                    # match_id = info.get("matchId")
                    start_date = info.get("startDate")
                    # convert startDate to readable date
                    date_str = "N/A"
                    if start_date:
                        import datetime
                        date_str = datetime.datetime.fromtimestamp(int(start_date)/1000).strftime("%d %b %Y, %I:%M %p")
                    if desc == curr_desc:
                        venue = info.get('venueInfo', {}).get('ground', 'N/A')

                        # Team scores
                        team1_score = "Yet to bat"
                        t1 = score.get('team1Score', {})
                        inngs1 = t1.get('inngs1', {})
                        if inngs1:
                            team1_score = f"{inngs1.get('runs','0')}/{inngs1.get('wickets','0')} ({inngs1.get('overs','0')})"

                        team2_score = "Yet to bat"
                        t2 = score.get('team2Score', {})
                        inngs2 = t2.get('inngs1', {})
                        if inngs2:
                            team2_score = f"{inngs2.get('runs','0')}/{inngs2.get('wickets','0')} ({inngs2.get('overs','0')})"

                        # Fetch full scorecard using matchId
                        url_scorecard = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{match_id}/hscard"
                        response2 = requests.get(url_scorecard, headers=headers)
                        scorecard_data = response2.json()

                        batsman_all = []
                        bowler_all= []
                        innings_data = []

                        # Loop through each innings in the scorecard
                        for innings in scorecard_data['scorecard']:
                            team_name = innings['batteamname']

                            # Batting
                            batsman_inn = []
                            for b in innings['batsman']:
                                runs = int(b.get("runs", 0))
                                balls = int(b.get("balls", 1))  # avoid div by 0
                                strike_rate = round((runs / balls) * 100, 2) if balls > 0 else 0
                                
                                batsman_inn.append({
                                    "Batsman": b.get("name"),
                                    "Runs": runs,
                                    "Balls": balls,
                                    "Fours": b.get("fours"),
                                    "Sixes": b.get("sixes"),
                                    "Strike Rate": strike_rate,
                                    
                                })
                            batsman_all.extend(batsman_inn)

                            # Bowling
                            bowler_inn = []
                            for bw in innings['bowler']:
                                bowler_inn.append({
                                    "Bowler": bw.get("name"),
                                    "Overs": bw.get("overs"),
                                    "Maidens": bw.get("maidens"),
                                    "Runs": bw.get("runs"),
                                    "Wickets": bw.get("wickets"),
                                    "Economy": bw.get("econ")
                                })
                            bowler_all.extend(bowler_inn)

                            # Save per innings
                            innings_data.append({
                                "team": team_name,
                                "batting": pd.DataFrame(batsman_inn),
                                "bowling": pd.DataFrame(bowler_inn)
                            })
                        
                        return {
                            "teams": f"{info['team1']['teamName']} vs {info['team2']['teamName']}",
                            "status": info.get('status', 'N/A'),
                            "venue": venue,
                            "city":info.get('venueInfo',{}).get('city','N/A'),
                            "date": date_str,
                            "score": f"{team1_score} | {team2_score}",
                            "df_batting": pd.DataFrame(batsman_all),
                            "df_bowling": pd.DataFrame(bowler_all),
                            "innings_data": innings_data,
                            "scorecard_data": scorecard_data,
                            "seriesId": series_id,
                            "match_format":info.get('matchFormat',"N/A")
                        }
def fetch_points_table(series_id):
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/series/{series_id}/points-table"
    response = requests.get(url, headers=headers)
    data = response.json()

    points = []
    for group in data.get("pointsTable", []):   # example: Group A, Group B
        group_name = group.get("groupName", "Points Table")
        for team in group.get("pointsTableInfo", []):
            points.append({
                "Group": group_name,
                "Team": team.get("teamName", ""),
                "Matches": team.get("matchesPlayed", 0),
                "Wins": team.get("matchesWon", team.get("wins", 0)),   # handle both keys
                "Loss": team.get("matchesLost", team.get("loss", 0)),
                "Draw": team.get("matchesDrawn", 0),   # only present in some series
                "NR": team.get("noResult", 0),         # only present in some series
                "Points": team.get("points", 0),
                "NRR": team.get("nrr", "0.000"),
                "Full Name": team.get("teamFullName", "")
            })

    return pd.DataFrame(points)
def fetch_upcoming_matches():
    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/upcoming"
    response = requests.get(url, headers=headers)
    data = response.json()

    matches = []
    for match_type in data.get("typeMatches", []):
        for series in match_type.get("seriesMatches", []):
            if "seriesAdWrapper" in series:
                series_info = series["seriesAdWrapper"]
                series_name = series_info.get("seriesName", "")
                for match in series_info.get("matches", []):
                    info = match.get("matchInfo", {})
                    team1 = info.get("team1", {}).get("teamName", "")
                    team2 = info.get("team2", {}).get("teamName", "")
                    venue = info.get("venueInfo", {}).get("ground", "")
                    start_date = info.get("startDate")
                    
                    # convert startDate to readable date
                    date_str = "N/A"
                    if start_date:
                        import datetime
                        date_str = datetime.datetime.fromtimestamp(int(start_date)/1000).strftime("%d %b %Y, %I:%M %p")

                    matches.append({
                        "desc": f"{team1} vs {team2} - {series_name}",
                        "series": series_name,
                        "status": info.get('status', 'N/A'),
                        "city":info.get('venueInfo',{}).get('city','N/A'),
                        "teams": f"{team1} vs {team2}",
                        "venue": venue,
                        "date": date_str,
                        "match_format":info.get('matchFormat',"N/A")
                    })
    return matches



import requests
import pandas as pd

# API Setup
url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"
headers = {
    "x-rapidapi-key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
    "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

response = requests.get(url, headers=headers)
data = response.json()


# --- Fetch live matches ---
def fetch_live_matches(data1):
    live_matches = []
    for match_type in data1.get("typeMatches", []):
        for series in match_type.get("seriesMatches", []):
            if "seriesAdWrapper" in series:
                for match in series["seriesAdWrapper"].get("matches", []):
                    info = match.get("matchInfo", {})
                    desc = f"{info.get('team1', {}).get('teamName', 'N/A')} vs {info.get('team2', {}).get('teamName', 'N/A')} - {info.get('matchDesc','')}"
                    match_id = info.get("matchId", None)
                    live_matches.append({"desc": desc, "matchId": match_id})
    return live_matches



def fetch_live_match_details(data1, selected_match):
    match_id = selected_match["matchId"]

    for match_type in data1.get('typeMatches', []):
        for series in match_type.get('seriesMatches', []):
            if 'seriesAdWrapper' in series:
                for match in series['seriesAdWrapper'].get('matches', []):
                    if match['matchInfo']['matchId'] == match_id:
                        info = match.get('matchInfo', {})
                        score = match.get('matchScore', {})
                        start_date = info.get("startDate")
                        # convert startDate to readable date
                        date_str = "N/A"
                        if start_date:
                            import datetime
                            date_str = datetime.datetime.fromtimestamp(int(start_date)/1000).strftime("%d %b %Y, %I:%M %p")
                        # Team scores
                        team1_score, team2_score = "Yet to bat", "Yet to bat"
                        t1 = score.get('team1Score', {}).get('inngs1', {})
                        if t1:
                            team1_score = f"{t1.get('runs','0')}/{t1.get('wickets','0')} ({t1.get('overs','0')})"
                        t2 = score.get('team2Score', {}).get('inngs1', {})
                        if t2:
                            team2_score = f"{t2.get('runs','0')}/{t2.get('wickets','0')} ({t2.get('overs','0')})"

                        # Fetch scorecard
                        url_scorecard = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{match_id}/hscard"
                        response2 = requests.get(url_scorecard, headers=headers)
                        scorecard_data = response2.json()

                        innings_data = []

                        # Loop through each innings in the scorecard
                        for innings in scorecard_data.get('scorecard', []):
                            team_name = innings['batteamname']
                            
                            # Process batsman data
                            batsman_list = []
                            for b in innings.get('batsman', []):
                                batsman_list.append({
                                    "Batsman": b.get("name"),
                                    "Runs": b.get("runs"),
                                    "Balls": b.get("balls"),
                                    "Fours": b.get("fours"),
                                    "Sixes": b.get("sixes")
                                })

                            # Process bowler data
                            bowler_list = []
                            for bw in innings.get('bowler', []):
                                bowler_list.append({
                                    "Bowler": bw.get("name"),
                                    "Overs": bw.get("overs"),
                                    "Maidens": bw.get("maidens"),
                                    "Runs": bw.get("runs"),
                                    "Wickets": bw.get("wickets")
                                })

                            innings_data.append({
                                "team": team_name,
                                "batting": pd.DataFrame(batsman_list),
                                "bowling": pd.DataFrame(bowler_list)
                            })

                        return {
                            "teams": f"{info['team1']['teamName']} vs {info['team2']['teamName']}",
                            "team1": info['team1']['teamName'],
                            "team2": info['team2']['teamName'],
                            "status": info.get('status', 'N/A'),
                            "venue": info.get('venueInfo', {}).get('ground', 'N/A'),
                            "city":info.get('venueInfo',{}).get('city','N/A'),
                            "date": date_str,
                            "score": f"{team1_score} | {team2_score}",
                            "innings_data": innings_data,  # <-- structured per innings
                            "scorecard_data": scorecard_data,
                            "match_format":info.get('matchFormat',"N/A")
                        }
    return None

def back_to_home():
    if st.button("🏠 Back to Home Page"):
        st.switch_page("pages/homepage.py")  
