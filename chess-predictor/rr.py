# For round robin tournaments

from chess import get_results

class RoundRobinTournament:

    def __init__(self, names, ratings, n_games=1):
        self.names = names
        self.ratings = ratings
        self.n_games = n_games
        self.completed_games = {}

    def add_games(self, games):
        for game in games:
            id1, id2, result = game
            pair = (id1, id2) if id1 < id2 else (id2, id1)
            result = result if id1 < id2 else 1 - result
            if pair not in self.completed_games:
                self.completed_games[pair] = []
            if len(self.completed_games[pair]) < self.n_games:
                self.completed_games[pair].append(result)

    def calculate_standings(self, completed_games=None):
        """
        Calculate the current standings based on completed games.
        """
        if completed_games is None:
            completed_games = self.completed_games
    
        standings = {name: 0 for name in self.names}
        for game, results in completed_games.items():
            for result in results:
                standings[self.names[game[0]]] += result
                standings[self.names[game[1]]] += 1 - result
        return standings
    
    def get_winners(self, completed_games=None):
        """
        Get the winners of the tournament based on the current standings.
        """
        standings = self.calculate_standings(completed_games)
        max_score = max(standings.values())
        winners = [name for name, score in standings.items() if score == max_score]
        return winners

    def get_odds(self, n=1):
        games_to_play = []
        for id1 in range(len(self.names)):
            for id2 in range(id1 + 1, len(self.names)):
                pair = (id1, id2)
                if pair not in self.completed_games:
                    games_to_play.extend([pair] * self.n_games)
                elif len(self.completed_games[pair]) < self.n_games:
                    games_to_play.extend([pair] * (self.n_games - len(self.completed_games[pair])))

        if not games_to_play:
            winners = self.get_winners()
            return {winner: 1 for winner in winners} + {name: 0 for name in self.names if name not in winners}
        
        simulated_results = get_results(games_to_play, self.ratings, n)
        # Initialize odds dictionary
        odds = {name: 0 for name in self.names}

        for i in range(n):
            temp_completed_games = {k: [res for res in v] for k, v in self.completed_games.items()}
            for j, game in enumerate(games_to_play):
                result = simulated_results[j][i]
                temp_completed_games.setdefault(game, []).append(result)
            standings = self.calculate_standings(temp_completed_games)
            max_score = max(standings.values())
            winners = [name for name, score in standings.items() if score == max_score]
            for winner in winners:
                odds[winner] += 1 / n
    
        return odds

def import_rr_tournament(filename):
    """
    Import the results of a round-robin chess tournament from a CSV file.
    
    :param filename: Path to the CSV file.
    :return: A 2D array of game results with shape (num_games, n).
    """

    lines = open(filename).readlines()
    n_games = int(lines[0].strip())
    # First line contains player names.
    player_names = lines[1].strip().split(',')
    # Second line is ratings
    player_ratings = lines[2].strip().split(',')
    player_ratings = [float(rating) for rating in player_ratings]
    # Remaining lines are game outcomes
    # Format is player1_name,player2_name,result
    game_results = open(filename).readlines()[3:]
    games = []
    for result in game_results:
        player1, player2, outcome = result.strip().split(',')
        games.append((player_names.index(player1), player_names.index(player2), float(outcome)))
    tournament = RoundRobinTournament(player_names, player_ratings, n_games)
    tournament.add_games(games)
    return tournament

def main():
    tournament = import_rr_tournament('candidates2024.txt')
    odds = tournament.get_odds(1000000)
    print(odds)

if __name__ == '__main__':
    main()