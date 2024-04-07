# Randomly simulate a chess game result

import numpy as np

def generate_game_results(win_draw_probs, n=1):
    """
    Vectorized generation of game results based on win/draw probabilities and multiplier n.

    :param win_draw_probs: A 2D array of shape (num_games, 2) with win and draw probabilities.
    :param n: Number of copies of game results.
    :return: A 2D array of game results with shape (num_games, n).
    """
    # Calculate lose probabilities
    lose_probs = 1 - np.sum(win_draw_probs, axis=1)

    # Expand the probabilities to match the output shape
    outcome_probs = np.column_stack([win_draw_probs, lose_probs[:, np.newaxis]])  # Shape: (num_games, 3)

    # Generate random numbers in the range [0, 1) for each outcome
    random_nums = np.random.rand(len(win_draw_probs), n)

    # Calculate cumulative probabilities to determine outcome thresholds
    cum_probs = np.cumsum(outcome_probs, axis=1)

    # Determine outcomes based on where the random number falls in the cumulative probabilities
    outcomes = np.sum(random_nums[:, :, np.newaxis] > cum_probs[:, np.newaxis, :], axis=2)

    # Map numeric outcomes to W, D, L
    outcome_map = np.array([1, 0.5, 0])
    result = outcome_map[outcomes]

    return result

def get_expected_score(eloDiff):
    """
    Calculate the probability of player 1 winning against player 2 using the normal distribution formula.
    
    :param eloDiff: Elo rating difference (rating1 - rating2).
    :return: Probability of player 1 winning.
    """
    return 1 / (1 + 10 ** (-eloDiff / 400))

def elo_per_pawn(elo):
    """
    Estimate the Elo rating equivalent of a 0.6 pawn advantage in chess.
    
    :param elo: Average Elo rating of two players.
    :return: Elo points equivalent to a 0.6 pawn advantage.
    """
    return np.exp(elo / 1020) * 26.59

def calculate_win_probability(rating1, rating2):
    """
    Calculate the win probability in chess based on the ratings of two players.
    
    :param rating1: Elo rating of player 1.
    :param rating2: Elo rating of player 2.
    :return: Win probability.
    """
    diff = rating1 - rating2
    expected_score = get_expected_score(diff)
    return expected_score - 0.5 * calculate_draw_probability(rating1, rating2)

def calculate_draw_probability(rating1, rating2):
    """
    Calculate the draw probability in chess based on the ratings of two players.
    
    :param rating1: Elo rating of player 1.
    :param rating2: Elo rating of player 2.
    :return: Draw probability.
    """
    diff = -1 * abs(rating1 - rating2)
    ave = (rating1 + rating2) / 2
    expected_score = get_expected_score(diff)
    eloPerPawn = elo_per_pawn(ave)
    eloShift = eloPerPawn * 0.6
    
    win_probability = get_expected_score(diff - eloShift)
    
    # Draw probability is calculated based on the difference between the expected score
    # and the win probability, considering that the expected score includes half the draw probability.
    draw_probability = (expected_score - win_probability) * 2
    return draw_probability

def get_results(games, ratings, n=1):
    """
    Generate game results based on the ratings of players in a series of games.
    
    :param games: A 2D array of shape (num_games, 2) with player ratings.
    :param ratings: A 1D array of player ratings.
    :param n: Number of copies of game results.
    :return: A 2D array of game results with shape (num_games, n).
    """
    win_draw_probs = np.array([[calculate_win_probability(ratings[game[0]], ratings[game[1]]),
                                calculate_draw_probability(ratings[game[0]], ratings[game[1]])] for game in games])
    return generate_game_results(win_draw_probs, n)