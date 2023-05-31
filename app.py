import streamlit as st
import sqlite3
import pandas as pd

LOCALES = ['IT', 'UK']

# Connect to the SQLite database
conn = sqlite3.connect('team_entries.db')
c = conn.cursor()

# Create tables if they don't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alias TEXT UNIQUE,
        elo INTEGER,
        games_played INTEGER
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        locale TEXT,
        blue_team_att TEXT,
        blue_team_def TEXT,
        red_team_att TEXT,
        red_team_def TEXT,
        match_type TEXT,
        blue_score INTEGER,
        red_score INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')


def get_player_aliases():
    # Retrieve player aliases from the database
    c.execute("SELECT alias FROM players")
    player_aliases = c.fetchall()

    # Flatten the list of aliases
    return [alias[0] for alias in player_aliases]


def valid_goals(blue_score, red_score):
    return blue_score == 10 or red_score == 10


def valid_teams(blue_team_att, blue_team_def, red_team_att, red_team_def):
    if blue_team_def is None and red_team_def is None and blue_team_att != red_team_att:
        return True
    return len({blue_team_att, blue_team_def, red_team_att, red_team_def}) == 4


def calculate_elo_rating(team1_rating, team2_rating, team1_result, k_factor=40):
    """
    Calculates the new Elo ratings of teams after a match.

    team1_rating: tuple or list of two ints or floats, the current Elo ratings of team 1's players.
    team2_rating: tuple or list of two ints or floats, the current Elo ratings of team 2's players.
    team1_result: float, the team1_result of the match (1 for a win, 0.5 for a draw, 0 for a loss).
    k_factor: int or float, the K-factor determines how much the Elo rating should change.
              (default value is 32, a commonly used value in chess)

    Returns updated Elo ratings for both teams as tuples.
    """
    team1_avg_rating = sum(team1_rating) / len(team1_rating)
    team2_avg_rating = sum(team2_rating) / len(team2_rating)

    team1_expected_score = 1 / (1 + 10 ** ((team2_avg_rating - team1_avg_rating) / 400))
    team2_expected_score = 1 - team1_expected_score

    team1_rating_change = k_factor * (team1_result - team1_expected_score)
    team2_rating_change = k_factor * ((1 - team1_result) - team2_expected_score)

    team1_new_ratings = [int(rating + team1_rating_change) for rating in team1_rating]
    team2_new_ratings = [int(rating + team2_rating_change) for rating in team2_rating]

    return tuple(team1_new_ratings), tuple(team2_new_ratings)


def log_match(locale, blue_team_att, blue_team_def, red_team_att, red_team_def, match_type, blue_score, red_score):
    if not valid_teams(blue_team_att, blue_team_def, red_team_att, red_team_def):
        return st.error('Player names must be different')

    if not valid_goals(blue_score, red_score):
        return st.error('One team must have scored ten goals')

    # Insert the new player into the database with a starting Elo score of 1000
    c.execute(
        "INSERT INTO matches (locale, blue_team_att, blue_team_def, red_team_att, red_team_def, match_type, blue_score, red_score) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (locale, blue_team_att, blue_team_def, red_team_att, red_team_def, match_type, blue_score, red_score)
    )
    conn.commit()

    # Update elo for all players:
    # Get Elo for each player
    blue_team_elo = c.execute(
        "SELECT alias, elo, games_played FROM players WHERE alias IN (?, ?)",
        [blue_team_att, blue_team_def]
    ).fetchall()
    red_team_elo = c.execute(
        "SELECT alias, elo, games_played FROM players WHERE alias IN (?, ?)",
        [red_team_att, red_team_def]
    ).fetchall()

    blue_team_new_elo, red_team_new_elo = calculate_elo_rating(
        [_[1] for _ in blue_team_elo],
        [_[1] for _ in red_team_elo],
        1 * (blue_score == 10),
        k_factor=40
    )

    for i, (player_, _, games_played_) in enumerate(blue_team_elo):
        c.execute(
            """
            UPDATE players
            SET elo = ?, games_played = ?
            WHERE alias = ?;
            """,
            [blue_team_new_elo[i], games_played_ + 1, player_]
        )
        conn.commit()

    for i, (player_, _, games_played_) in enumerate(red_team_elo):
        c.execute(
            """
            UPDATE players
            SET elo = ?, games_played = ?
            WHERE alias = ?;
            """,
            [red_team_new_elo[i], games_played_ + 1, player_]
        )
        conn.commit()

    st.success("Match registered successfully!")


# Streamlit app
def main():
    st.title("Team Management App")

    # Create the main navigation menu
    menu = ["Player Ranking", "Match Registration", "Match History", "Edit Match", "Player Registration"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Player Ranking":
        show_player_ranking()
    elif choice == "Player Registration":
        register_player()
    elif choice == "Match Registration":
        register_match()
    elif choice == "Match History":
        match_history()
    elif choice == "Edit Match":
        edit_match()


def show_player_ranking():
    st.title("Player Ranking")
    st.write("Ranked players by Elo:")

    # Retrieve player rankings from the database
    c.execute("SELECT alias, elo, games_played FROM players ORDER BY elo DESC")
    player_rankings = c.fetchall()

    # Display the rankings in a table
    st.table(pd.DataFrame(player_rankings, columns=['ALIAS', 'ELO', 'GAMES PLAYED']))


def match_history():
    st.title("Match History")

    # Retrieve player rankings from the database
    c.execute("""
        SELECT 
            id,
            locale,
            blue_team_att,
            blue_team_def,
            red_team_att,
            red_team_def,
            match_type,
            blue_score,
            red_score,
            timestamp
        FROM matches 
        ORDER BY timestamp DESC
        LIMIT 10
    """)
    matches = c.fetchall()

    st.table(
        pd.DataFrame(
            matches,
            columns=[
                'GAME_ID',
                'LOCALE',
                'BLUE_TEAM_ATT',
                'BLUE_TEAM_DEF',
                'RED_TEAM_ATT',
                'RED_TEAM_DEF',
                'MATCH_TYPE',
                'BLUE_SCORE',
                'RED_SCORE',
                'TIMESTAMP'
            ]
        ).fillna(
            {
                'BLUE_TEAM_ATT': '',
                'BLUE_TEAM_DEF': '',
                'RED_TEAM_ATT': '',
                'RED_TEAM_DEF': ''
            }
        )
    )

    # Delete button
    # if st.button("Edit"):
    #     edit_match()

def edit_match():
    st.title("Edit Match")

    # Fields to edit match
    game_id = st.text_input("Enter the Game ID to edit:", value=1)
    match = get_match_info(game_id)

    all_players = get_player_aliases()

    if match:
        locale = match[1]
        match_type = match[6]
        blue_team_att = match[2]
        blue_team_att_ix = all_players.index(str(blue_team_att))
        blue_team_def = match[3]
        blue_team_def_ix = 0
        if match_type=='2v2':
            blue_team_def_ix = all_players.index(str(blue_team_def))
        red_team_att = match[4]
        red_team_att_ix = all_players.index(str(red_team_att))
        red_team_def = match[5]
        red_team_def_ix = 0
        if match_type == '2v2':
            red_team_def_ix = all_players.index(str(red_team_def))
            alias_title = "Attacker alias"
        else:
            alias_title = "Alias"
        blue_score = match[7]
        red_score = match[8]


        locale = st.selectbox("locale", LOCALES, index=LOCALES.index(locale))
        match_type = st.selectbox("Game Type", ["1v1", "2v2"], index=["1v1", "2v2"].index(match_type))
        # Missing locale and game type

        col1, col2 = st.columns(2)
        # Get user input for team aliases
        with col1:
            st.write("Red Team:")
            red_att = st.selectbox(alias_title, all_players, key='red_att', index=red_team_att_ix)
            if match_type == '2v2':
                red_def = st.selectbox("Defender alias", all_players, key='red_def', index=red_team_def_ix)
            else:
                red_def = None
            red_score_ = st.number_input("Score", min_value=0, max_value=10, step=1, key='red_score', value=red_score)

        with col2:
            st.write("Blue Team:")
            blue_att = st.selectbox(alias_title, all_players, key='blue_att', index=blue_team_att_ix)
            if match_type == '2v2':
                blue_def = st.selectbox("Defender alias", all_players, key='blue_def', index=blue_team_def_ix)
            else:
                blue_def = None
            blue_score_ = st.number_input("Score", min_value=0, max_value=10, step=1, key='blue_score', value = blue_score)
    else:
        st.write("Game ID not found.")

    # Save button
    if st.button("Save"):
        update_match_info(game_id, locale, blue_att, blue_def, red_att, red_def, match_type,
                          blue_score_, red_score_)
        recompute_elo()

# Helper functions for database operations
def get_match_info(game_id):
    # Retrieve match information from the database based on the game_id
    c.execute("""
        SELECT 
            id,
            locale,
            blue_team_att,
            blue_team_def,
            red_team_att,
            red_team_def,
            match_type,
            blue_score,
            red_score
        FROM matches 
        WHERE id = ?
    """, (game_id,))
    match = c.fetchone()
    return match

def update_match_info(game_id, locale, blue_team_att, blue_team_def, red_team_att, red_team_def, match_type,blue_score, red_score):
    if not valid_teams(blue_team_att, blue_team_def, red_team_att, red_team_def):
        return st.error('Player names must be different')

    if not valid_goals(blue_score, red_score):
        return st.error('One team must have scored ten goals')

    # Update the match information in the database based on the game_id
    c.execute("""
        UPDATE matches 
        SET 
            locale = ?,
            blue_team_att = ?,
            blue_team_def = ?,
            red_team_att = ?,
            red_team_def = ?,
            match_type = ?,
            blue_score = ?,
            red_score = ?
        WHERE id = ?
    """, (locale, blue_team_att, blue_team_def, red_team_att, red_team_def, match_type, blue_score, red_score, game_id))
    conn.commit()

    st.success("Match successfully Edited.")

def recompute_elo():
    # Recalculate ELO scores for all players based on the new match information
    all_matches = get_all_matches()

    # Reset all player scores to the original value
    reset_player_scores()

    for match in all_matches:

        locale = match[1]
        blue_team_att = match[2]
        blue_team_def = match[3]
        red_team_att = match[4]
        red_team_def = match[5]
        match_type = match[6]
        blue_score = match[7]
        red_score = match[8]

        # Update elo for all players:
        # Get Elo for each player
        blue_team_elo = c.execute(
            "SELECT alias, elo, games_played FROM players WHERE alias IN (?, ?)",
            [blue_team_att, blue_team_def]
        ).fetchall()
        red_team_elo = c.execute(
            "SELECT alias, elo, games_played FROM players WHERE alias IN (?, ?)",
            [red_team_att, red_team_def]
        ).fetchall()

        blue_team_new_elo, red_team_new_elo = calculate_elo_rating(
            [_[1] for _ in blue_team_elo],
            [_[1] for _ in red_team_elo],
            1 * (blue_score == 10),
            k_factor=40
        )

        for i, (player_, _, games_played_) in enumerate(blue_team_elo):
            c.execute(
                """
                UPDATE players
                SET elo = ?, games_played = ?
                WHERE alias = ?;
                """,
                [blue_team_new_elo[i], games_played_ + 1, player_]
            )
            conn.commit()

        for i, (player_, _, games_played_) in enumerate(red_team_elo):
            c.execute(
                """
                UPDATE players
                SET elo = ?, games_played = ?
                WHERE alias = ?;
                """,
                [red_team_new_elo[i], games_played_ + 1, player_]
            )
            conn.commit()

    st.write("ELO scores recomputed.")

def reset_player_scores():
    all_players = get_player_aliases()

    for p in all_players:
        # Reset all player scores to the original value
        c.execute(
            """
            UPDATE players
            SET elo = ?, games_played = ?
            WHERE alias = ?;
            """,
            [1000, 0, p]
        )
        conn.commit()

def get_all_matches():
    # Retrieve all matches from the database
    c.execute("""
        SELECT 
            id,
            locale,
            blue_team_att,
            blue_team_def,
            red_team_att,
            red_team_def,
            match_type,
            blue_score,
            red_score
        FROM matches 
        ORDER BY timestamp ASC
    """)
    matches = c.fetchall()
    return matches

def register_player():
    st.title("Player Registration")
    st.write("Register a new player")

    # Get user input for player alias
    alias = st.text_input("Player Alias")

    # Check if the alias already exists in the database
    c.execute("SELECT COUNT(*) FROM players WHERE alias=?", (alias,))
    alias_count = c.fetchone()[0]

    # Submit button
    if st.button("Register"):
        if alias_count > 0:
            st.error("Player alias already exists. Please choose a unique alias.")
        else:
            # Insert the new player into the database with a starting Elo score of 1000
            c.execute("INSERT INTO players (alias, elo, games_played) VALUES (?, ?, ?)", (alias, 1000, 0))
            conn.commit()
            st.success("Player registered successfully!")


def register_match():
    st.title("Match Registration")
    st.write("Register a new match")

    # Get user input for game type
    game_type = st.selectbox("Game Type", ["1v1", "2v2"])

    # Register match based on game type
    if game_type == "1v1":
        register_1v1_match()
    elif game_type == "2v2":
        register_2v2_match()


def register_1v1_match():
    st.write("1v1 Match")
    st.write("Enter the details:")

    # Get player aliases from the database
    player_aliases = get_player_aliases()
    col1, col2 = st.columns(2)
    locale = st.selectbox("locale", LOCALES)

    # Get user input for team aliases
    with col1:
        st.write("Red Team:")
        red_alias = st.selectbox("Alias", player_aliases, key='red_att')
        red_score = st.number_input("Score", min_value=0, max_value=10, step=1, key='red_score')

    with col2:
        st.write("Blue Team:")
        blue_alias = st.selectbox("Alias", player_aliases, key='blue_att')
        blue_score = st.number_input("Score", min_value=0, max_value=10, step=1, key='blue_score')

    # Submit button
    if st.button("Register"):
        log_match(locale, blue_alias, None, red_alias, None, '1v1', blue_score, red_score)


def register_2v2_match():
    st.write("2v2 Match")
    st.write("Enter the details:")

    # Get player aliases from the database
    player_aliases = get_player_aliases()
    col1, col2 = st.columns(2)
    locale = st.selectbox("locale", LOCALES)

    # Get user input for team aliases
    with col1:
        st.write("Red Team:")
        red_att = st.selectbox("Attacker alias", player_aliases, key='red_att')
        red_def = st.selectbox("Defender alias", player_aliases, key='red_def')
        red_score = st.number_input("Score", min_value=0, max_value=10, step=1, key='red_score')

    with col2:
        st.write("Blue Team:")
        blue_att = st.selectbox("Attacker alias", player_aliases, key='blue_att')
        blue_def = st.selectbox("Defender alias", player_aliases, key='blue_def')
        blue_score = st.number_input("Score", min_value=0, max_value=10, step=1, key='blue_score')

    # Submit button
    if st.button("Register"):
        log_match(locale, blue_att, blue_def, red_att, red_def, '2v2', blue_score, red_score)


if __name__ == '__main__':
    main()