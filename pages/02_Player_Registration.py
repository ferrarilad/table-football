import streamlit as st

from utils import get_db_engine, get_db_cursor, page_init

page_init("Player Registration")

st.write("Register a new player")

# Get user input for player alias
alias = st.text_input("Player Alias")

# Submit button
if st.button("Register"):
    alias = alias.lower()

    conn = get_db_engine()
    c = get_db_cursor(conn)

    # Check if the alias already exists in the database
    c.execute("SELECT COUNT(*) FROM players WHERE alias=?", (alias,))
    alias_count = c.fetchone()[0]

    if alias_count > 0:
        st.error("Player alias already exists. Please choose a unique alias.")
    else:
        # Insert the new player into the database with a starting Elo score of 1000
        c.execute(
            "INSERT INTO players (alias, elo, games_played) VALUES (?, ?, ?)",
            (alias, 1000, 0),
        )
        conn.commit()
        st.success("Player registered successfully!")
