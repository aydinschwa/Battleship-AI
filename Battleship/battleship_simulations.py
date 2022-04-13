import numpy as np
import matplotlib.pyplot as plt
import random
import time
from collections import Counter
import multiprocessing
import pickle


class Battleship:

    def __init__(self):
        self.SHIP_MAP = np.zeros([10, 10])
        self.SHIP_INFO = {"Carrier": 5, "Battleship": 4, "Destroyer": 3, "Submarine": 3, "Patrol Boat": 2}
        self.SHIP_COORDINATE_DICT = dict()
        self.COORDINATE_SHIP_DICT = dict()
        self.SUNK_SHIP_COORDINATES = []
        self.SHOT_MAP = np.zeros([10, 10])
        self.PROB_MAP = np.zeros([10, 10])

        # ai variables
        self.hunt = True
        self.targets = []

        self.SCORE = 0
        self.NUM_GUESSES = 0
        self.GAME_OVER = False

    def place_ships(self):
        for ship, ship_size in self.SHIP_INFO.items():
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
                        self.SHIP_COORDINATE_DICT[ship] = coord_list
                        for coord in coord_list:
                            self.COORDINATE_SHIP_DICT[coord] = ship
                    elif const_axis == "col":
                        coord_list = list(zip([row for row in range(start_row, end_row)], [start_col] * ship_size))
                        self.SHIP_COORDINATE_DICT[ship] = coord_list
                        for coord in coord_list:
                            self.COORDINATE_SHIP_DICT[coord] = ship

                else:
                    continue
                break

    def gen_prob_map(self):
        prob_map = np.zeros([10, 10])
        for ship_name in set(self.COORDINATE_SHIP_DICT.values()):
            ship_size = self.SHIP_INFO[ship_name]
            use_size = ship_size - 1
            # check where a ship will fit on the board
            for row in range(10):
                for col in range(10):
                    if self.SHOT_MAP[row][col] != 1:
                        # get potential ship endpoints
                        endpoints = []
                        # add 1 to all endpoints to compensate for python indexing
                        if row - use_size >= 0:
                            endpoints.append(((row - use_size, col), (row + 1, col + 1)))
                        if row + use_size <= 9:
                            endpoints.append(((row, col), (row + use_size + 1, col + 1)))
                        if col - use_size >= 0:
                            endpoints.append(((row, col - use_size), (row + 1, col + 1)))
                        if col + use_size <= 9:
                            endpoints.append(((row, col), (row + 1, col + use_size + 1)))

                        for (start_row, start_col), (end_row, end_col) in endpoints:
                            if np.all(self.SHOT_MAP[start_row:end_row, start_col:end_col] == 0):
                                prob_map[start_row:end_row, start_col:end_col] += 1

                    # increase probability of attacking squares near successful hits
                    if self.SHOT_MAP[row][col] == 1 and \
                            self.SHIP_MAP[row][col] == 1 and \
                            (row, col) not in self.SUNK_SHIP_COORDINATES:  # un-weight hits on sunk ships

                        if (row + 1 <= 9) and (self.SHOT_MAP[row + 1][col] == 0):
                            if (row - 1 >= 0) and \
                                    (row - 1, col) not in self.SUNK_SHIP_COORDINATES and \
                                    (self.SHOT_MAP[row - 1][col] == self.SHIP_MAP[row - 1][col] == 1):
                                prob_map[row + 1][col] += 15
                            else:
                                prob_map[row + 1][col] += 10

                        if (row - 1 >= 0) and (self.SHOT_MAP[row - 1][col] == 0):
                            if (row + 1 <= 9) and \
                                    (row + 1, col) not in self.SUNK_SHIP_COORDINATES and \
                                    (self.SHOT_MAP[row + 1][col] == self.SHIP_MAP[row + 1][col] == 1):
                                prob_map[row - 1][col] += 15
                            else:
                                prob_map[row - 1][col] += 10

                        if (col + 1 <= 9) and (self.SHOT_MAP[row][col + 1] == 0):
                            if (col - 1 >= 0) and \
                                    (row, col - 1) not in self.SUNK_SHIP_COORDINATES and \
                                    (self.SHOT_MAP[row][col - 1] == self.SHIP_MAP[row][col - 1] == 1):
                                prob_map[row][col + 1] += 15
                            else:
                                prob_map[row][col + 1] += 10

                        if (col - 1 >= 0) and (self.SHOT_MAP[row][col - 1] == 0):
                            if (col + 1 <= 9) and \
                                    (row, col + 1) not in self.SUNK_SHIP_COORDINATES and \
                                    (self.SHOT_MAP[row][col + 1] == self.SHIP_MAP[row][col + 1] == 1):
                                prob_map[row][col - 1] += 15
                            else:
                                prob_map[row][col - 1] += 10

                    # decrease probability for misses to zero
                    elif self.SHOT_MAP[row][col] == 1 and self.SHIP_MAP[row][col] != 1:
                        prob_map[row][col] = 0

        self.PROB_MAP = prob_map

    def reset_board(self):
        self.__init__()

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

    def guess_prob(self):
        self.gen_prob_map()
        # get the row, col numbers of the largest element in PROB_MAP
        # https://thispointer.com/find-max-value-its-index-in-numpy-array-numpy-amax/
        max_indices = np.where(self.PROB_MAP == np.amax(self.PROB_MAP))
        guess_row, guess_col = max_indices[0][0], max_indices[1][0]

        return guess_row, guess_col

    def shoot(self, guess_row, guess_col):
        self.SHOT_MAP[guess_row][guess_col] = 1
        self.NUM_GUESSES += 1

        if self.SHIP_MAP[guess_row][guess_col] == 1:
            self.SCORE += 1
            ship = self.COORDINATE_SHIP_DICT.pop((guess_row, guess_col))
            # if ship is sunk, add its coordinates to list of sunken ship coordinates
            if ship not in self.COORDINATE_SHIP_DICT.values():
                self.SUNK_SHIP_COORDINATES.extend(self.SHIP_COORDINATE_DICT[ship])
                self.SHIP_COORDINATE_DICT.pop(ship)

        if self.SCORE == sum(self.SHIP_INFO.values()):
            self.GAME_OVER = True

    def simulate_games(self, num_games, strategy="random"):
        start_time = time.time()
        all_guesses = []
        for i in range(num_games):
            print(i) if i % 10 == 0 else 0
            self.place_ships()
            while not self.GAME_OVER:
                if strategy == "random":
                    guess_row, guess_col = self.guess_random()
                elif strategy == "hunt_target":
                    guess_row, guess_col = self.hunt_target()
                elif strategy == "hunt_target_parity":
                    guess_row, guess_col = self.hunt_target(2)
                elif strategy == "hunt_target_min_parity":
                    smallest_remaining_ship = min([self.SHIP_INFO[ship] for ship in self.COORDINATE_SHIP_DICT.values()])
                    guess_row, guess_col = self.hunt_target(smallest_remaining_ship)
                elif strategy == "prob":
                    guess_row, guess_col = self.guess_prob()
                else:
                    raise Exception(f"invalid strategy chosen: {strategy}")
                self.shoot(guess_row, guess_col)
            all_guesses.append(self.NUM_GUESSES)
            self.reset_board()
        print(f'{time.time() - start_time:.2f} seconds to simulate {num_games} games with the "{strategy}" strategy')
        return all_guesses


def plot_games(num_guesses):
    games_by_score = Counter(num_guesses)
    for i in range(101):
        if i not in games_by_score.keys():
            games_by_score[i] = 0
    games_by_score = dict(sorted(games_by_score.items(), key=lambda item: item[0]))
    plt.plot(games_by_score.keys(), games_by_score.values())


def sim_all_strategies(num_games=1):
    random_guesses = Battleship().simulate_games(num_games, strategy="random")
    ht_guesses = Battleship().simulate_games(num_games, strategy="hunt_target")
    ht_parity_guesses = Battleship().simulate_games(num_games, strategy="hunt_target_parity")
    ht_parity_min_guesses = Battleship().simulate_games(num_games, strategy="hunt_target_min_parity")
    prob_guesses = Battleship().simulate_games(num_games, strategy="prob")

    return random_guesses, ht_guesses, ht_parity_guesses, ht_parity_min_guesses, prob_guesses


def plot_all_strategies(guess_lists):
    for guess_list in guess_lists:
        plot_games(guess_list)


def sim_strategy(file_num, num_games=200000):
    prob_guesses = Battleship().simulate_games(num_games, strategy="hunt_target_min_parity")
    FileStore = open(f"stored_objects/guesses_{file_num}.pickle", "wb")
    pickle.dump(prob_guesses, FileStore)
    FileStore.close()


if __name__ == "__main__":
    processes = []
    for i in range(5):
        p = multiprocessing.Process(target=sim_strategy, args=(str(i),))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    all_guesses = []

    print(len(all_guesses))
