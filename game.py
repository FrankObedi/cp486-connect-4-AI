from random import shuffle
import numpy as np
from math import inf as infinity
from random import choice as random_choice
from time import time
import json

PLAYER_AI = 1
PLAYER_HUMAN = 2
STR_PLAYER_AI = 'A'
STR_PLAYER_HUMAN = 'H'
ROWS = 6
COLS = 7
WINDOW_SIZE = 4  # the connect number
WINDOW_SIZE_LESS1 = WINDOW_SIZE-1


def display_board(board, values=False):
    '''
    Display the current state of the board.
    values: if values is true then it displays the array as is. else it displays the string value
    '''
    for r in range(ROWS):
        row_string = f'{r}  |'
        for player in board[r]:
            if values:
                row_string += f' {player} |'
            else:
                if player == PLAYER_AI:
                    row_string += f' {STR_PLAYER_AI} |'
                elif player == PLAYER_HUMAN:
                    row_string += f' {STR_PLAYER_HUMAN} |'
                else:
                    row_string += ' - |'
        print(row_string)
    col_string = "    "
    for c in range(COLS):
        col_string += f" {c}  "
    print(col_string)
    return


def generate_board(COLS, ROWS):
    '''
    Generates the game board every time the game starts
    '''
    return np.array([[0] * COLS] * ROWS)


def get_json_board(board):
    # Convert the NumPy array to a Python list
    board_list = board.tolist()
    # Convert the Python list to a JSON string
    json_board = json.dumps(board_list)
    return json_board


def get_possible_moves(board):
    '''
    Returns a list of columns that are still available.
    Orders the columns favouring the center columns.
    '''
    available_cols = []
    available_cols_ordered = []
    for c in range(COLS):
        if board[0][c] == 0:
            available_cols.append(c)
    mid = len(available_cols)//2
    i = 0
    if len(available_cols) == 0:
        return []
    while len(available_cols_ordered) != len(available_cols) or i <= mid:
        if i == 0:
            available_cols_ordered.append(available_cols[mid+i])
        else:
            available_cols_ordered.append(available_cols[mid-i])
            if len(available_cols_ordered) == len(available_cols):
                break
            available_cols_ordered.append(available_cols[mid+i])
        i += 1
    # shuffle(available_cols_ordered)   # shuffle to test ai vs ai
    return available_cols_ordered


def select_move(possible_moves, selection):
    '''
    Gives human player the option of selecting one of the available moves.
    Returns a column number
    Returns None if error occurs.
    '''
    completed_move = False
    while completed_move == False:
        try:
            if selection in possible_moves:
                return selection
            # move not found
            selection = None
            print("Error: invalid move")
        except:
            print("Error: invalid move")
    return None


def drop_puck(board, col, player):
    '''
    Drop the players puck in the chosen column.
    '''
    r = 0
    if board[r][col] != 0:
        print(f"ERROR: cannot drop puck in column {col}")
        return
    while r < ROWS-1 and board[r+1][col] == 0:
        r += 1
    board[r][col] = player
    return board


def switch_player(player):
    '''
    Return the opposite player.
    '''
    if player == PLAYER_AI:
        return PLAYER_HUMAN
    else:
        return PLAYER_AI

# def is_winning_move(board, piece):
    '''
    Original
    code taken from https://github.com/KeithGalli/Connect4-Python/blob/master/connect4_with_ai.py#L67
    '''
    # Check horizontal locations for win
    for c in range(COLS-3):
        for r in range(ROWS-4, 0, -1):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    # Check vertical locations for win
    for c in range(COLS):
        for r in range(ROWS-4, 0, -1):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    # Check positively sloped diaganols
    for c in range(COLS-3):
        for r in range(ROWS-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    # Check negatively sloped diaganols
    for c in range(COLS-3):
        for r in range(3, ROWS):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True
    return False

# def is_winning_move(board, piece):
    '''
    code taken from https://github.com/KeithGalli/Connect4-Python/blob/master/connect4_with_ai.py#L67
        modified for connect N. Slightly slower than above version
    '''
    # Check horizontal locations for win
    for c in range(COLS-(WINDOW_SIZE-1)):
        for r in range(ROWS):
            count = 0
            for i in range(WINDOW_SIZE):
                if board[r][c+i] == piece:
                    count += 1
            if count == WINDOW_SIZE:
                return True

    # Check vertical locations for win
    for c in range(COLS):
        for r in range(ROWS-(WINDOW_SIZE-1)):
            count = 0
            for i in range(WINDOW_SIZE):
                if board[r+i][c] == piece:
                    count += 1
            if count == WINDOW_SIZE:
                return True

    # Check positively sloped diaganols
    for c in range(COLS-(WINDOW_SIZE-1)):
        for r in range(ROWS-(WINDOW_SIZE-1)):
            count = 0
            for i in range(WINDOW_SIZE):
                if board[r+i][c+i] == piece:
                    count += 1
            if count == WINDOW_SIZE:
                return True

    # Check negatively sloped diaganols
    for c in range(COLS-(WINDOW_SIZE-1)):
        for r in range((WINDOW_SIZE-1), ROWS):
            count = 0
            for i in range(WINDOW_SIZE):
                if board[r-i][c+i] == piece:
                    count += 1
            if count == WINDOW_SIZE:
                return True


def is_game_over(board):
    if np.any(board == 0):
        return False
    return True


def print_board(board):
    for row in board:
        print("|", end="")
        for cell in row:
            print(cell, end="|")
        print()


def is_winning_move(board, player):
    '''
    Returns True if this move would result in winnning the game.
    False otherwise.
    '''
    # Check vertically
    for c in range(COLS):
        count = 0  # number of occupied squares by player in a succession
        for r in range(ROWS):
            # no point in counting the rest
            if (r > ROWS-WINDOW_SIZE and count == 0):
                break
            # this player has the square, increase counter
            if (board[r][c] == player):
                count += 1
                if count == WINDOW_SIZE:
                    return True
            # opponent found
            elif (board[r][c] == switch_player(player)):
                break

    # Check horizontally
    break_flag = False
    for r in range(ROWS-1, -1, -1):
        count = 0  # number of occupied squares by player in a succession
        occupied_count = 0  # number of occupied squares irrespective of player
        for c in range(COLS):
            # no point in checking the rest. cant make 4 on this row
            if (c > COLS - WINDOW_SIZE and count == 0 and occupied_count == 0):
                break
            # count occupied square
            if (board[r][c] != 0):
                occupied_count += 1

            # this player has the square, increase counter
            if (board[r][c] == player):
                count += 1
                if count == WINDOW_SIZE:
                    return True
            # not this player or square is empty, reset counter
            else:
                count = 0
            # if a row is scanned and only counted <= 3 occupied squares
            # cancel searching the board. cannot make 4 above this row
            if (c == COLS-1 and occupied_count <= WINDOW_SIZE_LESS1):
                break_flag = True
                break
        if break_flag:  # cancel searching the board
            break

    # Check positively sloped diaganols
    for c in range(COLS-WINDOW_SIZE_LESS1):
        for r in range(ROWS-WINDOW_SIZE_LESS1):
            count = 0
            for i in range(WINDOW_SIZE):
                if board[r+i][c+i] == player:
                    count += 1
            if count == WINDOW_SIZE:
                return True

    # Check negatively sloped diaganols
    for c in range(COLS-WINDOW_SIZE_LESS1):
        for r in range(WINDOW_SIZE_LESS1, ROWS):
            count = 0
            for i in range(WINDOW_SIZE):
                if board[r-i][c+i] == player:
                    count += 1
            if count == WINDOW_SIZE:
                return True
    return False


def evaluate_window(window, player):
    '''
    Evaluates a single window.
    code taken from https://github.com/KeithGalli/Connect4-Python/blob/master/connect4_with_ai.py#L67
    '''
    score = 0
    opponent = switch_player(player)

    if window.count(player) == WINDOW_SIZE:
        score += 100
    elif window.count(player) == WINDOW_SIZE - 1 and window.count(0) == 1:
        score += 5
    elif window.count(player) == WINDOW_SIZE - 2 and window.count(0) == 2:
        score += 2
    # for a connect N > 4 add more clauses and change points up
    # elif window.count(player) == WINDOW_SIZE - 3 and window.count(0) == 3:
    #     score += 1

    if window.count(opponent) == WINDOW_SIZE - 1 and window.count(0) == 1:
        score -= 4
    return score


def evaluate_board(board, player):
    '''
    Evaluates the board state and returns a score in terms of the provided player.
    code taken from https://github.com/KeithGalli/Connect4-Python/blob/master/connect4_with_ai.py#L67
    '''
    value = 0
    # Vertical
    for c in range(COLS):
        column = [board[row][c] for row in range(ROWS)]
        for r in range(ROWS-WINDOW_SIZE_LESS1):
            window = column[r:r + WINDOW_SIZE]
            value += evaluate_window(window, player)

    # Horizontal
    for r in range(ROWS):
        row = [board[r][col] for col in range(COLS)]
        for c in range(COLS-WINDOW_SIZE_LESS1):
            window = row[c:c + WINDOW_SIZE]
            value += evaluate_window(window, player)

    # Diagonal Negative Slope
    for r in range(ROWS-WINDOW_SIZE_LESS1):
        for c in range(COLS-WINDOW_SIZE_LESS1):
            window = [board[r+i][c+i] for i in range(WINDOW_SIZE)]
            value += evaluate_window(window, player)

    # Diagonal Positive Slope
    for r in range(ROWS-WINDOW_SIZE_LESS1):
        for c in range(COLS-WINDOW_SIZE_LESS1):
            window = [board[r-i+WINDOW_SIZE_LESS1][c+i]
                      for i in range(WINDOW_SIZE)]
            value += evaluate_window(window, player)
    return value


def minimax(board, depth, alpha, beta, maximizingPlayer):
    '''
    Minimax algorithm
    code taken from https://github.com/KeithGalli/Connect4-Python/blob/master/connect4_with_ai.py#L67
    '''
    possible_moves = get_possible_moves(board)
    ai_wins = is_winning_move(board, PLAYER_AI)
    human_wins = is_winning_move(board, PLAYER_HUMAN)
    is_terminal = len(possible_moves) == 0 or ai_wins or human_wins

    if depth == 0 or is_terminal:
        if is_terminal:
            if ai_wins:
                return (None, infinity)
            elif human_wins:
                return (None, -infinity)
            else:  # Game is over, no more valid moves
                return (None, 0)
        else:  # Depth is zero
            x = evaluate_board(board, PLAYER_AI)
            return (None, x)

    if maximizingPlayer:
        value = -infinity
        column = random_choice(possible_moves)

        for col in possible_moves:
            b_copy = board.copy()
            drop_puck(b_copy, col, PLAYER_AI)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else:  # Minimizing player
        value = infinity
        column = random_choice(possible_moves)
        for col in possible_moves:
            b_copy = board.copy()
            drop_puck(b_copy,  col, PLAYER_HUMAN)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value


if __name__ == "__main__":
    # board = np.array([[0] * COLS] * ROWS)
    board = generate_board(COLS, ROWS)

    winner = None
    player = PLAYER_HUMAN

    while winner == None:
        display_board(board)

        possible_moves = get_possible_moves(board)

        if len(possible_moves) == 0:
            print("----Draw----")
            break

        print()
        if player == PLAYER_HUMAN:
            print("-----HUMAN   CHOOSE A COLUMN----")
        else:
            print("-----AI's   TURN ----")

        if player == PLAYER_HUMAN:
            column = select_move(possible_moves)

        else:
            DEPTH = 4
            t1 = time()
            column, value = minimax(
                board, DEPTH, -1000000000000, 1000000000000, True)
            t2 = time()
            print("decision made in {:.02f} seconds".format(t2-t1))

        drop_puck(board, column, player)

        if player == PLAYER_HUMAN:
            print(f"HUMAN has selected column ", column)
        else:
            print(f"AI has selected column ", column)

        if is_winning_move(board, player):
            if player == PLAYER_HUMAN:
                print(f"\n\n       HUMAN WINS!\n\n")
            else:
                print(f"\n\n       AI IS VICTORIOUS!\n\n")
            winner = player
            display_board(board)

        player = switch_player(player)

    print("--------------GAME OVER----------------")
