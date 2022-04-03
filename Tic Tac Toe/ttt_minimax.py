import math


def draw_board(board):
    for row in range(3):
        for col in range(3):
            print(board[row][col], end=" ")
            if col < 2:
                print("|", end=" ")
        if row < 2:
            print("\n--+---+--")
    print("\n")


def check_win(board, shape):

    win = False
    # check rows
    for i, row in enumerate(board):
        if "".join(row) == shape * 3:
            win = True

    # check cols
    board_transpose = list(zip(*board))
    for i, col in enumerate(board_transpose):
        if "".join(col) == shape * 3:
            win = True

    # check diagonals
    if board[0][0] == shape and \
            board[1][1] == shape and \
            board[2][2] == shape:
        win = True

    elif board[0][2] == shape and \
            board[1][1] == shape and \
            board[2][0] == shape:
        win = True

    if win:
        if shape == computer_shape:
            return 1
        else:
            return -1


def check_tie(board):
    for row in board:
        for val in row:
            if val == " ":
                return False
    return True


def get_open_squares(board):
    possible_plays = []
    for i, row in enumerate(board):
        for j, col in enumerate(row):
            if board[i][j] == " ":
                possible_plays.append(i * 3 + j)
    return possible_plays


def get_player_move(board):
    while True:
        print(f"{player_shape} Player's Move")
        move = int(input("choose a nonempty square from 0-8: "))
        print()
        if move in get_open_squares(board):
            break
    play_move(board, move, player_shape)


def play_move(board, square_num, shape):
    board[square_num // 3][square_num % 3] = shape


def minimax(board, shape, alpha, beta):
    if check_win(board, shape):
        return check_win(board, shape)

    if check_tie(board):
        return 0

    if shape == computer_shape:
        value = -math.inf
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = computer_shape
                    value = max(value, minimax(board, player_shape, alpha, beta))
                    alpha = max(value, alpha)
                    board[i][j] = " "

                    if beta <= alpha:
                        break
            if beta <= alpha:
                break

        return value

    elif shape == player_shape:
        value = math.inf
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = player_shape
                    value = min(value, minimax(board, computer_shape, alpha, beta))
                    beta = min(value, beta)
                    board[i][j] = " "

                    if beta <= alpha:
                        break
            if beta <= alpha:
                break

        return value


def play_ai_move(board):
    best_score = -math.inf
    best_move = None
    for i in range(3):
        for j in range(3):
            if board[i][j] == " ":
                board[i][j] = computer_shape
                score = minimax(board, player_shape, -math.inf, math.inf)
                if score > best_score:
                    best_score = score
                    best_move = (i, j)
                board[i][j] = " "
    return best_move


board = [[" " for _ in range(3)] for _ in range(3)]
player_shape = "X"
computer_shape = "O"

draw_board(board)
while True:
    row, col = play_ai_move(board)
    board[row][col] = computer_shape
    draw_board(board)
    get_player_move(board)
    draw_board(board)



