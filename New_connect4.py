import numpy as np
from math import inf as infinity
from random import choice as random_choice
from time import time
'''
 [[[default_value, player]]]

'''
PLAYER_AI = 1
PLAYER_HUMAN = 2
STR_PLAYER_AI = 'A'
STR_PLAYER_HUMAN = 'H'
ROWS = 6
COLS = 7
WINDOW_SIZE = 4
DEPTH = 4

'''
NxN board seems to be working decently.
to make connect N  scoring needs to be changed and is winning needs to be changed.
'''


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
        print (row_string)
    col_string = "    "
    for c in range(COLS):
        col_string += f" {c}  "
    print (col_string)
    return

def get_possible_moves(board):
    '''
    Returns a list of columns that are still available.
    '''
    available_cols = []
    for c in range(COLS):
        if board[0][c] == 0:
            available_cols.append(c)
    return available_cols

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
    # print(f"Player {player} dropped puck in column {col}")
    return

def switch_player(player):
    '''
    Return the opposite player.
    '''
    if player == PLAYER_AI:
        return PLAYER_HUMAN
    else:
        return PLAYER_AI

# def is_winning_move(board, piece):
#     '''
#     code taken from https://github.com/KeithGalli/Connect4-Python/blob/master/connect4_with_ai.py#L67
#     '''
#     # Check horizontal locations for win
#     for c in range(COLS-3):
#         for r in range(ROWS):
#             if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
#                 return True

#     # Check vertical locations for win
#     for c in range(COLS):
#         for r in range(ROWS-3):
#             if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
#                 return True

#     # Check positively sloped diaganols
#     for c in range(COLS-3):
#         for r in range(ROWS-3):
#             if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
#                 return True

#     # Check negatively sloped diaganols
#     for c in range(COLS-3):
#         for r in range(3, ROWS):
#             if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
#                 return True
               
def is_winning_move(board, player):
    '''
    Returns True if this move would result in winnning the game.
    False otherwise.
    '''
    ### Could avoid doing multiple passes but not a big deal for now

    # Check vertically
    for c in range(COLS):
        count = 0 # number of occupied squares by player in a succession
        for r in range(ROWS):

            # no point in counting the rest
            if (r > ROWS-WINDOW_SIZE and count == 0):
                break

            # this player has the square, increase counter
            if (board[r][c] == player):
                count += 1
                if count == 4:
                    return True
            # opponent found
            elif (board[r][c] == switch_player(player)):
                break

    # Check horizontally
    break_flag = False
    for r in range(ROWS-1,-1,-1 ):
        count = 0 # number of occupied squares by player in a succession
        occupied_count = 0 # number of occupied squares irrespective of player 
        for c in range(COLS):
            # no point in checking the rest. cant make 4 on this row
            if (c > COLS - WINDOW_SIZE and count == 0 and occupied_count == 0):
                break

            # count occupied square
            if (board[r][c] != 0 ):
                occupied_count += 1

            # this player has the square, increase counter
            if (board[r][c] == player ):
                count += 1
                if count == 4:
                    return True
            # not this player or square is empty, reset counter
            else:
                count = 0

            # if a row is scanned and only counted <= 3 occupied squares
            # cancel searching the board. cannot make 4 above this row
            if (c == COLS-1 and occupied_count <= 3):
                break_flag = True
                break
        
        if break_flag: # cancel searching the board
            break

    # lazy check
    # Check diagonal (negative slope)
    # could be improved
    for r in range(ROWS- (WINDOW_SIZE-1)):
        for c in range(COLS- (WINDOW_SIZE-1)):
            try:
                if (board[r][c] == player and 
                    board[r+1][c+1] == player and
                    board[r+2][c+2] == player and 
                    board[r+3][c+3] == player):
                    return True
            except:
                pass        
    # Check diagonal (positive slope)
    for r in range(WINDOW_SIZE-1, ROWS):
        for c in range(COLS - (WINDOW_SIZE-1)):
            try:
                if (board[r][c] == player and 
                    board[r-1][c+1] == player and
                    board[r-2][c+2] == player and 
                    board[r-3][c+3] == player):
                    return True
            except:
                pass
    return False

def evaluate_window(window, player):
    '''
    Evaluates a single window.
    code taken from https://github.com/KeithGalli/Connect4-Python/blob/master/connect4_with_ai.py#L67
    '''
    score = 0
    opponent = switch_player(player)
    if window.count(player) == 4:
        score += 100
    elif window.count(player) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(player) == 2 and window.count(0) == 2:
        score += 2

    if window.count(opponent) == 3 and window.count(0) == 1:
        score -= 4
    return score

def evaluate_board(board, player):
    '''
    Evaluates the board state and returns a score in terms of the provided player.
    code taken from https://github.com/KeithGalli/Connect4-Python/blob/master/connect4_with_ai.py#L67
    '''
    value = 0
    window_size_minus1 = WINDOW_SIZE-1

    '''
    add extra values to having center control here.
    only important for the first couple of moves.
    algorithm takes over from there.
    '''

    # Vertical
    for c in range(COLS):
        column = [board[row][c] for row in range(ROWS)]
        for r in range(ROWS-(WINDOW_SIZE-1)):
            window = column[r:r + WINDOW_SIZE]
            value += evaluate_window(window, player)

    # Horizontal
    for r in range(ROWS):
        row = [board[r][col] for col in range(COLS)]
        for c in range(COLS-window_size_minus1):
            window = row[c:c + WINDOW_SIZE]
            value += evaluate_window(window, player)

    # Diagonal Negative Slope
    for r in range(ROWS-window_size_minus1):
        for c in range(COLS-window_size_minus1):
            window = [board[r+i][c+i] for i in range(WINDOW_SIZE)]
            value += evaluate_window(window, player)


    # Diagonal Positive Slope
    for r in range(ROWS-window_size_minus1):
        for c in range(COLS-window_size_minus1):
            window = [board[r-i+window_size_minus1][c+i] for i in range(WINDOW_SIZE)]
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
    is_terminal = len(possible_moves) == 0  or ai_wins or human_wins

    if depth == 0 or is_terminal:
        if is_terminal:
            if ai_wins:
                # print("AI WINS", depth)
                # display_board(board)
                # print("------------------")
                return (None, 100000000000000)
            elif human_wins:
                # print("HUMAN WINS", depth)
                # display_board(board)
                # print("------------------")
                return (None, -10000000000000)
            else: # Game is over, no more valid moves
                return (None, 0)
        else: # Depth is zero
            x = evaluate_board(board, PLAYER_AI)
            return (None, x)
        
    if maximizingPlayer:
        value = -infinity
        column = random_choice(possible_moves)
        for col in possible_moves:

            b_copy = board.copy()
            drop_puck(b_copy, col, PLAYER_AI)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            # print(f"depth: {depth} max: {maximizingPlayer}, col: {col}   new_score:  {new_score}")
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        # print(f"\nreturning MAXX.  column: {column}   value:  {value}\n")
        

        return column, value
    
    else: # Minimizing player
        value = infinity
        column = random_choice(possible_moves)
        for col in possible_moves:
            b_copy = board.copy()
            drop_puck(b_copy,  col, PLAYER_HUMAN)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            # print(f"depth: {depth} max: {maximizingPlayer}, col: {col}   new_score:  {new_score}")
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        
        # print(f"\nreturning MIN.  column: {column}   value:  {value}\n")
        
        return column, value

def select_move(possible_moves):
    '''
    Gives human player the option of selecting one of the available moves.
    Returns a Move
    Returns None if error occurs.
    '''
    selection = None
    while selection == None:
        try:
            selection = int(input("Select a column to place your puck: "))
            if selection in possible_moves:
                    return selection
            # move not found
            selection = None
            print ("Error: invalid move")
        except:
            print ("Error: invalid move")
    return None


if __name__ == "__main__":
    board = np.array([[0] * COLS] * ROWS)

    winner = None
    player = PLAYER_HUMAN

    count = 0
    timer_sum = 0
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
            # t1 = time()
            # column,value = minimax(board, DEPTH, -infinity, infinity, True)
            # t2 = time()
            # timer_sum += t2-t1
            # count += 1
            # print("decision made in {:.02f} seconds".format(t2-t1))   

        else:
            t1 = time()
            column,value = minimax(board, DEPTH, -infinity, infinity, True)
            t2 = time()
            timer_sum += t2-t1
            count += 1
            print("decision made in {:.02f} seconds".format(t2-t1))

        drop_puck(board,column,player)

        if player == PLAYER_HUMAN:
            print (f"HUMAN has selected column ", column)
        else:
            print (f"AI has selected column ", column)
        


        if is_winning_move(board, player):
            if player == PLAYER_HUMAN:
                print (f"\n\n       HUMAN WINS!\n\n")
            else:
                print (f"\n\n       AI IS VICTORIOUS!\n\n")
            winner = player
            display_board(board)
                  

        
        player = switch_player(player)
    
    print("--------------GAME OVER----------------")
    print("average decision time: ", timer_sum/count)



