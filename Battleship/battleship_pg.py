import pygame as pg
import numpy as np
import random
import sys

pg.init()
pg.display.set_caption("Battleship")
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
SCREEN = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
SQUARE_SIZE = 45
OFFSET_SIZE = 2
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class Battleship:

    def __init__(self):
        self.SHIP_MAP = np.zeros([10, 10])
        self.SHOT_MAP = np.zeros([10, 10])
        self.SHIP_SIZES = [6, 5, 3, 3, 2]
        self.GAME_OVER = False

        self.SCORE = 0
        self.NUM_GUESSES = 0
        self.GUESS_DELAY = 100
        self.GUESS_EVENT = pg.USEREVENT
        pg.time.set_timer(self.GUESS_EVENT, self.GUESS_DELAY)

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
                else:
                    continue
                break

    def guess_random(self):
        while True:
            guess_row, guess_col = random.choice(range(10)), random.choice(range(10))
            if self.SHOT_MAP[guess_row][guess_col] == 0:
                break

        self.SHOT_MAP[guess_row][guess_col] = 1
        self.NUM_GUESSES += 1

        if self.SHIP_MAP[guess_row][guess_col] == 1:
            self.SCORE += 1
        if self.SCORE == sum(self.SHIP_SIZES):
            self.GAME_OVER = True

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

                board_x += SQUARE_SIZE + OFFSET_SIZE

            board_y += SQUARE_SIZE + OFFSET_SIZE

    def reset_board(self):
        self.SCORE = 0
        self.SHIP_MAP = np.zeros([10, 10])
        self.SHOT_MAP = np.zeros([10, 10])

    def play(self):
        self.place_ships()
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == self.GUESS_EVENT:
                    self.guess_random()
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

            pg.display.update()


if __name__ == "__main__":
    Battleship().play()
