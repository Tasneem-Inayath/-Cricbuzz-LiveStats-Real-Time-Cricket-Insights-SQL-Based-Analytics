queries_json = {
    # --- Beginner Level ---
    "1. List all players from India": '''
    SELECT 
        player_name,
        role,
        batting_style,
        bowling_style
    FROM players
    WHERE team_id = (
        SELECT team_id 
        FROM teams 
        WHERE country = 'India'
    );'''
,

    "2. Show all cricket matches played in the last 7 days": 
    '''SELECT 
        m.description AS match_description,
        t1.team_name AS team1,
        t2.team_name AS team2,
        v.venue_name,
        v.city,
        m.match_date
    FROM matches m
    JOIN teams t1 ON m.team1_id = t1.team_id
    JOIN teams t2 ON m.team2_id = t2.team_id
    JOIN venues v ON m.venue_id = v.venue_id
    WHERE m.match_date >= CURDATE() - INTERVAL 7 DAY
    ORDER BY m.match_date DESC;'''
,

    "3. Top 10 highest run scorers in ODI": 
    '''SELECT 
        player_name,
        runs AS total_runs,
        batting_average,
        centuries
    FROM top_odi_run_scorers
    ORDER BY runs DESC
    LIMIT 10;'''
,

    "4. Venues with capacity > 30,000": 
    '''SELECT 
        venue_name,
        city,
        country,
        capacity
    FROM venues
    WHERE capacity > 30000
    ORDER BY capacity DESC;
''',

    "5. Total matches won by each team": 
    '''SELECT 
        t.team_name,
        COUNT(*) AS total_wins
    FROM matches m
    JOIN teams t ON m.winner_team_id = t.team_id
    GROUP BY t.team_name
    ORDER BY total_wins DESC;'''
,

    "6. Count of players by role": 
'''    SELECT 
        role,
        COUNT(*) AS player_count
    FROM players
    GROUP BY role
    ORDER BY player_count DESC;'''
,

    "7. Highest individual score in each format": 
    '''SELECT 
        format,
        player_name,
        highest_score,
        balls,
        strike_rate,
        opposition
    FROM highest_scores hs
    WHERE (format, highest_score) IN (
        SELECT 
            format,
            MAX(highest_score)
        FROM highest_scores
        GROUP BY format
    );''',

    "8. Series started in 2024": 
    '''SELECT 
        series_name,
        host_country,
        start_date,
        total_matches
    FROM series_2024
    ORDER BY start_date;'''
,

    # --- Intermediate Level ---
    "9. All-rounders with >1000 runs and >50 wickets": 
    '''SELECT 
        player_name,
        runs AS total_runs,
        wickets AS total_wickets,
        format
    FROM all_rounders_stats
    WHERE runs > 1000 AND wickets > 50;'''
,

    "10. Last 20 completed matches": 
    '''SELECT 
        m.description AS match_description,
        t1.team_name AS team1,
        t2.team_name AS team2,
        tw.team_name AS winning_team,
        m.victory_margin,
        m.victory_type,
        v.venue_name
    FROM matches m
    JOIN teams t1 ON m.team1_id = t1.team_id
    JOIN teams t2 ON m.team2_id = t2.team_id
    JOIN teams tw ON m.winner_team_id = tw.team_id
    JOIN venues v ON m.venue_id = v.venue_id
    ORDER BY m.match_date DESC
    LIMIT 20;'''
,

    "11. Compare player performance across formats": 
    '''SELECT 
        p.player_id,
        p.player_name,
        MAX(CASE WHEN p.format = 'Test' THEN p.runs ELSE 0 END) AS Test_Runs,
        MAX(CASE WHEN p.format = 'ODI' THEN p.runs ELSE 0 END) AS ODI_Runs,
        MAX(CASE WHEN p.format = 'T20I' THEN p.runs ELSE 0 END) AS T20I_Runs,
        ROUND(AVG(p.batting_average), 2) AS Overall_Batting_Avg,
        COUNT(DISTINCT p.format) AS Formats_Played
    FROM 
        player_batting_stats p
    GROUP BY 
        p.player_id, p.player_name
    HAVING 
        Formats_Played >= 2
    ORDER BY 
        Overall_Batting_Avg DESC;''',

    "12. Team performance home vs away": 
    '''SELECT 
        t.team_id,
        t.team_name,
        SUM(CASE WHEN v.country = t.country AND m.winner_team_id = t.team_id THEN 1 ELSE 0 END) AS home_wins,
        SUM(CASE WHEN v.country <> t.country AND m.winner_team_id = t.team_id THEN 1 ELSE 0 END) AS away_wins
    FROM matches m
    JOIN teams t 
        ON m.winner_team_id = t.team_id
    JOIN venues v 
        ON m.venue_id = v.venue_id
    GROUP BY t.team_id, t.team_name
    ORDER BY t.team_name;''',

    "13. Partnerships with >=100 runs": 
    '''SELECT
        match_id,
        innings_id,
        bat1name,
        bat2name,
        total_runs AS partnership_runs
    FROM partnerships
    WHERE total_runs >= 100
    ORDER BY match_id, innings_id, partnership_runs DESC;'''
,

    "14. Bowling performance at venues": 
    '''SELECT
        venue_id,
        bowler_id,
        bowler_name,
        COUNT(DISTINCT match_id) AS matches_played,
        SUM(wickets) AS total_wickets,
        SUM(economy * overs) / SUM(overs) AS avg_economy
    FROM bowling_performance
    WHERE overs >= 4
    GROUP BY venue_id, bowler_id, bowler_name
    HAVING COUNT(DISTINCT match_id) >= 3
    ORDER BY venue_id, total_wickets DESC;''',

    "15. Players in close matches (<50 runs or <5 wickets)": 
    '''SELECT 
        player_id,
        player_name,
        COUNT(*) AS close_matches_played,
        ROUND(AVG(runs_scored), 2) AS avg_runs_in_close,
        SUM(CASE 
                WHEN bat_team_id = team_won_id THEN 1 
                ELSE 0 
            END) AS close_matches_won
    FROM match_player_stats
    WHERE 
        (win_by_runs = 1 AND win_margin < 50)    -- close by runs
        OR
        (win_by_runs = 0 AND win_margin < 5)     -- close by wickets
    GROUP BY player_id, player_name
    ORDER BY avg_runs_in_close DESC;''',

    "16. Batting performance by year since 2020": 
        '''select * from player_yearly_stats where matches_played>5;''',

    # --- Advanced Level ---
    "17. Toss advantage analysis": 
    '''SELECT 
        toss_decision,
        COUNT(*) AS total_matches,
        SUM(CASE WHEN toss_winner_id = winner_id THEN 1 ELSE 0 END) AS matches_won_by_toss_winner,
        ROUND(100.0 * SUM(CASE WHEN toss_winner_id = winner_id THEN 1 ELSE 0 END) / COUNT(*), 2) AS win_percentage
    FROM toss_analysis
    GROUP BY toss_decision;''',

    "18. Most economical bowlers in ODI/T20I": 
    '''SELECT
        player_id,
        player_name,
        match_type,
        matches,
        overs,
        wickets,
        economy
    FROM
        player_bowling_stats
    WHERE
        match_type IN ('odi', 't20')
        AND matches >= 10
        AND (overs / matches) >= 2
    ORDER BY
        economy ASC,
        wickets DESC;''',

    "19. Most consistent batsmen": 
    '''SELECT 
        player_id,
        player_name,
        COUNT(*) AS innings_count,
        AVG(runs) AS avg_runs,
        STDDEV(runs) AS std_dev_runs
    FROM 
        batsman_stats_22_25
    WHERE 
        balls >= 10
        AND match_date >= '2022-01-01'
    GROUP BY 
        player_id, player_name
    HAVING 
        COUNT(*) > 0
    ORDER BY 
        std_dev_runs ASC,  
        avg_runs DESC;''',

    "20. Matches played per format with batting avg": 
    '''SELECT 
        player_id,
        player_name,
        test_matches,
        odi_matches,
        t20_matches,
        test_avg,
        odi_avg,
        t20_avg,
        total_matches
    FROM player_batting_summary
    WHERE total_matches >= 20
    ORDER BY total_matches DESC;''',

    "21. Comprehensive performance ranking": 
    '''SELECT
        b.player_id,
        b.player_name,
        
        -- Batting points
        ((b.runs * 0.01) + (b.average * 0.5) + (b.strike_rate * 0.3)) AS batting_points,
        
        -- Bowling points
        CASE 
            WHEN bw.wickets = 0 AND bw.average = 0 AND bw.economy = 0 THEN 0
            ELSE ((bw.wickets * 2) + ((50 - bw.average) * 0.5) + ((6 - bw.economy) * 2))
        END AS bowling_points,
        
        -- Total points
        (
            ((b.runs * 0.01) + (b.average * 0.5) + (b.strike_rate * 0.3)) +
            CASE 
                WHEN bw.wickets = 0 AND bw.average = 0 AND bw.economy = 0 THEN 0
                ELSE ((bw.wickets * 2) + ((50 - bw.average) * 0.5) + ((6 - bw.economy) * 2))
            END
        ) AS total_points

    FROM batting_stats b
    LEFT JOIN bowling_stats bw 
        ON b.player_id = bw.player_id AND b.format = bw.format

    ORDER BY total_points DESC;''',

    "22. Head-to-head team analysis": {
    "1.Total matches played between them":
    '''SELECT
    LEAST(team1_id, team2_id) AS team_a,
    GREATEST(team1_id, team2_id) AS team_b,
    COUNT(*) AS total_matches
    FROM matches
    WHERE match_date >= DATE_SUB(CURDATE(), INTERVAL 3 YEAR)
    GROUP BY team_a, team_b
    HAVING total_matches >= 1;''',

    "2.Wins for each team (head-to-head)":
    '''SELECT
        LEAST(team1_id, team2_id) AS team_a,
        GREATEST(team1_id, team2_id) AS team_b,
        SUM(CASE WHEN winner_team_id = LEAST(team1_id, team2_id) THEN 1 ELSE 0 END) AS team_a_wins,
        SUM(CASE WHEN winner_team_id = GREATEST(team1_id, team2_id) THEN 1 ELSE 0 END) AS team_b_wins
    FROM matches
    WHERE match_date >= DATE_SUB(CURDATE(), INTERVAL 3 YEAR)
    GROUP BY team_a, team_b;''',

    "3.Average victory margin when each team wins":
    '''SELECT
        LEAST(team1_id, team2_id) AS team_a,
        GREATEST(team1_id, team2_id) AS team_b,
        AVG(CASE WHEN winner_team_id = LEAST(team1_id, team2_id) THEN victory_margin END) AS team_a_avg_margin,
        AVG(CASE WHEN winner_team_id = GREATEST(team1_id, team2_id) THEN victory_margin END) AS team_b_avg_margin
    FROM matches
    WHERE match_date >= DATE_SUB(CURDATE(), INTERVAL 3 YEAR)
    GROUP BY team_a, team_b;''',

    "4.Overall win percentage for each team":
    '''SELECT
        t.team_id,
        t.team_name,
        SUM(CASE WHEN m.winner_team_id = t.team_id THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS win_percentage
    FROM teams t
    JOIN matches m ON t.team_id IN (m.team1_id, m.team2_id)
    WHERE m.match_date >= DATE_SUB(CURDATE(), INTERVAL 3 YEAR)
    GROUP BY t.team_id, t.team_name;''',
}

,

    "23. Recent player form (last 10 matches per player)": 
    
    '''WITH recent_matches AS (
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
    ,

    "24. Successful batting partnerships": 
            '''SELECT
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
        LIMIT 50;''',

    "25. Player performance over time (quarterly)": 
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
        ORDER BY career_phase DESC, player_name;'''
}
