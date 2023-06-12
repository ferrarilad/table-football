from . import get_db_cursor, get_db_engine
from .games import get_player_aliases


def get_all_matches():
    conn = get_db_engine()
    c = get_db_cursor(conn)

    # Retrieve all matches from the database
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
        ORDER BY timestamp ASC
    """
    )
    matches = c.fetchall()
    return matches


def reset_player_scores():
    all_players = get_player_aliases()

    conn = get_db_engine()
    c = get_db_cursor(conn)

    for p in all_players:
        # Reset all player scores to the original value
        c.execute(
            """
            UPDATE players
            SET elo = ?, games_played = ?
            WHERE alias = ?;
            """,
            [1000, 0, p],
        )
        conn.commit()


def recompute_elo():
    conn = get_db_engine()
    c = get_db_cursor(conn)

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
            [blue_team_att, blue_team_def],
        ).fetchall()
        red_team_elo = c.execute(
            "SELECT alias, elo, games_played FROM players WHERE alias IN (?, ?)",
            [red_team_att, red_team_def],
        ).fetchall()

        blue_team_new_elo, red_team_new_elo = calculate_elo_rating(
            [_[1] for _ in blue_team_elo],
            [_[1] for _ in red_team_elo],
            1 * (blue_score == 10),
            k_factor=40,
        )

        for i, (player_, _, games_played_) in enumerate(blue_team_elo):
            c.execute(
                """
                UPDATE players
                SET elo = ?, games_played = ?
                WHERE alias = ?;
                """,
                [blue_team_new_elo[i], games_played_ + 1, player_],
            )
            conn.commit()

        for i, (player_, _, games_played_) in enumerate(red_team_elo):
            c.execute(
                """
                UPDATE players
                SET elo = ?, games_played = ?
                WHERE alias = ?;
                """,
                [red_team_new_elo[i], games_played_ + 1, player_],
            )
            conn.commit()


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

    team1_rating_change = [
        k_factor * (team1_result - 1 / (1 + 10 ** ((team2_avg_rating - rating) / 400)))
        for rating in team1_rating
    ]
    team2_rating_change = [
        k_factor
        * ((1 - team1_result) - 1 / (1 + 10 ** ((team1_avg_rating - rating) / 400)))
        for rating in team2_rating
    ]

    team1_new_ratings = [
        rating + rating_change
        for rating, rating_change in zip(team1_rating, team1_rating_change)
    ]
    team2_new_ratings = [
        rating + rating_change
        for rating, rating_change in zip(team2_rating, team2_rating_change)
    ]

    return tuple(team1_new_ratings), tuple(team2_new_ratings)


def calculate_elo_rating_old(team1_rating, team2_rating, team1_result, k_factor=40):
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
    # team2_expected_score = 1 - team1_expected_score

    team1_rating_change = k_factor * (team1_result - team1_expected_score)
    # team2_rating_change = k_factor * ((1 - team1_result) - team2_expected_score)

    team1_new_ratings = [rating + int(team1_rating_change) for rating in team1_rating]
    team2_new_ratings = [rating - int(team1_rating_change) for rating in team2_rating]

    return tuple(team1_new_ratings), tuple(team2_new_ratings)
