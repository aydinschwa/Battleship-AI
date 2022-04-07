import pygame as pg
import numpy as np
import random
import sys

pg.init()
pg.display.set_caption("Battleship")
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 500
SCREEN = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
SQUARE_SIZE = 45
OFFSET_SIZE = 2
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)


class Battleship:

    def __init__(self):

        self.SHIP_MAP = np.zeros([10, 10])
        self.SHIP_SIZES = [5, 4, 3, 3, 2]
        self.SHIP_COORDINATES = dict()
        self.SHOT_MAP = np.zeros([10, 10])
        self.PROB_MAP = np.zeros([10, 10])

        # ai variables
        self.hunt = True
        self.targets = []

        self.SCORE = 0
        self.NUM_GUESSES = 0
        self.GUESS_DELAY = 500
        self.GUESS_EVENT = pg.USEREVENT
        pg.time.set_timer(self.GUESS_EVENT, self.GUESS_DELAY)
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

    def gen_prob_map(self):
        prob_map = np.zeros([10, 10])
        for ship_size in set(self.SHIP_COORDINATES.values()):
            print(set(self.SHIP_COORDINATES.values()))
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
                    if self.SHOT_MAP[row][col] == 1 and self.SHIP_MAP[row][col] == 1:
                        if (row + 1 <= 9) and (self.SHOT_MAP[row + 1][col] == 0):
                            prob_map[row + 1][col] += 10
                        if (row - 1 >= 0) and (self.SHOT_MAP[row - 1][col] == 0):
                            prob_map[row - 1][col] += 10
                        if (col + 1 <= 9) and (self.SHOT_MAP[row][col + 1] == 0):
                            prob_map[row][col + 1] += 10
                        if (col - 1 >= 0) and (self.SHOT_MAP[row][col - 1] == 0):
                            prob_map[row][col - 1] += 10

                    # decrease probability for misses to zero
                    elif self.SHOT_MAP[row][col] == 1 and self.SHIP_MAP[row][col] != 1:
                        prob_map[row][col] = 0

        self.PROB_MAP = prob_map

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

    def draw_board(self):
        board_y = 0
        for i in range(10):
            board_x = 0
            for j in range(10):
                if self.SHIP_MAP[i][j] == 0:
                    pg.draw.rect(SCREEN, WHITE, pg.Rect(board_x, board_y, SQUARE_SIZE, SQUARE_SIZE))
                elif self.SHIP_MAP[i][j] == 1:
                    pg.draw.rect(SCREEN, (111, 111, 111), pg.Rect(board_x, board_y, SQUARE_SIZE, SQUARE_SIZE))

                if self.SHOT_MAP[i][j] == 1:
                    pg.draw.line(SCREEN, BLACK,
                                 (board_x, board_y),
                                 (board_x + SQUARE_SIZE, board_y + SQUARE_SIZE),
                                 width=5)
                    pg.draw.line(SCREEN, BLACK,
                                 (board_x, board_y + SQUARE_SIZE),
                                 (board_x + SQUARE_SIZE, board_y),
                                 width=5)

                if self.SHIP_MAP[i][j] == 1 and self.SHOT_MAP[i][j] == 1:
                    pg.draw.line(SCREEN, RED,
                                 (board_x, board_y),
                                 (board_x + SQUARE_SIZE, board_y + SQUARE_SIZE),
                                 width=5)
                    pg.draw.line(SCREEN, RED,
                                 (board_x, board_y + SQUARE_SIZE),
                                 (board_x + SQUARE_SIZE, board_y),
                                 width=5)

                board_x += SQUARE_SIZE + OFFSET_SIZE

            board_y += SQUARE_SIZE + OFFSET_SIZE

    def draw_heat_map(self):
        board_y = 0
        for i in range(10):
            board_x = 500
            for j in range(10):
                if np.sum(self.PROB_MAP):
                    pass
                    pg.draw.rect(SCREEN, (self.PROB_MAP[i][j] * 3, 0, 0), pg.Rect(board_x, board_y, SQUARE_SIZE, SQUARE_SIZE))

                board_x += SQUARE_SIZE + OFFSET_SIZE

            board_y += SQUARE_SIZE + OFFSET_SIZE

    def reset_board(self):
        self.SHIP_MAP = np.zeros([10, 10])
        self.SHOT_MAP = np.zeros([10, 10])
        self.SHIP_SIZES = [6, 5, 3, 3, 2]
        self.GAME_OVER = False

        self.targets = []

        self.SCORE = 0
        self.NUM_GUESSES = 0

    def shoot(self, guess_row, guess_col):
        self.SHOT_MAP[guess_row][guess_col] = 1
        self.NUM_GUESSES += 1

        if self.SHIP_MAP[guess_row][guess_col] == 1:
            self.SCORE += 1
            self.SHIP_COORDINATES.pop((guess_row, guess_col))

        if self.SCORE == sum(self.SHIP_SIZES):
            self.GAME_OVER = True

    def play(self):
        self.place_ships()
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == self.GUESS_EVENT:
                    guess_row, guess_col = self.guess_prob()
                    self.shoot(guess_row, guess_col)

                if event.type == pg.MOUSEBUTTONDOWN:
                    mx, my = pg.mouse.get_pos()
                    total_x_offset = (mx // SQUARE_SIZE) * OFFSET_SIZE
                    total_y_offset = (my // SQUARE_SIZE) * OFFSET_SIZE
                    board_x = (mx - total_x_offset) // SQUARE_SIZE
                    board_y = (my - total_y_offset) // SQUARE_SIZE
                    if (0 <= board_x <= 9) and (0 <= board_y <= 9):
                        self.SHOT_MAP[board_y][board_x] = 1

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_r:
                        self.reset_board()
                    if event.key == pg.K_s:
                        self.reset_board()
                        self.place_ships()

            if self.GAME_OVER:
                print(self.NUM_GUESSES)
                pg.quit()
                sys.exit()

            SCREEN.fill(BLACK)
            self.draw_board()
            self.draw_heat_map()

            pg.display.update()


if __name__ == "__main__":
    Battleship().play()
