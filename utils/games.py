from . import get_db_cursor, get_db_engine


def get_player_aliases():
    conn = get_db_engine()
    c = get_db_cursor(conn)

    # Retrieve player aliases from the database
    c.execute("SELECT LOWER(alias) as alias FROM players")
    player_aliases = c.fetchall()

    # Flatten the list of aliases
    return [alias[0] for alias in player_aliases]


def valid_goals(blue_score, red_score):
    return blue_score == 10 or red_score == 10


def valid_teams(blue_team_att, blue_team_def, red_team_att, red_team_def):
    if blue_team_def is None and red_team_def is None and blue_team_att != red_team_att:
        return True
    return len({blue_team_att, blue_team_def, red_team_att, red_team_def}) == 4
