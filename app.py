import pandas as pd
import streamlit as st

from utils import get_db_engine, get_db_cursor, page_init

page_init("Player Ranking")


def main():
    st.header("Work Hard, have fun, make history...⚽")

    st.sidebar.subheader("Instructions")
    st.sidebar.write(
        """
    To participate to the competition: 
    1. Only the first time: select \"Player Registration\" and add your identifier\n
    2. Play a match\n
    3. Register the game in the \"Register match\" section\n
    4. See your ranking in  \"Player Ranking\"
    """
    )

    show_player_ranking()


def show_player_ranking():
    st.subheader("Instructions")
    st.write(
        """
    To participate to the competition: 
    1. Only the first time: select \"Player Registration\" and add your identifier\n

    2. Play a match\n
    3. Register the game in the \"Register match\" section\n
    4. See your ranking in  \"Player Ranking\"
    """
    )

    st.write("Ranked players by Elo:")

    conn = get_db_engine()
    c = get_db_cursor(conn)

    # Retrieve player rankings from the database
    c.execute("SELECT LOWER(alias) as alias, elo, games_played FROM players ORDER BY elo DESC")
    player_rankings = c.fetchall()

    df = pd.DataFrame(player_rankings, columns=["ALIAS", "ELO", "GAMES"])

    df["ALIAS"] = df.apply(
        lambda x: f'🆕 {x["ALIAS"]}' if x["GAMES"] == 0 else x["ALIAS"],
        axis=1,
    )

    # Display the rankings in a table
    st.table(df[["ALIAS", "ELO"]])


if __name__ == "__main__":
    main()
