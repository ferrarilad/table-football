import pandas as pd
import streamlit as st
from utils import get_db_cursor, get_db_engine, page_init

page_init("Player Ranking")

st.subheader("Ranked players by Elo (showing only players with 1 match registered):")

conn = get_db_engine()
c = get_db_cursor(conn)

# Retrieve player rankings from the database
c.execute(
    "SELECT LOWER(alias) as alias, elo, games_played, games_won, win_rate FROM players WHERE games_played > 0 ORDER BY elo DESC"
)
player_rankings = c.fetchall()

df = pd.DataFrame(
    player_rankings, columns=["ALIAS", "ELO", "GAMES", "GAMES WON", "WIN RATE"]
).reset_index()
df["index"] = df["index"] + 1
df.set_index("index", inplace=True)
df["ELO"] = df["ELO"].astype(int)

df["ALIAS"] = df.apply(
    lambda x: f'🆕 {x["ALIAS"]}' if x["GAMES"] == 0 else x["ALIAS"],
    axis=1,
)

df["WIN RATE"] = df.apply(
    lambda x: f'{x["WIN RATE"]:.1%}',
    axis=1,
)

# Display the rankings in a table
st.table(df[["ALIAS", "ELO", "WIN RATE"]])
