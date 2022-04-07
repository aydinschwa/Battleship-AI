import numpy as np
import matplotlib.pyplot as plt
import random
import time
from collections import Counter


class Battleship:

    def __init__(self):
        self.SHIP_MAP = np.zeros([10, 10])
        self.SHOT_MAP = np.zeros([10, 10])
        self.SHIP_SIZES = [5, 4, 3, 3, 2]
        self.SHIP_COORDINATES = dict()

        self.targets = []

        self.SCORE = 0
        self.NUM_GUESSES = 0
        self.GAME_OVER = False

    def place_ships(self):
        for ship_size in self.SHIP_SIZES:

            # select random start point for ship that isn't on top of another ship
            while True:
                start_row = random.choice(range(10))
                start_col = random.choice(range(10))

                # randomly choose an axis to hold constant
                const_axis = random.choice(["row", "col"])

                # randomly choose a direction
                direction = random.choice(["up", "down"])

                # select endpoint
                if const_axis == "row":
                    if direction == "up" and start_col - ship_size >= 0:
                        end_row = start_row + 1
                        end_col = start_col - ship_size
                        start_col, end_col = end_col, start_col
                    elif direction == "down" and start_col + ship_size <= 9:
                        end_row = start_row + 1
                        end_col = start_col + ship_size
                    else:
                        continue

                elif const_axis == "col":
                    if direction == "up" and start_row - ship_size >= 0:
                        end_row = start_row - ship_size
                        start_row, end_row = end_row, start_row
                        end_col = start_col + 1
                    elif direction == "down" and start_row + ship_size <= 9:
                        end_row = start_row + ship_size
                        end_col = start_col + 1
                    else:
                        continue

                # check that all spaces that we want to insert into are clear
                if np.all(self.SHIP_MAP[start_row:end_row, start_col:end_col] == 0):
                    self.SHIP_MAP[start_row:end_row, start_col:end_col] = 1

                    # create a quickly-searchable dictionary of coordinates mapped to ships
                    if const_axis == "row":
                        coord_list = list(zip([start_row] * ship_size, [col for col in range(start_col, end_col)]))
                        for coord in coord_list:
                            self.SHIP_COORDINATES[coord] = ship_size
                    elif const_axis == "col":
                        coord_list = list(zip([row for row in range(start_row, end_row)], [start_col] * ship_size))
                        for coord in coord_list:
                            self.SHIP_COORDINATES[coord] = ship_size

                else:
                    continue
                break

    def reset_board(self):
        self.SHIP_MAP = np.zeros([10, 10])
        self.SHOT_MAP = np.zeros([10, 10])
        self.SHIP_SIZES = [6, 5, 3, 3, 2]
        self.GAME_OVER = False

        self.targets = []

        self.SCORE = 0
        self.NUM_GUESSES = 0

    def guess_random(self, parity=None):
        while True:
            guess_row, guess_col = random.choice(range(10)), random.choice(range(10))
            if parity:
                if (guess_row + guess_col) % parity != 0:
                    continue
            if self.SHOT_MAP[guess_row][guess_col] == 0:
                break

        return guess_row, guess_col

    def hunt_target(self, parity=None):
        # enter hunt mode when no more targets left
        if not self.targets:
            guess_row, guess_col = self.guess_random(parity)
        else:
            guess_row, guess_col = self.targets.pop()

        if self.SHIP_MAP[guess_row][guess_col] == 1:
            # add all adjacent squares to list of potential targets where possible
            potential_targets = [(guess_row + 1, guess_col), (guess_row, guess_col + 1),
                                 (guess_row - 1, guess_col), (guess_row, guess_col - 1)]
            for target_row, target_col in potential_targets:
                if (0 <= target_row <= 9) and \
                   (0 <= target_col <= 9) and \
                   (self.SHOT_MAP[target_row][target_col] == 0) and \
                   ((target_row, target_col) not in self.targets):
                    self.targets.append((target_row, target_col))

        return guess_row, guess_col

    def shoot(self, guess_row, guess_col):
        self.SHOT_MAP[guess_row][guess_col] = 1
        self.NUM_GUESSES += 1

        if self.SHIP_MAP[guess_row][guess_col] == 1:
            self.SCORE += 1
            self.SHIP_COORDINATES.pop((guess_row, guess_col))

        if self.SCORE == sum(self.SHIP_SIZES):
            self.GAME_OVER = True

    def simulate_games(self, num_runs=100, strategy="random"):
        start_time = time.time()
        all_guesses = []
        for _ in range(num_runs):
            self.place_ships()
            while not self.GAME_OVER:
                if strategy == "random":
                    guess_row, guess_col = self.guess_random()
                elif strategy == "hunt_target":
                    guess_row, guess_col = self.hunt_target()
                elif strategy == "hunt_target_parity":
                    guess_row, guess_col = self.hunt_target(2)
                elif strategy == "hunt_target_min_parity":
                    guess_row, guess_col = self.hunt_target(min(self.SHIP_COORDINATES.values()))
                else:
                    raise Exception(f"invalid strategy chosen: {strategy}")
                self.shoot(guess_row, guess_col)
            all_guesses.append(self.NUM_GUESSES)
            self.reset_board()
        print(f'{time.time() - start_time:.2f} seconds to simulate {num_runs} games with the "{strategy}"strategy')
        return all_guesses


def plot_games(num_guesses):
    games_by_score = Counter(num_guesses)
    for i in range(101):
        if i not in games_by_score.keys():
            games_by_score[i] = 0
    games_by_score = dict(sorted(games_by_score.items(), key=lambda item: item[0]))
    plt.plot(games_by_score.keys(), games_by_score.values())


if __name__ == "__main__":
    num_games = 1000
    random_guesses = Battleship().simulate_games(num_games, strategy="random")
    ht_guesses = Battleship().simulate_games(num_games, strategy="hunt_target")
    ht_parity_guesses = Battleship().simulate_games(num_games, strategy="hunt_target_parity")
    ht_parity_min_guesses = Battleship().simulate_games(num_games, strategy="hunt_target_min_parity")
    plot_games(random_guesses)
    plot_games(ht_guesses)
    plot_games(ht_parity_guesses)
    plot_games(ht_parity_min_guesses)
    plt.show()
