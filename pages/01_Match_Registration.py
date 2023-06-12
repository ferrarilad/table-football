import streamlit as st
from utils import LOCALES, get_db_cursor, get_db_engine, page_init
from utils.elo import calculate_elo_rating
from utils.games import get_player_aliases, valid_goals, valid_teams

page_init("Match Registration")


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
        red_alias = st.selectbox("Alias", player_aliases, key="red_att")
        red_score = st.number_input(
            "Score", min_value=0, max_value=10, step=1, key="red_score"
        )

    with col2:
        st.write("Blue Team:")
        blue_alias = st.selectbox("Alias", player_aliases, key="blue_att")
        blue_score = st.number_input(
            "Score", min_value=0, max_value=10, step=1, key="blue_score"
        )

    # Submit button
    if st.button("Register"):
        log_match(
            locale, blue_alias, None, red_alias, None, "1v1", blue_score, red_score
        )


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
        red_att = st.selectbox("Attacker alias", player_aliases, key="red_att")
        red_def = st.selectbox("Defender alias", player_aliases, key="red_def")
        red_score = st.number_input(
            "Score", min_value=0, max_value=10, step=1, key="red_score"
        )

    with col2:
        st.write("Blue Team:")
        blue_att = st.selectbox("Attacker alias", player_aliases, key="blue_att")
        blue_def = st.selectbox("Defender alias", player_aliases, key="blue_def")
        blue_score = st.number_input(
            "Score", min_value=0, max_value=10, step=1, key="blue_score"
        )

    # Submit button
    if st.button("Register"):
        log_match(
            locale, blue_att, blue_def, red_att, red_def, "2v2", blue_score, red_score
        )


def log_match(
    locale,
    blue_team_att,
    blue_team_def,
    red_team_att,
    red_team_def,
    match_type,
    blue_score,
    red_score,
):
    if not valid_teams(blue_team_att, blue_team_def, red_team_att, red_team_def):
        return st.error("Player names must be different")

    if not valid_goals(blue_score, red_score):
        return st.error("One team must have scored ten goals")

    conn = get_db_engine()
    c = get_db_cursor(conn)

    # Insert the new player into the database with a starting Elo score of 1000
    c.execute(
        "INSERT INTO matches (locale, blue_team_att, blue_team_def, red_team_att, red_team_def, match_type, blue_score, red_score) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            locale,
            blue_team_att,
            blue_team_def,
            red_team_att,
            red_team_def,
            match_type,
            blue_score,
            red_score,
        ),
    )
    conn.commit()

    # Update elo for all players:
    # Get Elo for each player
    blue_team_elo = c.execute(
        "SELECT alias, elo, games_played, games_won FROM players WHERE alias IN (?, ?)",
        [blue_team_att, blue_team_def],
    ).fetchall()
    red_team_elo = c.execute(
        "SELECT alias, elo, games_played, games_won FROM players WHERE alias IN (?, ?)",
        [red_team_att, red_team_def],
    ).fetchall()

    blue_team_new_elo, red_team_new_elo = calculate_elo_rating(
        [_[1] for _ in blue_team_elo],
        [_[1] for _ in red_team_elo],
        1 * (blue_score == 10),
        k_factor=40,
    )

    for i, (player_, _, games_played_, games_won_) in enumerate(blue_team_elo):
        new_games_played_ = games_played_ + 1
        new_games_won_ = games_won_ + 1 * (blue_score == 10)
        new_win_rate = new_games_won_ / new_games_played_
        c.execute(
            """
            UPDATE players
            SET elo = ?, games_played = ?, games_won = ?, win_rate = ?
            WHERE alias = ?;
            """,
            [
                blue_team_new_elo[i],
                new_games_played_,
                new_games_won_,
                new_win_rate,
                player_,
            ],
        )
        conn.commit()

    for i, (player_, _, games_played_, games_won_) in enumerate(red_team_elo):
        new_games_played_ = games_played_ + 1
        new_games_won_ = games_won_ + 1 * (blue_score != 10)
        new_win_rate = new_games_won_ / new_games_played_
        c.execute(
            """
            UPDATE players
            SET elo = ?, games_played = ?, games_won = ?, win_rate = ?
            WHERE alias = ?;
            """,
            [
                red_team_new_elo[i],
                new_games_played_,
                new_games_won_,
                new_win_rate,
                player_,
            ],
        )
        conn.commit()

    st.success("Match registered successfully!")


st.write("Register a new match")

# Get user input for game type
game_type = st.selectbox("Game Type", ["1v1", "2v2"])

# Register match based on game type
if game_type == "1v1":
    register_1v1_match()
elif game_type == "2v2":
    register_2v2_match()
