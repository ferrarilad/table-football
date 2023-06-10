import datetime as dt
import pandas as pd
import sqlite3
import streamlit as st

from utils import get_db_engine, get_db_cursor, page_init
from utils.helpers import download_string_as_file

USER = "admin"
PASSWORD = "admin"

page_init("Admin")

col1, col2 = st.columns(2)

usr = col1.text_input("Username")
pwd = col2.text_input("Password", type="password")

if not (usr == USER and pwd == PASSWORD):
    st.subheader("Please log in")
    st.stop()


def reset_db():
    from sqlalchemy import text
    engine = get_db_engine()

    with engine.connect() as con:
        sql = text("select 'drop table ' || name || ';' from sqlite_master where type = 'table';")
        result = con.execute(sql)
        statements = [row[0] for row in result]

        for s in statements:
            con.execute(text(s))


def copy_db():
    con = get_db_engine().raw_connection()
    contents = ""
    for line in con.iterdump():
        contents = contents + ('%s\n' % line)
    return contents


col1, col2, col3 = st.columns(3)

if col1.button("Download DB"):
    download_string_as_file(copy_db(), "database.sql")
    st.success("You are done!")

if col2.button("Update DB (Run migrations)"):
    import alembic.config

    alembicArgs = [
        '--raiseerr',
        'upgrade', 'head',
    ]
    alembic.config.main(argv=alembicArgs)
    st.success("You are done!")

st.subheader("Upload")

col1, col2 = st.columns(2)


def upload_players(df):
    conn = get_db_engine()
    c = get_db_cursor(conn)

    df = df[["alias", "elo", "games_played"]]

    # df.rename(columns={"index": "id"})
    c.execute("DELETE FROM players")
    conn.commit()
    for i, row in df.iterrows():
        c.execute(
            "INSERT INTO players (alias, elo, games_played) VALUES (?, ?, ?)",
            row,
        )
        if i % 10 == 9:
            conn.commit()

    conn.commit()


with col1:
    players_data = st.file_uploader("Upload players data")
    if players_data is not None:
        # Can be used wherever a "file-like" object is accepted:
        players = pd.read_csv(players_data)
        st.write(
            "Preview the data and please ensure that the dataframe contains the following columns:"
        )
        st.text(
            """
            - alias
            - elo
            - games_played
            """
        )
        st.write(players.head(5))
        st.write("Note that this will overwrite players table:")
        if st.button(
                label="Confirm upload",
                key="ply_conf"
        ):
            try:
                upload_players(players)
                st.success("Done!")
            except Exception as e:
                st.write(e)


def upload_matches(df):
    conn = get_db_engine()
    c = get_db_cursor(conn)

    try:
        df = df[
            [
                "locale",
                "blue_team_att",
                "blue_team_def",
                "red_team_att",
                "red_team_def",
                "match_type",
                "blue_score",
                "red_score",
                "timestamp",
            ]
        ]

        # df.rename(columns={"index": "id"})
        c.execute("DELETE FROM matches")
        conn.commit()
        for i, row in df.iterrows():
            c.execute(
                "INSERT INTO matches(locale, blue_team_att, blue_team_def, red_team_att, red_team_def, match_type, blue_score, red_score, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                row,
            )
            if i % 10 == 9:
                conn.commit()
        conn.commit()
    except Exception as e:
        st.write(e)


with col2:
    match_data = st.file_uploader("Upload match data")
    if match_data is not None:
        # Can be used wherever a "file-like" object is accepted:
        matches = pd.read_csv(match_data)
        st.write(
            "Preview the data and please ensure that the dataframe contains the following columns:"
        )
        st.text(
            """
            - locale
            - blue_team_att
            - blue_team_def
            - red_team_att
            - red_team_def
            - match_type
            - blue_score
            - red_score
            - timestamp"""
        )
        st.write(matches.head(5))
        st.write("Note that this will overwrite matches table:")

        if st.button(
                label="Confirm upload",
                key="mtc_conf",
        ):
            try:
                upload_matches(matches)
                st.success("Done!")
            except Exception as e:
                st.write(e)

st.subheader("Download")

col1, col2 = st.columns(2)


def download_players():
    conn = get_db_engine()
    c = get_db_cursor(conn)

    c.execute(
        """
    SELECT
            alias
            , elo
            , games_played 
        FROM players 
        """
    )
    player_data = c.fetchall()
    player = pd.DataFrame(player_data, columns=["alias", "elo", "games_played"])

    download_string_as_file(
        player.to_csv(index=False),
        f"players_{dt.date.today()}.csv",
    )


col1.button(
    label="Download players data",
    on_click=download_players
)


def download_matches():
    conn = get_db_engine()
    print(conn)
    c = get_db_cursor(conn)

    c.execute("""
    SELECT
            locale
        , blue_team_att
        , blue_team_def
        , red_team_att
        , red_team_def
        , match_type
        , blue_score
        , red_score
        , timestamp
        FROM matches 
    """)

    matches_data = c.fetchall()
    matches = pd.DataFrame(
        matches_data,
        columns=[
            "locale",
            "blue_team_att",
            "blue_team_def",
            "red_team_att",
            "red_team_def",
            "match_type",
            "blue_score",
            "red_score",
            "timestamp",
        ],
    )

    download_string_as_file(
        matches.to_csv(index=False),
        f"matches_{dt.date.today()}.csv"
    )


col2.button(
    label="Download matches data",
    on_click=download_matches,
)
