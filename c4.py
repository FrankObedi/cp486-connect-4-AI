from math import inf
import random

# CONSTANTS
ROWS, COLUMNS = 6, 7
player1, player2 = "H", "A"
window_len = 4


class square():
    '''
    Individual square class.
    Used to maintain player occupancy and square values.
    '''
    player = None
    value = 0  # default board values

    def __init__(self):
        pass

    def __str__(self):
        # return str(self.value)   # show default values
        if self.player != None:
            return str(self.player)
        else:
            return "-"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        # if we want to compare points
        if isinstance(other, square):
            return self.value == other.value
        # if we want to compare player
        else:
            return self.player == other

    def json_serializable(self):
        return {
            "player": self.player
        }


class Move():
    '''
    Available move class.
    Used as an iterable list of available moves along with each moves value.
    '''

    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.value = board[row][col].value

    def __str__(self):
        return (f'[Move | row: {self.row}  col: {self.col}  value: {self.value}]')

    def __repr__(self):
        return str(self)


def show_possible_moves(possible_moves):
    '''
    Prints the column of the possible moves
    '''
    s = "Possible moves: "
    for move in possible_moves:
        s += f' {move.col}'
    print(s)
    return


def select_move(possible_moves):
    '''
    Gives human player the option of selecting one of the available moves.
    Returns a Move
    Returns None if error occurs.
    '''
    show_possible_moves(possible_moves)
    selection = None
    while selection == None:
        try:
            selection = int(input("Select a column to place your puck: "))
            # look for selected move
            for move in possible_moves:
                if move.col == selection:
                    return move
            # move not found
            selection = None
            print("Error: invalid move")
        except:
            print("Error: invalid move")
    return None


def get_possible_moves(board_local):
    '''
    Iterates through the board to find columns that are still available.
    Returns: A list of Move objects that represent valid moves available.
    '''
    possible_moves = []
    cols_taken = []
    for r in range(len(board_local)-1, -1, -1):
        for c in range(len(board_local[0])):
            if board_local[r][c].player == None and c not in cols_taken:
                possible_moves.append(Move(r, c))
                cols_taken.append(c)
            if len(possible_moves) == 7 or (r == 0 and c == 6):
                possible_moves = sorted(
                    possible_moves, key=lambda move: move.col)
                return possible_moves
    return possible_moves


def drop_puck(board_local, move, player):
    '''
    Sets the chosen square to the players puck.
    Had an issue where it places it above empty square due to minimax. This ensure it "drops"
    '''
    r = move.row
    while r <= 4 and board_local[r+1][move.col] == None:
        r += 1
    board_local[r][move.col].player = player
    # print(f"Player {player} dropped puck in column {move.col}")
    return


def is_winning_move(board_local, player, move, from_minimax):
    '''
    Returns True if this move would result in winnning the game.
    False otherwise.
    '''
    count = 0  # number of occupied squares by player in a succession
    total_count = 0  # number of occupied squares irrespective of player

    # temporarily drop the puck
    if not from_minimax:
        board_local[move.row][move.col].player = player

    # Check vertically
    for c in range(len(board_local[0])):
        for r in range(len(board_local)-1, -1, -1):

            # no point in counting the rest
            if (r < 3 and count == 0):
                break

            # this player has the square, increase counter
            if (board_local[r][c].player == player):
                count += 1
                if count == 4:
                    return True
            # If empty square move to next column. nothing on top
            elif (board_local[r][c].player == None):
                break
            # not this player, reset counter
            else:
                count = 0
        count = 0

    # Check horizontally
    break_flag = False
    for r in range(len(board_local)-1, -1, -1):
        for c in range(len(board_local[0])):

            # no point in checking the rest. cant make 4 on this row
            if (c > len(board_local[0]) - 3 and count == 0 and total_count == 0):
                break

            # count occupied square
            if (board_local[r][c].player != None):
                total_count += 1

            # this player has the square, increase counter
            if (board_local[r][c].player == player):
                count += 1
                if count == 4:
                    return True
            # not this player or square is empty, reset counter
            else:
                count = 0

            # if a row is scanned and only counted <= 3 occupied squares
            # cancel searching the board. cannot make 4 above this row
            if (c == len(board_local[0])-1 and total_count <= 3):
                break_flag = True
                break

        if break_flag:  # cancel searching the board
            break
        count = 0
        total_count = 0

    # lazy check
    # Check diagonal (negative slope)
    for r in range(len(board_local)-4, -1, -1):
        for c in range(len(board_local[0])):
            try:
                if (board_local[r][c].player == player and
                    board_local[r+1][c+1].player == player and
                    board_local[r+2][c+2].player == player and
                        board_local[r+3][c+3].player == player):
                    return True
            except:
                pass

    # Check diagonal (positive slope)
    for r in range(3, len(board_local)):
        for c in range(len(board_local[0])):
            try:
                if (board_local[r][c].player == player and
                    board_local[r-1][c+1].player == player and
                    board_local[r-2][c+2].player == player and
                        board_local[r-3][c+3].player == player):
                    return True
            except:
                pass

    # return the sqaure back to normal
    if not from_minimax:
        board_local[move.row][move.col].player = None
    return False


def calc_move_score(board, move, player):
    '''
    Calculate the value of making this move.
    This is done for each possible move.
    Move is made temporarily and the value is calculated.
    '''
    print("CURRENT PLAYER:", player)
    bonus = 0
    board[move.row][move.col].player = player.lower()  # for visualization
    # print ("------calc move begin---------")
    # print(f"this player is {player}")
    # print (move)
    # print()
    # display_board()

    # temporarily drop the puck
    board[move.row][move.col].player = player
    # get default value
    value = board[move.row][move.col].value

    '''Check vertically'''
    # create a list of the column
    player_count = 0
    opponent_count = 0
    column = [board[r][move.col] for r in range(len(board))]

    # count opponent pieces in row
    skip = 1  # skip this players temporary placed piece
    for sq in column:
        if sq.player == player and skip == 1:
            skip -= 1
            continue
        elif sq.player == switch_player(player):
            opponent_count += 1
        elif sq.player == player:
            break

    # count player pieces in row
    for sq in column:
        if sq.player == player:
            player_count += 1
        elif sq.player == switch_player(player):
            break

    if opponent_count == 3 and player_count == 1:  # favour preventing opponent win over getting 3 in a row
        value = max(value, 110)
    elif opponent_count == 2:  # favour blocking a 2 over something else
        bonus = 2

    if player_count == 4:  # you win
        value = inf
    elif player_count == 3 and move.row > 0:  # 3 in a row and atleast one space left
        value = max(value, 100)
    elif player_count == 3 and move.row == 0:  # less points since you can no longer make 4
        value = max(value, 50)
    elif player_count == 2:  # 2 in a row
        value = max(value, 10)
    elif player_count == 1:  # one
        value = max(value, 0)

    '''Check horizontally'''
    player_count = 0
    row = board[move.row]

    for c in range(move.col - window_len+1, len(board[0])-3):
        if c < 0:  # dont start index from negative
            continue
        if c > move.col:  # if we pass our move col, stop
            break
        window = row[c:c + window_len]  # our possible windows

        # count number of different squares
        player_count = window.count(player)
        empty_count = window.count(None)
        opponent_count = window.count(switch_player(player))

        if player_count == 4:  # you win
            value = inf
        elif opponent_count == 3:  # if opponent has 3 in this window, critical to make this move
            value = max(value, 110)
        elif player_count == 3 and empty_count == 1:  # 3 in a row with one still left
            value = max(value, 100)
        elif player_count == 2 and empty_count == 2:  # 2 in a row with two still left
            value = max(value, 10)
        elif player_count == 1:  # either leave this 0 or low number
            value = max(value, 0)
        # print (c, window, value)

    '''Check diagonally - positive slope'''
    # find the start of the diagonal
    r, c = move.row, move.col
    while r < 5 and c > 0:
        c -= 1
        r += 1

    # check each window of 4
    temp_r = r
    temp_c = c
    while r > 2 and c < 4:  # cant make four otherwise
        window = []
        while r >= 0 and c <= 6 and len(window) < 4:  # build the window
            window.append(board[r][c])
            c += 1
            r -= 1

        # evaluate the window
        player_count = window.count(player)
        empty_count = window.count(None)
        opponent_count = window.count(switch_player(player))

        if player_count == 4:  # you win
            value = inf
        elif opponent_count == 3:  # if opponent has 3 in this window, critical to make this move
            value = max(value, 110)
        elif player_count == 3 and empty_count == 1:  # 3 in a row with one still left
            value = max(value, 100)
        elif player_count == 2 and empty_count == 2:  # 2 in a row with two still left
            value = max(value, 10)
        elif player_count == 1:  # either leave this 0 or low number
            value = max(value, 0)
        # print (window, value)

        # move to the next window
        temp_r -= 1
        temp_c += 1
        r = temp_r
        c = temp_c

    '''Check diagonally - negative slope'''
    # find the start of the diagonal
    r, c = move.row, move.col
    while r > 0 and c > 0:
        c -= 1
        r -= 1
    # check each window of 4
    temp_r = r
    temp_c = c
    while r < 3 and c < 4:  # cant make four otherwise
        window = []
        while r <= 5 and c <= 6 and len(window) < 4:  # build the window
            window.append(board[r][c])
            c += 1
            r += 1

        # evaluate the window
        player_count = window.count(player)
        empty_count = window.count(None)
        opponent_count = window.count(switch_player(player))

        if player_count == 4:  # you win
            value = inf
        elif opponent_count == 3:  # if opponent has 3 in this window, critical to make this move
            value = max(value, 110)
        elif player_count == 3 and empty_count == 1:  # 3 in a row with one still left
            value = max(value, 100)
        elif player_count == 2 and empty_count == 2:  # 2 in a row with two still left
            value = max(value, 10)
        elif player_count == 1:  # either leave this 0 or low number
            value = max(value, 0)

        # move to the next window
        temp_r += 1
        temp_c += 1
        r = temp_r
        c = temp_c

    '''
    Special cases
    wont need this with minimax
    '''
    # Case 1
    # break up patterns such as | - | R | - | R | - |
    # if  | - | R | R | R | - |  happens then Y losses
    # or  | - | R | R | - | - | or | - | - | R | R | - |
    # reason to take middle rows first.
    for i in range(len(row)-4):
        if row[i].player == None \
                and row[i+1].player == switch_player(player) \
                and row[i+2].player == player \
                and row[i+3].player == switch_player(player) \
                and row[i+4].player == None:
            value = max(value, 60)
        elif row[i].player == player \
                and row[i+1].player == switch_player(player) \
                and row[i+2].player == None \
                and row[i+3].player == switch_player(player) \
                and row[i+4].player == None:
            value = max(value, 60)
        elif row[i].player == None \
                and row[i+1].player == switch_player(player) \
                and row[i+2].player == None \
                and row[i+3].player == switch_player(player) \
                and row[i+4].player == player:
            value = max(value, 60)
        # these are not exactly correct
        # need to take the spot next to opponent
        elif row[i].player == None \
                and row[i+1].player == None \
                and row[i+2].player == switch_player(player) \
                and row[i+3].player == switch_player(player) \
                and row[i+4].player == None:
            value = max(value, 60)
        elif row[i].player == None \
                and row[i+1].player == switch_player(player) \
                and row[i+2].player == switch_player(player) \
                and row[i+3].player == None \
                and row[i+4].player == None:
            value = max(value, 60)

    board[move.row][move.col].player = None
    # print ("------calc move end---------")

    return value + board[move.row][move.col].value + bonus


'''
function minimax(node, depth, maximizingPlayer) is
    if depth = 0 or node is a terminal node then
        return the heuristic value of node
    if maximizingPlayer then
        value := −∞
        for each child of node do
            value := max(value, minimax(child, depth − 1, FALSE))
        return value
    else (* minimizing player *)
        value := +∞
        for each child of node do
            value := min(value, minimax(child, depth − 1, TRUE))
        return value
'''


def minimax(board_local, move, depth, player):
    print(f"---entering minimax-  depth: {depth}   player {player}")
    print(move)
    # display_board(board_local)
    if move != None:
        p1_wins = is_winning_move(board_local, player1, move, True)
        p2_wins = is_winning_move(board_local, player2, move, True)
    else:
        p1_wins = False
        p2_wins = False

    best_move = possible_moves[0]  # random selection

    # BC
    if depth == 0 or is_terminal:
        if is_terminal:
            # move.value = 0
            # return 0
            if p1_wins:
                move.value = 999
                return move
            elif p2_wins:
                move.value = -999
                return move
            else:
                move.value = 0
                return move
        else:
            if maxing:
                move.value = calc_move_score(board_local, move, player1)
            else:
                move.value = calc_move_score(board_local, move, player2)
            return move

    if player:
        best_move.value = -inf
        for move2 in possible_moves:

            board_copy = board_local.copy()
            drop_puck(board_copy, move2, player)
            # board_copy[move2.row][move2.col].player = player
            display_board(board_copy)
            new_move = minimax(board_copy, move2, depth -
                               1, switch_player(player))

            # reset the temporary placement
            board_copy[next_move.row][next_move.col].player = None

            if new_move.value > best_move.value:
                best_move = new_move
            # alpha = max(alpha, value)
                # if alpha >= beta:
                # 	break
    else:
        pass

    print("best move from minimax ", best_move)
    return best_move


def generate_board():
    '''
    Generates an empty board. 
    Returns: A 2D list of squares.
    [[square,square,...],[square,square,...], ...]
    '''
    board = [[square() for _ in range(COLUMNS)] for _ in range(ROWS)]

    # default values to favour middle column.
    # bias = 0
    # for c in range(COLUMNS):
    #     if c < 3:
    #         bias += 1
    #     elif c == 3:
    #         bias = 5
    #     elif c == 4:
    #         bias = 2
    #     else:
    #         bias -= 1
    #     for r in range(ROWS):
    #         if r > 1 and c == 3:
    #             bias = 8
    #         board[r][c].value = bias + r
    # return board

    bias = 0
    for col in range(COLUMNS):
        if col < 3:
            bias += 1
        elif col == 3:
            bias = 7
        elif col == 4:
            bias = 3
        else:
            bias -= 1
        for r in range(ROWS):
            if r > 1 and col == 3:
                bias = 8
            board[r][col].value = bias + r

    return board


def display_board(board_local):
    '''
    Display the current state of the board.
    '''
    r = 0
    for row in board_local:
        row_string = f'{r} |'
        r += 1
        for sq in row:
            row_string += f' {sq} |'
        print(row_string)
    print('    0   1   2   3   4   5   6')
    return


def switch_player(player):
    '''
    Return the opposite player.
    '''
    if player == player1:
        return player2
    else:
        return player1


if __name__ == "__main__":

    board = generate_board()

    display_board(board)

    winner = None
    player = player1

    while winner == None:
        display_board(board)
        possible_moves = get_possible_moves(board)

        if len(possible_moves) == 0:
            print("----Draw----")
            break
        print()
        if player == player1:
            print("-----HUMAN   CHOOSE A COLUMN----")
        else:
            print("-----AI    CHOOSE A COLUMN----")

        if player == player1:
            for move in possible_moves:
                move.value = -calc_move_score(board, move, player)
            for move in possible_moves:
                print(move)
            move = select_move(possible_moves)

        else:
            # for move in possible_moves:
            #     move.value = calc_move_score(board, move, player)
            # for move in possible_moves:
            #     print (move)
            # move = select_move(possible_moves)
            maximizing = False
            move = minimax(board, None,  2, -inf, inf, True)

            print("Yellow selected ", move)

        if is_winning_move(board, player, move, False):
            print(f'Player {player} wins!!!')
            winner = player
            board[move.row][move.col].player = player
            display_board(board)
        else:
            print(f"{player} dropping puck on real board at {move}")
            # drop_puck(board, move, player)
            drop_puck(board, move, player)

        player = switch_player(player)
