import requests
headers = {
    "X-RapidAPI-Key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
    "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com"
}

import requests
import mysql.connector
import time

import requests
import mysql.connector
import time

def update_venues_tables(venue_ids, conn):
    cursor = conn.cursor()

    for venue_id in venue_ids:
        # Skip invalid IDs
        if not venue_id or not isinstance(venue_id, int):
            print(f"Skipping invalid venue_id: {venue_id}")
            continue

        # API request setup
        url = f"https://cricbuzz-cricket.p.rapidapi.com/venues/v1/{venue_id}"
        headers = {
            "x-rapidapi-key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
            "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
        }

        # Fetch venue data
        try:
            response = requests.get(url, headers=headers, timeout=10)
        except requests.exceptions.RequestException as e:
            print(f"Request failed for venue {venue_id}: {e}")
            continue

        if response.status_code != 200 or not response.text.strip():
            print(f"Bad response for venue {venue_id}, status code: {response.status_code}")
            continue

        try:
            venue_info = response.json()
        except Exception as e:
            print(f"Invalid JSON for venue {venue_id}: {e}")
            continue

        # Extract fields
        venue_name = venue_info.get("ground", "Unknown")
        city = venue_info.get("city", "")
        country = venue_info.get("country", "")

        # Capacity handling
        capacity = None
        capacity_raw = venue_info.get("capacity") or venue_info.get("profile", {}).get("capacity")

        if capacity_raw:
            try:
                if isinstance(capacity_raw, int):
                    capacity = capacity_raw
                elif isinstance(capacity_raw, str):
                    digits = "".join(c for c in capacity_raw if c.isdigit())
                    capacity = int(digits) if digits else None
            except Exception as e:
                print(f"Capacity parsing error for {venue_id}: {capacity_raw} -> {e}")
                capacity = None

        print(f"Venue {venue_id} raw capacity: {capacity_raw} | Parsed: {capacity}")

        # Insert or Update into DB
        try:
            cursor.execute("""
                INSERT INTO venues (venue_id, venue_name, city, country, capacity)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    venue_name = VALUES(venue_name),
                    city = VALUES(city),
                    country = VALUES(country),
                    capacity = VALUES(capacity)
            """, (venue_id, venue_name, city, country, capacity))
            conn.commit()
            print(f"Upserted venue: {venue_name}, {city}, {country}, {capacity}")
        except mysql.connector.Error as e:
            print(f"MySQL error for venue {venue_id}: {e}")
            continue

        # Avoid hitting API rate limits
        time.sleep(0.5)

def update_series_table(conn):
    import requests
    import mysql.connector
    from datetime import datetime

    # -------------------
    # Database connection
    # -------------------
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="2741",
        database="cricketdb"
    )
    cursor = conn.cursor()

    # -------------------
    # Create series table if not exists
    # -------------------
    create_table_query = """
    CREATE TABLE IF NOT EXISTS series (
        series_id INT PRIMARY KEY,
        series_name VARCHAR(255),
        host_country VARCHAR(100),
        start_date DATE,
        end_date DATE,
        total_matches INT
    )
    """
    cursor.execute(create_table_query)
    conn.commit()

    # -------------------
    # RapidAPI config
    # -------------------
    API_KEY = "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef"
    HEADERS = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }

    # -------------------
    # Fetch series list
    # -------------------
    series_url = "https://cricbuzz-cricket.p.rapidapi.com/series/v1/archives/international"
    try:
        series_response = requests.get(series_url, headers=HEADERS, timeout=10)
        series_response.raise_for_status()
        series_data = series_response.json()
    except requests.RequestException as e:
        print(f"Error fetching series list: {e}")
        series_data = {}
    except ValueError as e:  # JSON decode error
        print(f"Error parsing series JSON: {e}")
        series_data = {}

    # -------------------
    # Helper: get total matches for a series
    # -------------------
    def get_total_matches(series_id):
        url = f"https://cricbuzz-cricket.p.rapidapi.com/series/v1/{series_id}"
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            print(f"Error fetching matches for series {series_id}: {e}")
            return 0
        except ValueError as e:
            print(f"Error parsing matches JSON for series {series_id}: {e}")
            return 0

        total_matches = 0
        for item in data.get("matchDetails", []):
            match_map = item.get("matchDetailsMap")
            if match_map and "match" in match_map:
                total_matches += len(match_map["match"])
        return total_matches

    # -------------------
    # Insert series data
    # -------------------
    for year_block in series_data.get("seriesMapProto", []):
        for s in year_block.get("series", []):
            series_id = s["id"]
            series_name = s["name"]
            start_date = datetime.fromtimestamp(int(s["startDt"]) / 1000).strftime("%Y-%m-%d")
            end_date = datetime.fromtimestamp(int(s["endDt"]) / 1000).strftime("%Y-%m-%d")

            # Fetch host country from venues
            venue_url = f"https://cricbuzz-cricket.p.rapidapi.com/series/v1/{series_id}/venues"
            try:
                venue_response = requests.get(venue_url, headers=HEADERS, timeout=10)
                venue_response.raise_for_status()
                venue_data = venue_response.json()
                venues = venue_data.get("seriesVenue", [])
                host_country = venues[0].get("country") if venues else None
            except requests.RequestException as e:
                print(f"Warning: Could not fetch venues for series {series_id}: {e}")
                host_country = None
            except ValueError as e:
                print(f"Warning: Could not parse venue JSON for series {series_id}: {e}")
                host_country = None

            # Get total matches from matches API
            total_matches = get_total_matches(series_id)

            # Insert into DB
            insert_query = """
            INSERT INTO series (series_id, series_name, host_country, start_date, end_date, total_matches)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                series_name = VALUES(series_name),
                host_country = VALUES(host_country),
                start_date = VALUES(start_date),
                end_date = VALUES(end_date),
                total_matches = VALUES(total_matches)
            """
            cursor.execute(insert_query, (series_id, series_name, host_country, start_date, end_date, total_matches))
            conn.commit()
            print(f"Inserted/Updated series {series_name} with {total_matches} matches.")

    cursor.close()
    conn.close()
    print("Series table updated successfully!")

import json
import requests
from datetime import datetime

def update_match_table():
    import mysql.connector
    import requests
    from datetime import datetime

    # -----------------------
    # Database connection
    # -----------------------
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="2741",
        database="cricketdb"
    )
    cursor = conn.cursor()

    # -----------------------
    # Fetch latest matches
    # -----------------------
    def fetch_latest_matches():
        url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent"
        headers = {
            "X-RapidAPI-Key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
            "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers)
        return response.json() if response.status_code == 200 else {}

    # -----------------------
    # Batch insert helper
    # -----------------------
    def batch_insert(cursor, query, data_list, batch_size=20):
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i:i+batch_size]
            cursor.executemany(query, batch)
            conn.commit()  # commit per batch

    # -----------------------
    # Toss info
    # -----------------------
    def toss_decisions(match_id):
        url = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{match_id}"
        headers = {
            "x-rapidapi-key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
            "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers)
        data = response.json()

        team1 = data.get("team1", {})
        team2 = data.get("team2", {})
        toss_status = data.get("tossstatus", "")

        toss_winner_id = None
        toss_decision = None

        if toss_status:
            parts = toss_status.split(" opt to ")
            if len(parts) == 2:
                toss_winner_name = parts[0].strip()
                toss_decision = parts[1].strip().lower()
                if toss_winner_name == team1.get("teamname"):
                    toss_winner_id = team1.get("teamid")
                elif toss_winner_name == team2.get("teamname"):
                    toss_winner_id = team2.get("teamid")

        return toss_winner_id, toss_decision

    # -----------------------
    # Main loop: collect all data
    # -----------------------
    data = fetch_latest_matches()
    all_teams = set()
    all_venues = set()
    all_matches = []
    venues_ids = []

    for category in data.get("typeMatches", []):
        for series in category.get("seriesMatches", []):
            series_wrapper = series.get("seriesAdWrapper", {})
            series_id = series_wrapper.get("seriesId")
            series_name = series_wrapper.get("seriesName")

            for match in series_wrapper.get("matches", []):
                info = match.get("matchInfo", {})
                match_id = info.get("matchId")
                match_date_ts = info.get("startDate")
                match_date = datetime.fromtimestamp(int(match_date_ts)/1000).strftime("%Y-%m-%d %H:%M:%S") if match_date_ts else None
                description = info.get("matchDesc")
                venue_id = info.get("venueInfo", {}).get("id")
                venue_name = info.get("venueInfo", {}).get("ground")
                venues_ids.append(venue_id)

                team1 = info.get("team1", {})
                team2 = info.get("team2", {})

                team1_id = team1.get("teamId")
                team2_id = team2.get("teamId")

                # Winner info
                winner_team_id = None
                victory_margin = None
                victory_type = "NR"
                status = info.get("status", "")
                if "won by" in status:
                    parts = status.split(" won by ")
                    winner_team_name = parts[0].strip()
                    winner_team_id = team1_id if winner_team_name == info.get("team1", {}).get("teamName") else team2_id
                    margin_parts = parts[1].split(" ")
                    try:
                        victory_margin = int(margin_parts[0])
                        victory_type = margin_parts[1] if margin_parts[1].lower() in ["runs", "wickets"] else "NR"
                    except:
                        victory_margin = None

                # Toss info
                toss_winner_id, toss_decision = toss_decisions(match_id)

                # Collect teams
                for team in [team1, team2]:
                    t_id = team.get("teamId")
                    t_name = team.get("teamName")
                    if t_id and t_name:
                        all_teams.add((t_id, t_name))

                # Collect venues
                if venue_id and venue_name:
                    all_venues.add((venue_id, venue_name))

                # Collect matches
                all_matches.append((
                    match_id, series_id, match_date, description, venue_id,
                    team1_id, team2_id, winner_team_id, victory_margin, victory_type,
                    toss_winner_id, toss_decision
                ))

                # print("Collected:", description)

    # ------------------------
    # Insert all data safely
    # ------------------------
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")  # disable temporarily

    if all_teams:
        batch_insert(cursor, "INSERT IGNORE INTO teams (team_id, team_name) VALUES (%s, %s)", list(all_teams))
    if all_venues:
        batch_insert(cursor, "INSERT IGNORE INTO venues (venue_id, venue_name) VALUES (%s, %s)", list(all_venues))
    if all_matches:
        batch_insert(cursor, """
            INSERT INTO matches
            (match_id, series_id, match_date, description, venue_id, team1_id, team2_id,
             winner_team_id, victory_margin, victory_type, toss_winner_id, toss_decision)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                series_id=VALUES(series_id), match_date=VALUES(match_date), description=VALUES(description),
                venue_id=VALUES(venue_id), team1_id=VALUES(team1_id), team2_id=VALUES(team2_id),
                winner_team_id=VALUES(winner_team_id), victory_margin=VALUES(victory_margin),
                victory_type=VALUES(victory_type), toss_winner_id=VALUES(toss_winner_id),
                toss_decision=VALUES(toss_decision)
        """, all_matches, batch_size=20)

    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")  # enable back

    # print("All matches processed successfully.")
    # update_venues_tables(venues_ids, conn)

def top_odi(): #query3
    import json
    import requests
    import mysql.connector
    import mysql.connector
    import requests

    url = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/topstats/0"

    querystring = {"statsType":"mostRuns","matchType":"2"}

    headers = {
        "x-rapidapi-key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    player_ids =[]
    data = response.json()
    for player in data['values']:
        values = player['values']
        player_id = values[0]
        name = values[1]
        matches = values[2]
        innings = values[3]
        runs = values[4]
        avg = values[5]
        
        player_ids.append( player_id,
        )
    # -------------------------------
    # MySQL Connection
    # -------------------------------
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="2741",
        database="cricketdb"
    )
    cursor = conn.cursor()

    # -------------------------------
    # Step 1: Create Table
    # -------------------------------
    create_table_query = """
    CREATE TABLE IF NOT EXISTS top_odi_run_scorers (
        player_id INT PRIMARY KEY,
        player_name VARCHAR(100) NOT NULL,
        matches INT,
        innings INT,
        runs INT NOT NULL,
        batting_average DECIMAL(5,2),
        centuries INT
    );
    """
    cursor.execute(create_table_query)
    conn.commit()

    for player in player_ids:
        url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player}/batting"

        headers = {
            "x-rapidapi-key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
            "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers)
        data = response.json()

        player_name = data['appIndex']['seoTitle'].split(" Profile")[0]
        values = data['values']

        # Initialize variables
        matches = innings = runs = avg = hundreds = None

        for row in values:
            stat_name = row['values'][0]
            if stat_name == "Matches":
                matches = row['values'][2]  # ODI column
            elif stat_name == "Innings":
                innings = row['values'][2]
            elif stat_name == "Runs":
                runs = row['values'][2]
            elif stat_name == "Average":
                avg = row['values'][2]
            elif stat_name == "100s":
                hundreds = row['values'][2]

        # Prepare tuple for insertion
        player_tuple = (player, player_name, matches, innings, runs, avg, hundreds)

        # SQL Insert
        insert_query = """
        INSERT INTO top_odi_run_scorers
        (player_id, player_name, matches, innings, runs, batting_average, centuries)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        player_name=VALUES(player_name),
        matches=VALUES(matches),
        innings=VALUES(innings),
        runs=VALUES(runs),
        batting_average=VALUES(batting_average),
        centuries=VALUES(centuries);
        """

        cursor.execute(insert_query, player_tuple)
        conn.commit()

    cursor.close()
    conn.close()
def player_batting_stats_(): 
    import requests
    import mysql.connector
    url = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/topstats/0"

    querystring = {"statsType":"mostRuns","matchType":"2"}

    headers = {
            "x-rapidapi-key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
            "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
        }

    response = requests.get(url, headers=headers, params=querystring)
    player_ids =[]
    data = response.json()
    for player in data['values']:
            values = player['values']
            player_id = values[0]
            name = values[1]
            matches = values[2]
            innings = values[3]
            runs = values[4]
            avg = values[5]
            
            player_ids.append( player_id,
            )
    # MySQL connection
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="2741",
        database="cricketdb"
    )
    cursor = conn.cursor()

    # Make sure table includes 'format' column
    create_table_query = """
    CREATE TABLE IF NOT EXISTS player_batting_stats (
        player_id INT,
        player_name VARCHAR(100),
        format VARCHAR(10),
        matches INT,
        innings INT,
        runs INT,
        batting_average DECIMAL(5,2),
        centuries INT,
        PRIMARY KEY(player_id, format)
    );
    """
    cursor.execute(create_table_query)
    conn.commit()

    # Loop through player IDs
    for player in player_ids:
        url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player}/batting"
        headers = {
            "x-rapidapi-key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
            "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
        }
        
        response = requests.get(url, headers=headers)
        data = response.json()
        
        player_name = data['appIndex']['seoTitle'].split(" Profile")[0]
        headers_list = data['headers']  # ["ROWHEADER","Test","ODI","T20","IPL"]
        values = data['values']

        # Loop through formats (skip first column, which is row header)
        for col_index in range(1, len(headers_list)):
            format_name = headers_list[col_index]
            matches = innings = runs = avg = hundreds = None

            for row in values:
                stat_name = row['values'][0]
                stat_value = row['values'][col_index]  # value for this format

                if stat_name == "Matches":
                    matches = stat_value
                elif stat_name == "Innings":
                    innings = stat_value
                elif stat_name == "Runs":
                    runs = stat_value
                elif stat_name == "Average":
                    avg = stat_value
                elif stat_name == "100s":
                    hundreds = stat_value

            # Insert into MySQL
            player_tuple = (player, player_name, format_name, matches, innings, runs, avg, hundreds)
            insert_query = """
            INSERT INTO player_batting_stats
            (player_id, player_name, format, matches, innings, runs, batting_average, centuries)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            player_name=VALUES(player_name),
            matches=VALUES(matches),
            innings=VALUES(innings),
            runs=VALUES(runs),
            batting_average=VALUES(batting_average),
            centuries=VALUES(centuries);
            """
            cursor.execute(insert_query, player_tuple)
            print("inserted")
            conn.commit()

    cursor.close()
    conn.close()
def query_7():
    import requests
    import mysql.connector

    # ------------------------
    # MySQL Connection
    # ------------------------
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="2741",
        database="cricketdb"
    )
    cursor = conn.cursor()

    # ------------------------
    # Create table if not exists
    # ------------------------
    create_table_query = """
    CREATE TABLE IF NOT EXISTS highest_scores (
        id INT AUTO_INCREMENT PRIMARY KEY,
        format VARCHAR(10),
        player_name VARCHAR(100),
        highest_score INT,
        balls INT,
        strike_rate DECIMAL(6,2),
        opposition VARCHAR(50)
    )
    """
    cursor.execute(create_table_query)

    # ------------------------
    # Fetch data from API
    # ------------------------
    url = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/topstats/0"
    headers = {
        "x-rapidapi-key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }

    formats = {
        "Test": "1",
        "ODI": "2",
        "T20": "3"
    }

    for fmt, match_type in formats.items():
        querystring = {"statsType":"highestScore","matchType":match_type}
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
        
        for player in data['values']:
            try:
                hs = int(player['values'][0])
                name = player['values'][1]
                balls = int(player['values'][2]) if player['values'][2] else None
                sr = float(player['values'][3]) if player['values'][3] else None
                opposition = player['values'][-1]
                
                insert_query = """
                INSERT INTO highest_scores (format, player_name, highest_score, balls, strike_rate, opposition)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (fmt, name, hs, balls, sr, opposition))
            except Exception as e:
                print("Skipping row due to error:", e)

    # Commit and close
    cursor.close()
    conn.close()

    print("Data inserted successfully!")
# SELECT 
#     format,
#     player_name,
#     highest_score,
#     balls,
#     strike_rate,
#     opposition
# FROM highest_scores hs
# WHERE (format, highest_score) IN (
#     SELECT 
#         format,
#         MAX(highest_score)
#     FROM highest_scores
#     GROUP BY format
# )
# ORDER BY format;
# /---------------------------------------------------------------------------------------------------------------------------------------

def all_rounder_stats():
    import requests
    import mysql.connector

    # --- MySQL connection ---
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="2741",
        database="cricketdb"
    )
    cursor = conn.cursor()

    # --- Create table if not exists ---
    create_table_query = """
    CREATE TABLE IF NOT EXISTS all_rounders_stats (
        player_id INT,
        player_name VARCHAR(100),
        format VARCHAR(10),
        runs INT,
        batting_average DECIMAL(5,2),
        centuries INT,
        wickets INT,
        bowling_average DECIMAL(5,2),
        economy DECIMAL(5,2),
        PRIMARY KEY(player_id, format)
    );
    """
    cursor.execute(create_table_query)
    conn.commit()

    # --- Fetch all-rounder player IDs ---
    cursor.execute("SELECT player_id FROM players WHERE role LIKE '%Allrounder%'")
    player_ids = [row[0] for row in cursor.fetchall()]  #type:ignore

    headers = {
        "x-rapidapi-key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }

    # --- Safe conversion functions ---
    def safe_int(x):
        try:
            return int(x)
        except:
            return None

    def safe_float(x):
        try:
            return float(x)
        except:
            return None

    # --- Process each player ---
    for player_id in player_ids:
        try:
            # Fetch batting stats
            bat_url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}/batting"
            bat_data = requests.get(bat_url, headers=headers).json()

            # Skip if data missing
            if 'appIndex' not in bat_data or 'values' not in bat_data:
                print(f"Skipping player {player_id} – no batting data")
                continue

            # Fetch bowling stats
            bowl_url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}/bowling"
            bowl_data = requests.get(bowl_url, headers=headers).json()

            if 'values' not in bowl_data:
                print(f"Skipping player {player_id} – no bowling data")
                continue

            # Player name
            player_name = bat_data.get('appIndex', {}).get('seoTitle', '').replace(" Profile", "")

            headers_list = bat_data['headers']  # ["ROWHEADER","Test","ODI","T20","IPL"]
            bat_values = bat_data['values']
            bowl_values = bowl_data['values']

            # --- Loop through each format ---
            for col_index in range(1, len(headers_list)):
                format_name = headers_list[col_index]

                # Batting stats
                runs = avg = hundreds = None
                for row in bat_values:
                    if row['values'][0] == "Runs":
                        runs = safe_int(row['values'][col_index])
                    elif row['values'][0] == "Average":
                        avg = safe_float(row['values'][col_index])
                    elif row['values'][0] == "100s":
                        hundreds = safe_int(row['values'][col_index])

                # Bowling stats
                wickets = bowl_avg = econ = None
                for row in bowl_values:
                    if row['values'][0] == "Wickets":
                        wickets = safe_int(row['values'][col_index])
                    elif row['values'][0] == "Avg":
                        bowl_avg = safe_float(row['values'][col_index])
                    elif row['values'][0] == "Eco":
                        econ = safe_float(row['values'][col_index])

                # --- Insert into MySQL ---
                player_tuple = (player_id, player_name, format_name, runs, avg, hundreds, wickets, bowl_avg, econ)
                insert_query = """
                INSERT INTO all_rounders_stats
                (player_id, player_name, format, runs, batting_average, centuries, wickets, bowling_average, economy)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                player_name=VALUES(player_name),
                runs=VALUES(runs),
                batting_average=VALUES(batting_average),
                centuries=VALUES(centuries),
                wickets=VALUES(wickets),
                bowling_average=VALUES(bowling_average),
                economy=VALUES(economy);
                """
                cursor.execute(insert_query, player_tuple) #type:ignore

            # Commit once per player
            conn.commit()
            print(f"Inserted stats for player: {player_name}")

        except Exception as e:
            print(f"Error for player {player_id}: {e}")

    cursor.close()
    conn.close()

    #SELECT player_name, SUM(runs) AS total_runs, SUM(wickets) AS total_wickets
    # FROM all_rounders_stats
    # GROUP BY player_name

    cursor.close()
    conn.close()
    print("Done!")
# ----------------------------------------------------------------------------------------------
def player_batting_stats():  # query 11
    import requests
    import mysql.connector

    # -------------------
    # Step 1: Fetch top players (just to get IDs)
    # -------------------
    url = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/topstats/0"
    querystring = {"statsType": "mostRuns"}  # You said you'll remove matchType

    headers = {
        "x-rapidapi-key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    player_ids = []
    data = response.json()

    for player in data.get("values", []):
        values = player["values"]
        player_id = values[0]
        player_ids.append(player_id)   # ✅ fixed

    # -------------------
    # Step 2: MySQL connection
    # -------------------
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="2741",
        database="cricketdb"
    )
    cursor = conn.cursor()

    # Create table if not exists
    create_table_query = """
    CREATE TABLE IF NOT EXISTS player_batting_stats (
        player_id INT,
        player_name VARCHAR(100),
        format VARCHAR(10),
        matches INT,
        innings INT,
        runs INT,
        batting_average DECIMAL(6,2),
        centuries INT,
        PRIMARY KEY(player_id, format)
    );
    """
    cursor.execute(create_table_query)
    conn.commit()

    # -------------------
    # Step 3: Loop through players → fetch stats
    # -------------------
    for player in player_ids:
        url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player}/batting"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"⚠️ Error fetching stats for player {player}: {e}")
            continue

        if "headers" not in data or "values" not in data:
            continue

        player_name = data.get("appIndex", {}).get("seoTitle", "").split(" Profile")[0]
        headers_list = data["headers"]  # ["ROWHEADER","Test","ODI","T20I","IPL"]
        values = data["values"]

        # Loop through formats
        for col_index in range(1, len(headers_list)):
            format_name = headers_list[col_index]

            # ✅ Optional: skip IPL if you only want international
            if format_name not in ["Test", "ODI", "T20I"]:
                continue

            matches = innings = runs = avg = hundreds = None

            for row in values:
                stat_name = row["values"][0]
                stat_value = row["values"][col_index]

                if stat_value in ["-", "", None]:
                    continue

                if stat_name == "Matches":
                    matches = int(stat_value)
                elif stat_name == "Innings":
                    innings = int(stat_value)
                elif stat_name == "Runs":
                    runs = int(stat_value)
                elif stat_name == "Average":
                    try:
                        avg = float(stat_value)
                    except:
                        avg = None
                elif stat_name == "100s":
                    hundreds = int(stat_value)

            # Insert into DB
            player_tuple = (player, player_name, format_name, matches, innings, runs, avg, hundreds)
            insert_query = """
            INSERT INTO player_batting_stats
            (player_id, player_name, format, matches, innings, runs, batting_average, centuries)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            player_name=VALUES(player_name),
            matches=VALUES(matches),
            innings=VALUES(innings),
            runs=VALUES(runs),
            batting_average=VALUES(batting_average),
            centuries=VALUES(centuries);
            """
            cursor.execute(insert_query, player_tuple)
            conn.commit()
            print(f"✅ Inserted/Updated {player_name} ({format_name})")

    cursor.close()
    conn.close()
    print("All player batting stats updated successfully!")
#SELECT 
#     p.player_id,
#     p.player_name,
#     MAX(CASE WHEN p.format = 'Test' THEN p.runs ELSE 0 END) AS Test_Runs,
#     MAX(CASE WHEN p.format = 'ODI' THEN p.runs ELSE 0 END) AS ODI_Runs,
#     MAX(CASE WHEN p.format = 'T20I' THEN p.runs ELSE 0 END) AS T20I_Runs,
#     ROUND(AVG(p.batting_average), 2) AS Overall_Batting_Avg,
#     COUNT(DISTINCT p.format) AS Formats_Played
# FROM 
#     player_batting_stats p
# GROUP BY 
#     p.player_id, p.player_name
# HAVING 
#     Formats_Played >= 2
# ORDER BY 
#     Overall_Batting_Avg DESC;


#-------------------------------------------- query 12:----------------------------------------------
# SELECT 
#     t.team_id,
#     t.team_name,
#     SUM(CASE WHEN v.country = t.country AND m.winner_team_id = t.team_id THEN 1 ELSE 0 END) AS home_wins,
#     SUM(CASE WHEN v.country <> t.country AND m.winner_team_id = t.team_id THEN 1 ELSE 0 END) AS away_wins
# FROM matches m
# JOIN teams t 
#     ON m.winner_team_id = t.team_id
# JOIN venues v 
#     ON m.venue_id = v.venue_id
# GROUP BY t.team_id, t.team_name
# ORDER BY t.team_name;

# ------------------------------------------------------------------------------------------------------

def query_13():
    import mysql.connector

    import requests

    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent"

    headers = {
        "x-rapidapi-key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    match_ids = []
    partnership_data = []

    for matches in data.get("typeMatches", []):
        for series in matches.get("seriesMatches", []):
            wrapper = series.get("seriesAdWrapper")
            if wrapper:
                for match in wrapper.get('matches', []):
                    info = match.get("matchInfo", {})
                    match_id = info.get("matchId")
                    if match_id:
                        match_ids.append(match_id)

    for p in match_ids:
        scurl = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{p}/hscard"
        response = requests.get(scurl, headers=headers)
        res = response.json()
        
        for innings in res.get("scorecard", []):   # check spelling: 'scorcard' or 'scorecard'?
            innings_id = innings.get("inningsid")
            partnerships = innings.get("partnership", {}).get("partnership", [])
            for data in partnerships:
                bat1id = data.get("bat1id")
                bat1name = data.get("bat1name")
                bat2id = data.get("bat2id")
                bat2name = data.get("bat2name")
                total_runs = data.get("totalruns")
                balls_faced = data.get("totalballs")

                partnership_data.append({
                    "match_id": p,
                    "innings_id": innings_id,
                    "bat1id": bat1id,
                    "bat1name": bat1name,
                    "bat2id": bat2id,
                    "bat2name": bat2name,
                    "total_runs": total_runs,
                    "total_balls": balls_faced
                })


    # --- Connect to MySQL ---
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="2741",
        database="cricketdb"
    )

    cursor = conn.cursor()

    # --- Create table ---
    create_table_query = """
    CREATE TABLE IF NOT EXISTS partnerships (
        id INT AUTO_INCREMENT PRIMARY KEY,
        match_id BIGINT NOT NULL,
        innings_id INT NOT NULL,
        bat1id BIGINT,
        bat1name VARCHAR(100),
        bat2id BIGINT,
        bat2name VARCHAR(100),
        total_runs INT,
        total_balls INT
    );
    """

    cursor.execute(create_table_query)
    conn.commit()

    # --- Insert data ---
    insert_query = """
    INSERT INTO partnerships (
        match_id, innings_id, bat1id, bat1name, bat2id, bat2name, total_runs, total_balls
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    # Example: partnership_data is the list of dictionaries you collected
    for p in partnership_data:
        cursor.execute(insert_query, (
            p["match_id"],
            p["innings_id"],
            p.get("bat1id"),
            p.get("bat1name"),
            p.get("bat2id"),
            p.get("bat2name"),
            p.get("total_runs"),
            p.get("total_balls")
        ))
        conn.commit()




    print(f"{cursor.rowcount} records inserted into partnerships table.")

    # --- Close connection ---
    cursor.close()
    conn.close()
# ---------------------------------------------------------------------------------

def query_14():
    import requests
    import mysql.connector
    headers = {
        "x-rapidapi-key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }
    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent"

    headers = {
            "x-rapidapi-key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
            "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
        }

    response = requests.get(url, headers=headers)
    data = response.json()

    match_ids = []
    bowling_data = []

    for matches in data.get("typeMatches", []):
            for series in matches.get("seriesMatches", []):
                wrapper = series.get("seriesAdWrapper")
                if wrapper:
                    for match in wrapper.get('matches', []):
                        info = match.get("matchInfo", {})
                        match_id = info.get("matchId")
                        venue_id = info.get("venueInfo").get("id")
                        if match_id:
                            match_ids.append(match_id)
                            

    # list of match_ids you already have
                            scurl = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{match_id}/hscard"
                            response = requests.get(scurl, headers=headers)
                            res = response.json()
                            
                            for innings in res.get("scorecard", []):  # check key spelling
                                for bowler in innings.get("bowler", []):
                                    overs = float(bowler.get("overs", 0))
                                    if overs >= 4:
                                        bowling_data.append({
                                            "match_id": match_id,
                                            "venue_id": venue_id,
                                            "bowler_id": bowler.get("id"),
                                            "bowler_name": bowler.get("name"),
                                            "overs": overs,
                                            "runs": bowler.get("runs"),
                                            "wickets": bowler.get("wickets"),
                                            "economy": float(bowler.get("economy")) if bowler.get("economy") else None
                                        })

        # Connect to MySQL
    conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="2741",
            database="cricketdb"
        )
    cursor = conn.cursor()

        # Create table if not exists
    create_table_query = """
        CREATE TABLE IF NOT EXISTS bowling_performance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            match_id BIGINT,
            venue_id BIGINT,
            bowler_id BIGINT,
            bowler_name VARCHAR(100),
            overs FLOAT,
            runs INT,
            wickets INT,
            economy FLOAT
        );
        """
    cursor.execute(create_table_query)
    conn.commit()

        # Insert query
    insert_query = """
        INSERT INTO bowling_performance (
            match_id, venue_id, bowler_id, bowler_name, overs, runs, wickets, economy
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Insert each record
    for b in bowling_data:
            cursor.execute(insert_query, (
                b.get("match_id"),
                b.get("venue_id"),
                b.get("bowler_id"),
                b.get("bowler_name"),
                b.get("overs"),
                b.get("runs"),
                b.get("wickets"),
                b.get("economy")
            ))
            conn.commit()
            print(f"{cursor.rowcount} records inserted into bowling_performance table.")

        # Close connection
    cursor.close()
    conn.close()

# SELECT
#     venue_id,
#     bowler_id,
#     bowler_name,
#     COUNT(DISTINCT match_id) AS matches_played,
#     SUM(wickets) AS total_wickets,
#     SUM(economy * overs) / SUM(overs) AS avg_economy
# FROM bowling_performance
# WHERE overs >= 4
# GROUP BY venue_id, bowler_id, bowler_name
# HAVING COUNT(DISTINCT match_id) >= 3
# ORDER BY venue_id, total_wickets DESC;
# -------------------------------------------------------------------------------------------------------------------------
def query_15():
    import mysql.connector
    import requests
    import time
    import mysql.connector

    # -------------------
    # DB Connection
    # -------------------
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="2741",
        database="cricketdb"
    )
    cursor = conn.cursor()

    # -------------------
    # Create Table Query
    # -------------------
    create_table_query = """
    CREATE TABLE match_player_stats (
        id INT AUTO_INCREMENT PRIMARY KEY,
        match_id BIGINT NOT NULL,
        player_id INT NOT NULL,
        player_name VARCHAR(100) NOT NULL,
        runs_scored INT DEFAULT 0,
        balls_faced INT DEFAULT 0,
        fours INT DEFAULT 0,
        sixes INT DEFAULT 0,
        strike_rate DECIMAL(6,2) DEFAULT 0.00,
        team_name VARCHAR(50) DEFAULT 'Unknown',
        bat_team_id INT NOT NULL,
        team_won_id INT NOT NULL,
        win_margin INT DEFAULT 0,
        win_by_runs TINYINT(1) DEFAULT 0,
        win_by_innings TINYINT(1) DEFAULT 0,
        INDEX idx_match_id (match_id),
        INDEX idx_player_id (player_id)
    );

    """

    cursor.execute(create_table_query)
    conn.commit()

    cursor.close()
    conn.close()

    print("✅ match_player_stats table created successfully!")
    # -------------------
    # DB Connection
    # -------------------
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="2741",
        database="cricketdb"
    )
    cursor = conn.cursor()

    # -------------------
    # API Config
    # -------------------
    HEADERS = {
        "x-rapidapi-key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }

    # -------------------
    # Insert Query
    # -------------------
    INSERT_QUERY = """
    INSERT INTO match_player_stats
    (match_id, player_id, player_name, runs_scored, balls_faced, fours, sixes, strike_rate,
    team_name, bat_team_id, team_won_id, win_margin, win_by_runs, win_by_innings)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    # -------------------
    # Fetch recent matches
    # -------------------
    recent_url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent"
    resp = requests.get(recent_url, headers=HEADERS)
    matches_data = resp.json()

    match_ids = []

    for match_type in matches_data.get("typeMatches", []):
        for series in match_type.get("seriesMatches", []):
            wrapper = series.get("seriesAdWrapper")
            if not wrapper:
                continue
            for match in wrapper.get("matches", []):
                match_info = match.get("matchInfo", {})
                match_id = match_info.get("matchId")
                if match_id:
                    match_ids.append(match_id)

    print(f"Found {len(match_ids)} recent matches.")

    # -------------------
    # Helper function to insert player safely
    # -------------------
    def insert_player(match_id, player, team_name, bat_team_id, team_won_id, win_margin, win_by_runs, win_by_innings):
        if not player:
            return
        try:
            cursor.execute(INSERT_QUERY, (
                match_id,
                player.get("id") or 0,
                player.get("name") or "Unknown",
                int(player.get("runs", 0)),
                int(player.get("balls", 0)),
                int(player.get("fours", 0)),
                int(player.get("sixes", 0)),
                float(player.get("strkrate") or 0.0),
                team_name,
                bat_team_id,
                team_won_id,
                win_margin,
                win_by_runs,
                win_by_innings
            ))
        except Exception as e:
            print(f"❌ Error inserting player {player.get('name')}: {e}")

    # -------------------
    # Process each match
    # -------------------
    for match_id in match_ids:
        try:
            scurl = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{match_id}/leanback"
            response = requests.get(scurl, headers=HEADERS)
            sc_data = response.json()

            miniscore = sc_data.get("miniscore", {})
            match_header = sc_data.get("matchheaders", {})

            # -------------------
            # Team info
            # -------------------
            team_details = match_header.get("teamdetails", {})
            bat_team_id = team_details.get("batteamid") or 0
            bat_team_name = team_details.get("batteamname") or "Unknown"
            bowl_team_id = team_details.get("bowlteamid") or 0
            bowl_team_name = team_details.get("bowlteamname") or "Unknown"

            winning_team_id = match_header.get("winningteamid") or 0

            # -------------------
            # Winning info
            # -------------------
            innings_list = miniscore.get("inningsscores", {}).get("inningsscore", [])
            win_by_runs = 0
            win_by_innings = 0
            win_margin = 0

            if len(innings_list) >= 2:
                first_innings = innings_list[1]  # team batted first
                second_innings = innings_list[0]  # team batted second

                first_score = int(first_innings.get("runs", 0))
                second_score = int(second_innings.get("runs", 0))
                second_wickets = int(second_innings.get("wickets", 0))

                if winning_team_id == first_innings.get("batteamid"):
                    win_by_runs = 1
                    win_by_innings = 0
                    win_margin = first_score - second_score
                elif winning_team_id == second_innings.get("batteamid"):
                    win_by_runs = 0
                    win_by_innings = 0
                    win_margin = 10 - second_wickets
                else:
                    win_by_runs = 0
                    win_by_innings = 1
                    win_margin = abs(first_score - second_score)

            # -------------------
            # Insert striker and non-striker with bat_team_id & team_won_id
            # -------------------
            insert_player(match_id, miniscore.get("batsmanstriker"), bat_team_name, bat_team_id, winning_team_id, win_margin, win_by_runs, win_by_innings)
            insert_player(match_id, miniscore.get("batsmannonstriker"), bat_team_name, bat_team_id, winning_team_id, win_margin, win_by_runs, win_by_innings)

            conn.commit()
            print(f"✅ Inserted players for match {match_id}")

            # Small delay to avoid API rate limits
            time.sleep(0.5)

        except Exception as e:
            print(f"❌ Error processing match {match_id}: {e}")
            continue

    # -------------------
    # Close DB
    # -------------------
    cursor.close()
    conn.close()
    print("✅ All done!")

# SELECT 
#     player_id,
#     player_name,
#     COUNT(*) AS close_matches_played,
#     ROUND(AVG(runs_scored), 2) AS avg_runs_in_close,
#     SUM(CASE 
#             WHEN bat_team_id = team_won_id THEN 1 
#             ELSE 0 
#         END) AS close_matches_won
# FROM match_player_stats
# WHERE 
#     (win_by_runs = 1 AND win_margin < 50)    -- close by runs
#     OR
#     (win_by_runs = 0 AND win_margin < 5)     -- close by wickets
# GROUP BY player_id, player_name
# ORDER BY avg_runs_in_close DESC;
# ---------------------------------------------------------------------------------------------------------------------------------------
def query_16():
    import requests
    import mysql.connector

    # Database connection
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="2741",
        database="cricketdb"
    )
    cursor = conn.cursor()

    url = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/topstats/0"
    headers = {
        "x-rapidapi-key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }

    top_teams_ids = [1,2,3,4,5,6,7,8,9,10]
    years = [2020,2021,2022,2023,2024,2025]

    for year in years:
        for team_id in top_teams_ids:
            # 1️⃣ Fetch highestAvg stats
            query_avg = {"statsType": "highestAvg", "year": str(year), "team": str(team_id)}
            response_avg = requests.get(url, headers=headers, params=query_avg)
            data_avg = response_avg.json()
            
            # Build dict: player_id -> info from highestAvg
            avg_dict = {}
            for val in data_avg.get('values', []):
                values = val.get('values')
                player_id = values[0]
                player_name = values[1]
                matches_played_avg = int(values[2])  # matches from highestAvg
                avg_runs = float(values[5])
                avg_dict[player_id] = {
                    "player_name": player_name,
                    "matches_played_avg": matches_played_avg,
                    "avg_runs": avg_runs
                }

            # 2️⃣ Fetch highestSr stats
            query_sr = {"statsType": "highestSr", "year": str(year), "team": str(team_id)}
            response_sr = requests.get(url, headers=headers, params=query_sr)
            data_sr = response_sr.json()
            
            # Build dict: player_id -> strike_rate info
            sr_dict = {}
            for val in data_sr.get('values', []):
                values = val.get('values')
                player_id = values[0]
                matches_played_sr = int(values[2])  # matches from SR
                strike_rate = float(values[5])  # correct index for SR in JSON
                sr_dict[player_id] = {
                    "strike_rate": strike_rate,
                    "matches_played_sr": matches_played_sr
                }

            # 3️⃣ Merge data and calculate weighted strike rate
            for player_id, info in avg_dict.items():
                player_name = info["player_name"]
                matches_played = info["matches_played_avg"]  # use avg matches
                avg_runs = info["avg_runs"]

                # Weighted strike rate (matches weighted)
                sr_info = sr_dict.get(player_id)
                if sr_info:
                    weighted_sr = round((sr_info["strike_rate"] * sr_info["matches_played_sr"]) / sr_info["matches_played_sr"], 2)
                else:
                    weighted_sr = 0

                # 4️⃣ Insert/update table
                insert_query = """
                    INSERT INTO player_yearly_stats 
                    (player_id, player_name, year, matches_played, team_id, avg_runs, avg_strike_rate)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                        matches_played = VALUES(matches_played),
                        avg_runs = VALUES(avg_runs),
                        avg_strike_rate = VALUES(avg_strike_rate)
                """
                cursor.execute(insert_query, (player_id, player_name, year, matches_played, team_id, avg_runs, weighted_sr))
                conn.commit()
                print("done",player_name)

    cursor.close()
    conn.close()

    print("Data inserted/updated successfully with weighted strike rate!")
# select * from player_yearly_stats where matches_played>5;
# ----------------------------------------------------------------------------------------------------------------------------------
def query_17():
    import requests
    import mysql.connector

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="2741",
        database="cricketdb"
    )
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO toss_analysis (match_id, toss_winner_id, toss_decision, winner_id)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE 
        toss_winner_id = VALUES(toss_winner_id),
        toss_decision = VALUES(toss_decision),
        winner_id = VALUES(winner_id);
    """
    headers = {
        "x-rapidapi-key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }
    recent_url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent"
    resp = requests.get(recent_url, headers=headers)
    matches_data = resp.json()


    for match_type in matches_data.get("typeMatches", []):
            for series in match_type.get("seriesMatches", []):
                wrapper = series.get("seriesAdWrapper")
                if not wrapper:
                    continue
                for match in wrapper.get("matches", []):
                    match_info = match.get("matchInfo", {})
                    match_id = match_info.get("matchId")
                    if match_id:
                        scurl = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{match_id}/leanback"
                        scresponse = requests.get(scurl, headers=headers)
                        scdata = scresponse.json()
                        matchheaders = scdata.get('matchheaders') or scdata.get('matchHeader')
                        if not matchheaders:
                            print("No matchheaders for match", match_id)
                            continue

                        toss_results = matchheaders.get('tossresults') or matchheaders.get('tossResults')
                        if not toss_results:
                            print("No toss results for match", match_id)
                            tosswinnerid, toss_decision = None, None
                        else:
                            tosswinnerid = toss_results.get('tosswinnerid') or toss_results.get('tossWinnerId')
                            toss_decision = toss_results.get('decision')

                        winningteamid = matchheaders.get('winningteamid') or matchheaders.get('winningTeamId')
                        print(match_id, tosswinnerid, toss_decision, winningteamid)

                        try:
                            cursor.execute(insert_query, (
                                match_id,
                                tosswinnerid,
                                toss_decision,
                                winningteamid
                            ))
                        except Exception as e:
                            print("Insert error:", match_id, e)

    conn.commit()
    cursor.close()
    conn.close()
# SELECT 
#     toss_decision,
#     COUNT(*) AS total_matches,
#     SUM(CASE WHEN toss_winner_id = winner_id THEN 1 ELSE 0 END) AS matches_won_by_toss_winner,
#     ROUND(100.0 * SUM(CASE WHEN toss_winner_id = winner_id THEN 1 ELSE 0 END) / COUNT(*), 2) AS win_percentage
# FROM toss_analysis
# GROUP BY toss_decision;
# -------------------------------------------------------------------------------------------------------------------------------
def query_18():
    import requests
    import mysql.connector
    import mysql.connector

    # -------------------
    # DB Connection
    # -------------------
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="2741",
        database="cricketdb"
    )
    cursor = conn.cursor()

    # -------------------
    # Create Table Query
    # -------------------
    create_table_query = """
    CREATE TABLE player_bowling_stats (
        id INT AUTO_INCREMENT PRIMARY KEY,
        player_id INT NOT NULL,
        player_name VARCHAR(100) NOT NULL,
        match_type VARCHAR(10) NOT NULL,  -- "odi" or "t20"
        matches INT,
        overs DECIMAL(7,2),
        wickets INT,
        economy DECIMAL(5,2)
    );


    """

    cursor.execute(create_table_query)
    conn.commit()

    cursor.close()
    conn.close()

    print("✅ match_player_stats table created successfully!")

    # Connect to your MySQL
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="2741",
        database="cricketdb"
    )
    cursor = conn.cursor()

    matchtype =[2,3]  # 2 = ODI, 3 = T20

    insert_query = """
    INSERT INTO player_bowling_stats
    (player_id, player_name, match_type, matches, overs, wickets, economy)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    for type in matchtype:
        url = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/topstats/0"
        querystring = {"statsType":"lowestEcon","matchType":f"{type}"}
        headers = {
            "x-rapidapi-key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
            "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)
        bowl_stats = response.json()

        for val in bowl_stats.get('values', []):
            player_id = val.get('values')[0]
            player_name = val.get('values')[1]
            matches = val.get('values')[2]
            overs = val.get('values')[3]
            wickets = val.get('values')[4]
            economy = val.get('values')[5]
            match_name = "odi" if type == 2 else "t20"
            cursor.execute(insert_query, (
                player_id,
                player_name,
                match_name,
                matches,
                overs,
                wickets,
                economy
            ))

    # Commit and close
    conn.commit()
    cursor.close()
    conn.close()


# SELECT
#     player_id,
#     player_name,
#     match_type,
#     matches,
#     overs,
#     wickets,
#     economy
# FROM
#     player_bowling_stats
# WHERE
#     match_type IN ('odi', 't20')
#     AND matches >= 10
#     AND (overs / matches) >= 2
# ORDER BY
#     economy ASC,
#     wickets DESC;
# -------------------------------------------------------------------------------------------------------------------------
def query_19():
    import requests
    from datetime import datetime

    series_ids_22_25 = [3961,4499,6906,5917,7476,9129,9315,10587]
    match_ids = []  # store tuples of (matchId, matchDate)
    match_dates=[]
    headers = {
        "x-rapidapi-key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }

    for series_id in series_ids_22_25:
        url = f"https://cricbuzz-cricket.p.rapidapi.com/series/v1/{series_id}"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Series {series_id} failed with status {response.status_code}")
            continue

        try:
            seriesdata = response.json()
        except Exception as e:
            print(f"Series {series_id} JSON decode failed: {e}")
            continue

        for detail in seriesdata.get("matchDetails", []):
            match_details_map = detail.get("matchDetailsMap", {})
            if isinstance(match_details_map, list):
                mdm_list = match_details_map
            else:
                mdm_list = [match_details_map]

            for mdm in mdm_list:
                for match in mdm.get("match", []):
                    match_info = match.get("matchInfo", {})
                    match_id = match_info.get("matchId")
                    start_date_ms = match_info.get("startDate")
                    if match_id and start_date_ms:
                        # Convert milliseconds since epoch to YYYY-MM-DD
                        match_date = datetime.fromtimestamp(int(start_date_ms)/1000).strftime("%Y-%m-%d")
                        match_ids.append(match_id)
                        match_dates.append(match_date)
    import requests

    # Example match_ids list
    batsman_stats = []

    headers = {
        "x-rapidapi-key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }

    for match_id, match_date in zip(match_ids, match_dates):

        url = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{match_id}/hscard"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Match {match_id} failed with status {response.status_code}")
            continue
        
        try:
            match_data = response.json()
        except Exception as e:
            print(f"Match {match_id} JSON decode failed: {e}")
            continue
        
        # Loop through innings
        for inning in match_data.get("scorecard", []):
            for batsman in inning.get("batsman", []):
                batsman_stats.append({
                    "player_id": batsman.get("id"),
                    "player_name": batsman.get("name"),
                    "runs": batsman.get("runs"),
                    "balls": batsman.get("balls"),
                    "match_id":match_id,
                    "match_date":match_date

                })

    # Example output
    for stat in batsman_stats[:10]:  # show first 10
        print(stat)
    import mysql.connector

    # -------------------
    # DB Connection
    # -------------------
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="2741",
        database="cricketdb"
    )
    cursor = conn.cursor()

    # -------------------
    # Create Table Query
    # -------------------
    create_table_query = """
    CREATE TABLE batsman_stats_22_25 (
        id INT AUTO_INCREMENT PRIMARY KEY,
        player_id INT NOT NULL,
        player_name VARCHAR(100) NOT NULL,
        runs INT NOT NULL,
        balls INT NOT NULL,
        match_date DATE NOT NULL,
        match_id INT NOT NULL
    );


    """

    cursor.execute(create_table_query)
    conn.commit()

    cursor.close()
    conn.close()

    print("✅ match_player_stats table created successfully!")
    import mysql.connector

    # Connect to your DB
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="2741",
        database="cricketdb"
    )
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO batsman_stats_22_25 (player_id, player_name, runs, balls, match_date, match_id)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    for stat in batsman_stats:
        cursor.execute(insert_query, (
            stat["player_id"],
            stat["player_name"],
            stat["runs"],
            stat["balls"],
            stat["match_date"],
            stat["match_id"]
        ))

    conn.commit()
    cursor.close()
    conn.close()

# # SELECT 
#     player_id,
#     player_name,
#     COUNT(*) AS innings_count,
#     AVG(runs) AS avg_runs,
#     STDDEV(runs) AS std_dev_runs
# FROM 
#     batsman_stats_22_25
# WHERE 
#     balls >= 10
#     AND match_date >= '2022-01-01'
# GROUP BY 
#     player_id, player_name
# HAVING 
#     COUNT(*) > 0
# ORDER BY 
#     std_dev_runs ASC,   -- most consistent first (lower SD)
#     avg_runs DESC;-- tie-breaker: higher average run
# --------------------------------------------------------------------------------------------------------------------------------
def query_20():
    import mysql.connector
    import requests

    # -----------------------------
    # DB Connection
    # -----------------------------
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="2741",
        database="cricketdb"
    )
    cursor = conn.cursor(dictionary=True)

    # -----------------------------
    # Get first 200 players
    # -----------------------------
    # <--- key part
    cursor.execute("SELECT player_id, player_name FROM players LIMIT 200")
    players = cursor.fetchall()


    # -----------------------------
    # Create summary table
    # -----------------------------
    create_table_query = """
    CREATE TABLE IF NOT EXISTS player_batting_summary (
        player_id INT PRIMARY KEY,
        player_name VARCHAR(100),
        test_matches INT,
        odi_matches INT,
        t20_matches INT,
        test_avg FLOAT,
        odi_avg FLOAT,
        t20_avg FLOAT,
        total_matches INT
    )
    """
    cursor.execute(create_table_query)
    conn.commit()

    # -----------------------------
    # Function to fetch player stats
    # -----------------------------
    def fetch_player_stats(player_id):

        url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}/batting"

        headers = {
            "x-rapidapi-key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
            "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers)
        data = response.json()
        
        # Extract stats
        stats = {}
        for row in data['values']:
            if row['values'][0] == 'Matches':
                stats['test_matches'] = int(row['values'][1])
                stats['odi_matches'] = int(row['values'][2])
                stats['t20_matches'] = int(row['values'][3])
        
        # Calculate total matches
        stats['total_matches'] = stats['test_matches'] + stats['odi_matches'] + stats['t20_matches']
        
        # Extract averages
        for row in data['values']:
            if row['values'][0] == 'Average':
                stats['test_avg'] = float(row['values'][1])
                stats['odi_avg'] = float(row['values'][2])
                stats['t20_avg'] = float(row['values'][3])
        
        return stats

    # -----------------------------
    # Process each player
    # -----------------------------
    for player in players:
        player_id = player['player_id']# type: ignore
        player_name = player['player_name']# type: ignore
        
        stats = fetch_player_stats(player_id)
        
        if stats['total_matches'] >= 20:
            insert_query = """
            REPLACE INTO player_batting_summary
            (player_id, player_name, test_matches, odi_matches, t20_matches, test_avg, odi_avg, t20_avg, total_matches)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            cursor.execute(insert_query, (
                player_id, # type: ignore
                player_name,
                stats['test_matches'],
                stats['odi_matches'],
                stats['t20_matches'],
                stats['test_avg'],
                stats['odi_avg'],
                stats['t20_avg'],
                stats['total_matches']
            ))
            conn.commit()

    print("Summary table updated for first 200 players!")
    cursor.close()
    conn.close()

# SELECT 
#     player_id,
#     player_name,
#     test_matches,
#     odi_matches,
#     t20_matches,
#     test_avg,
#     odi_avg,
#     t20_avg,
#     total_matches
# FROM player_batting_summary
# WHERE total_matches >= 20
# ORDER BY total_matches DESC;
# --------------------------------------------------------------------------------------------------------------------------

def query_21():
    import requests
    import mysql.connector

    # ----------- DB Connection -----------
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="2741",
        database="cricketdb"
    )
    cursor = conn.cursor()

    # ----------- Get 100 players from players table -----------
    cursor.execute("SELECT player_id, player_name FROM players LIMIT 100")
    players = cursor.fetchall()  # List of tuples: (player_id, player_name)

    # ----------- API Config -----------
    headers = {
        "x-rapidapi-key": "3eaece787amshfe1adf78b14d67bp1c781fjsnebfd830416ef",
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }

    formats = ["Test", "ODI", "T20", "IPL"]

    # ----------- Fetch Batting Stats & Insert -----------
    for pid, pname in players:
        BATTING_API = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{pid}/batting"
        response = requests.get(BATTING_API, headers=headers)
        if response.status_code != 200:
            print(f"Batting API failed for {pname}")
            continue
        data = response.json()

        # Build mapping from row headers to format values
        batting_map = {}
        for row in data['values']:
            stat_name = row['values'][0]
            if stat_name in ["Matches", "Innings", "Runs", "Balls", "Average", "SR"]:
                batting_map[stat_name] = row['values'][1:]  # values per format

        for i, fmt in enumerate(formats):
            insert_batting = """
            INSERT INTO batting_stats 
            (player_id, player_name, format, matches, innings, runs, balls, average, strike_rate)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_batting, (
                pid,
                pname,
                fmt,
                int(batting_map.get("Matches")[i]), #type:ignore
                int(batting_map.get("Innings")[i]),#type:ignore
                int(batting_map.get("Runs")[i]),#type:ignore
                int(batting_map.get("Balls")[i]),#type:ignore
                float(batting_map.get("Average")[i]),#type:ignore
                float(batting_map.get("SR")[i])#type:ignore
            ))

    # ----------- Fetch Bowling Stats & Insert -----------
    for pid, pname in players:
        BOWLING_API = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{pid}/bowling"
        response = requests.get(BOWLING_API, headers=headers)
        if response.status_code != 200:
            print(f"Bowling API failed for {pname}")
            continue
        data = response.json()

        bowling_map = {}
        for row in data['values']:
            stat_name = row['values'][0]
            if stat_name in ["Matches", "Wickets", "Avg", "Eco"]:
                bowling_map[stat_name] = row['values'][1:]

        for i, fmt in enumerate(formats):
            insert_bowling = """
            INSERT INTO bowling_stats
            (player_id, player_name, format, matches, wickets, average, economy)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_bowling, (#type:ignore
                pid,
                pname,
                fmt,
                int(bowling_map.get("Matches")[i]),#type:ignore
                int(bowling_map.get("Wickets")[i]),#type:ignore
                float(bowling_map.get("Avg")[i]),#type:ignore
                float(bowling_map.get("Eco")[i])#type:ignore
            ))

    # ----------- Commit & Close -----------
    conn.commit()
    cursor.close()
    conn.close()

    print("Batting and bowling stats fetched and inserted correctly for 100 players.")
# SELECT
#     b.player_id,
#     b.player_name,
    
#     -- Batting points
#     ((b.runs * 0.01) + (b.average * 0.5) + (b.strike_rate * 0.3)) AS batting_points,
    
#     -- Bowling points
#     CASE 
#         WHEN bw.wickets = 0 AND bw.average = 0 AND bw.economy = 0 THEN 0
#         ELSE ((bw.wickets * 2) + ((50 - bw.average) * 0.5) + ((6 - bw.economy) * 2))
#     END AS bowling_points,
    
#     -- Total points
#     (
#         ((b.runs * 0.01) + (b.average * 0.5) + (b.strike_rate * 0.3)) +
#         CASE 
#             WHEN bw.wickets = 0 AND bw.average = 0 AND bw.economy = 0 THEN 0
#             ELSE ((bw.wickets * 2) + ((50 - bw.average) * 0.5) + ((6 - bw.economy) * 2))
#         END
#     ) AS total_points

# FROM batting_stats b
# LEFT JOIN bowling_stats bw 
#     ON b.player_id = bw.player_id AND b.format = bw.format

# ORDER BY total_points DESC;
# -----------------------------------------------------------------------------------------------------------------------------------
def query_22():
    #already made tables so only queries..
    '''
    1.Total matches played between them
    SELECT
    LEAST(team1_id, team2_id) AS team_a,
    GREATEST(team1_id, team2_id) AS team_b,
    COUNT(*) AS total_matches
    FROM matches
    WHERE match_date >= DATE_SUB(CURDATE(), INTERVAL 3 YEAR)
    GROUP BY team_a, team_b
    HAVING total_matches >= 1;

    2.Wins for each team (head-to-head)
    SELECT
        LEAST(team1_id, team2_id) AS team_a,
        GREATEST(team1_id, team2_id) AS team_b,
        SUM(CASE WHEN winner_team_id = LEAST(team1_id, team2_id) THEN 1 ELSE 0 END) AS team_a_wins,
        SUM(CASE WHEN winner_team_id = GREATEST(team1_id, team2_id) THEN 1 ELSE 0 END) AS team_b_wins
    FROM matches
    WHERE match_date >= DATE_SUB(CURDATE(), INTERVAL 3 YEAR)
    GROUP BY team_a, team_b;

    3.Average victory margin when each team wins
    SELECT
        LEAST(team1_id, team2_id) AS team_a,
        GREATEST(team1_id, team2_id) AS team_b,
        AVG(CASE WHEN winner_team_id = LEAST(team1_id, team2_id) THEN victory_margin END) AS team_a_avg_margin,
        AVG(CASE WHEN winner_team_id = GREATEST(team1_id, team2_id) THEN victory_margin END) AS team_b_avg_margin
    FROM matches
    WHERE match_date >= DATE_SUB(CURDATE(), INTERVAL 3 YEAR)
    GROUP BY team_a, team_b;
    4.Overall win percentage for each team
    SELECT
        t.team_id,
        t.team_name,
        SUM(CASE WHEN m.winner_team_id = t.team_id THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS win_percentage
    FROM teams t
    JOIN matches m ON t.team_id IN (m.team1_id, m.team2_id)
    WHERE m.match_date >= DATE_SUB(CURDATE(), INTERVAL 3 YEAR)
    GROUP BY t.team_id, t.team_name;

    '''
# ------------------------------------------------------------------------------------------------------------------------------
def query_23():
    '''
        WITH recent_matches AS (
        SELECT
            bs.player_id,
            bs.player_name,
            bs.runs,
            bs.balls,
            bs.match_date,
            ROW_NUMBER() OVER (PARTITION BY bs.player_id ORDER BY bs.match_date DESC) AS rn
        FROM batsman_stats_22_25 bs
    ),
    last_10 AS (
        SELECT *
        FROM recent_matches
        WHERE rn <= 10
    ),
    last_5 AS (
        SELECT *
        FROM recent_matches
        WHERE rn <= 5
    ),
    metrics AS (
        SELECT
            l10.player_id,
            l10.player_name,
            ROUND(AVG(l5.runs),2) AS last_5_avg_runs,
            ROUND(AVG(l10.runs),2) AS last_10_avg_runs,
            ROUND(AVG(l10.runs / NULLIF(l10.balls,0) * 100),2) AS avg_strike_rate_10,
            SUM(CASE WHEN l10.runs >= 50 THEN 1 ELSE 0 END) AS scores_50_plus,
            ROUND(STDDEV(l10.runs),2) AS consistency_stddev
        FROM last_10 l10
        LEFT JOIN last_5 l5 ON l10.player_id = l5.player_id AND l5.rn <= 5
        GROUP BY l10.player_id, l10.player_name
    )
    SELECT
        player_id,
        player_name,
        last_5_avg_runs,
        last_10_avg_runs,
        avg_strike_rate_10,
        scores_50_plus,
        consistency_stddev,
        CASE
            WHEN last_10_avg_runs >= 50 AND scores_50_plus >= 3 AND consistency_stddev <= 15 THEN 'Excellent Form'
            WHEN last_10_avg_runs >= 40 AND scores_50_plus >= 2 AND consistency_stddev <= 25 THEN 'Good Form'
            WHEN last_10_avg_runs >= 30 AND scores_50_plus >= 1 THEN 'Average Form'
            ELSE 'Poor Form'
        END AS form_category
    FROM metrics
    ORDER BY last_10_avg_runs DESC;

    '''
# --------------------------------------------------------------------------------------------------------------------------------------
def query_24():
    '''    SELECT
        p1.player_id AS player_a_id,
        p1.player_name AS player_a_name,
        p2.player_id AS player_b_id,
        p2.player_name AS player_b_name,
        COUNT(*) AS total_partnerships,
        AVG(ph.total_runs) AS avg_partnership_runs,
        SUM(CASE WHEN ph.total_runs >= 50 THEN 1 ELSE 0 END) AS fifty_plus_count,
        MAX(ph.total_runs) AS highest_partnership,
        ROUND(SUM(CASE WHEN ph.total_runs >= 50 THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS success_rate_percentage
    FROM partnerships AS ph
    JOIN players AS p1 ON ph.bat1id = p1.player_id
    JOIN players AS p2 ON ph.bat2id = p2.player_id
    GROUP BY ph.bat1id, ph.bat2id
    ORDER BY success_rate_percentage DESC, avg_partnership_runs DESC
    LIMIT 50;'''
#------------------------------------------------------------------------------------------------------------------------------------- 

def query_25():
        '''WITH stats_with_quarter AS (
        SELECT
            player_id,
            player_name,
            YEAR(match_date) AS year,
            QUARTER(match_date) AS quarter,
            AVG(runs) AS avg_runs,
            AVG(runs / NULLIF(balls,0) * 100) AS avg_strike_rate,
            COUNT(DISTINCT match_id) AS matches_in_quarter
        FROM batsman_stats_22_25
        GROUP BY player_id, player_name, YEAR(match_date), QUARTER(match_date)
        HAVING COUNT(DISTINCT match_id) >= 2
    ),

    ranked_quarters AS (
        SELECT
            *,
            ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY year, quarter) AS rn
        FROM stats_with_quarter
    ),

    trend_calc AS (
        SELECT
            c1.player_id,
            c1.player_name,
            c1.year,
            c1.quarter,
            c1.avg_runs,
            c1.avg_strike_rate,
            CASE
                WHEN c2.avg_runs IS NULL OR c2.avg_strike_rate IS NULL THEN 'Stable'
                WHEN c1.avg_runs > c2.avg_runs AND c1.avg_strike_rate > c2.avg_strike_rate THEN 'Improving'
                WHEN c1.avg_runs < c2.avg_runs AND c1.avg_strike_rate < c2.avg_strike_rate THEN 'Declining'
                ELSE 'Stable'
            END AS trend
        FROM ranked_quarters c1
        LEFT JOIN ranked_quarters c2
            ON c1.player_id = c2.player_id
            AND c1.rn = c2.rn + 1
    )

    SELECT
        player_id,
        player_name,
        COUNT(*) AS total_quarters,
        SUM(CASE WHEN trend='Improving' THEN 1 ELSE 0 END) AS improving_quarters,
        SUM(CASE WHEN trend='Declining' THEN 1 ELSE 0 END) AS declining_quarters,
        SUM(CASE WHEN trend='Stable' THEN 1 ELSE 0 END) AS stable_quarters,
        CASE
            WHEN SUM(CASE WHEN trend='Improving' THEN 1 ELSE 0 END) >
                SUM(CASE WHEN trend='Declining' THEN 1 ELSE 0 END) THEN 'Career Ascending'
            WHEN SUM(CASE WHEN trend='Improving' THEN 1 ELSE 0 END) <
                SUM(CASE WHEN trend='Declining' THEN 1 ELSE 0 END) THEN 'Career Declining'
            ELSE 'Career Stable'
        END AS career_phase
    FROM trend_calc
    GROUP BY player_id, player_name
    ORDER BY career_phase DESC, player_name;
    '''

# ------------------------------------------------------------------------------------------------------------------------------------