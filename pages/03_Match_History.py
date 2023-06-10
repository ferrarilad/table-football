import pandas as pd
import streamlit as st

from utils import get_db_engine, get_db_cursor, page_init, LOCALES
from utils.elo import recompute_elo
from utils.games import get_player_aliases, valid_teams, valid_goals

# Helper functions for database operations
def get_match_info(game_id):
    # Retrieve match information from the database based on the game_id

    conn = get_db_engine()
    c = get_db_cursor(conn)

    c.execute(
        """
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
    """,
        (game_id,),
    )
    match = c.fetchone()
    return match


def update_match_info(
        game_id,
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

    # Update the match information in the database based on the game_id
    c.execute(
        """
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
    """,
        (
            locale,
            blue_team_att,
            blue_team_def,
            red_team_att,
            red_team_def,
            match_type,
            blue_score,
            red_score,
            game_id,
        ),
    )
    conn.commit()

    st.success("Match successfully Edited.")


page_init("Match History")

conn = get_db_engine()
c = get_db_cursor(conn)

# Retrieve player rankings from the database
c.execute(
    """
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
"""
)
matches = pd.DataFrame(
    c.fetchall(),
    columns=[
        "GAME_ID",
        "LOCALE",
        "BLUE_TEAM_ATT",
        "BLUE_TEAM_DEF",
        "RED_TEAM_ATT",
        "RED_TEAM_DEF",
        "MATCH_TYPE",
        "BLUE_SCORE",
        "RED_SCORE",
        "TIMESTAMP",
    ],
).fillna(
    {
        "BLUE_TEAM_ATT": "",
        "BLUE_TEAM_DEF": "",
        "RED_TEAM_ATT": "",
        "RED_TEAM_DEF": "",
    }
)

st.table(matches)

with st.expander("Edit Match"):
    # Fields to edit match
    game_id = st.text_input(
        "Enter the Game ID to edit:",
        value=matches.iloc[0].GAME_ID
    )
    match = get_match_info(game_id)

    if not match:
        st.write("Game ID not found.")
        st.stop()

    all_players = get_player_aliases()

    locale = match[1]
    match_type = match[6]
    blue_team_att = match[2]
    blue_team_att_ix = all_players.index(str(blue_team_att))
    blue_team_def = match[3]
    blue_team_def_ix = 0
    if match_type == "2v2":
        blue_team_def_ix = all_players.index(str(blue_team_def))
    red_team_att = match[4]
    red_team_att_ix = all_players.index(str(red_team_att))
    red_team_def = match[5]
    red_team_def_ix = 0
    if match_type == "2v2":
        red_team_def_ix = all_players.index(str(red_team_def))
        alias_title = "Attacker alias"
    else:
        alias_title = "Alias"
    blue_score = match[7]
    red_score = match[8]

    locale = st.selectbox("locale", LOCALES, index=LOCALES.index(locale))
    match_type_sel = st.selectbox(
        "Game Type",
        ["1v1", "2v2"],
        index=["1v1", "2v2"].index(match_type)
    )
    # Missing locale and game type

    col1, col2 = st.columns(2)
    # Get user input for team aliases
    with col1:
        st.write("Red Team:")
        red_att = st.selectbox(
            alias_title, all_players, key="red_att", index=red_team_att_ix
        )
        if match_type_sel == "2v2":
            red_def = st.selectbox(
                "Defender alias", all_players, key="red_def", index=red_team_def_ix
            )
        else:
            red_def = None
        red_score_ = st.number_input(
            "Score",
            min_value=0,
            max_value=10,
            step=1,
            key="red_score",
            value=red_score,
        )

    with col2:
        st.write("Blue Team:")
        blue_att = st.selectbox(
            alias_title, all_players, key="blue_att", index=blue_team_att_ix
        )
        if match_type_sel == "2v2":
            blue_def = st.selectbox(
                "Defender alias",
                all_players,
                key="blue_def",
                index=blue_team_def_ix,
            )
        else:
            blue_def = None
        blue_score_ = st.number_input(
            "Score",
            min_value=0,
            max_value=10,
            step=1,
            key="blue_score",
            value=blue_score,
        )

    # Save button
    if st.button("Save"):
        update_match_info(
            game_id,
            locale,
            blue_att,
            blue_def,
            red_att,
            red_def,
            match_type_sel,
            blue_score_,
            red_score_,
        )
        recompute_elo()
        st.write("ELO scores recomputed.")
