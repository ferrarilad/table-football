import streamlit as st

try:
    from streamlit import cache_resource
except:
    from streamlit import experimental_singleton as cache_resource


def page_init(title: str):
    st.set_page_config(
        page_title=f"{title} - Table Football",
        page_icon="⚽",
        initial_sidebar_state="auto",
        menu_items=None,
    )

    st.header(title)


def get_db_engine():
    import sqlite3

    return sqlite3.connect("./database.db")


def get_db_cursor(engine):
    return engine.cursor()


LOCALES = ["IT", "UK"]
