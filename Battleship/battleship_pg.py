import pygame as pg
import numpy as np
import random
import sys

pg.init()
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
SCREEN = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

BOARD = np.zeros([10, 10])
SQUARE_SIZE = 45
OFFSET_SIZE = 2
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

SHIP_SIZES = [6, 5, 3, 3, 2]


# switching to using numpy here will probably help a lot
def place_ships():
    for ship_size in SHIP_SIZES:

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
            if np.all(BOARD[start_row:end_row, start_col:end_col] == 0):
                BOARD[start_row:end_row, start_col:end_col] = 1
            else:
                continue
            break


def draw_board(board):
    board_y = 0
    for row in board:
        board_x = 0
        for val in row:
            if val == 0:
                pg.draw.rect(SCREEN, WHITE, pg.Rect(board_x, board_y, SQUARE_SIZE, SQUARE_SIZE))
            elif val == 1:
                pg.draw.rect(SCREEN, (111, 111, 111), pg.Rect(board_x, board_y, SQUARE_SIZE, SQUARE_SIZE))
                # pg.draw.line(SCREEN, BLACK,
                #              (board_x, board_y),
                #              (board_x + SQUARE_SIZE, board_y + SQUARE_SIZE),
                #              width=5)
                # pg.draw.line(SCREEN, BLACK,
                #              (board_x, board_y + SQUARE_SIZE),
                #              (board_x + SQUARE_SIZE, board_y),
                #              width=5)

            board_x += SQUARE_SIZE + OFFSET_SIZE

        board_y += SQUARE_SIZE + OFFSET_SIZE


def reset_board(board):
    for i in range(10):
        for j in range(10):
            board[i][j] = 0


pg.display.set_caption("Battleship")
place_ships()
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if event.type == pg.MOUSEBUTTONDOWN:
            mx, my = pg.mouse.get_pos()
            total_x_offset = (mx // SQUARE_SIZE) * OFFSET_SIZE
            total_y_offset = (my // SQUARE_SIZE) * OFFSET_SIZE
            board_x = (mx - total_x_offset) // SQUARE_SIZE
            board_y = (my - total_y_offset) // SQUARE_SIZE
            if (0 <= board_x <= 9) and (0 <= board_y <= 9):
                BOARD[board_y][board_x] = 1

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_r:
                reset_board(BOARD)
            if event.key == pg.K_s:
                reset_board(BOARD)
                place_ships()

    SCREEN.fill(BLACK)
    draw_board(BOARD)

    pg.display.update()
