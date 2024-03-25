

class square():
    '''
    Individual square class.
    Used to maintain player occupancy and square values.
    '''
    player = None
    red_value = 0 # TBD
    yellow_value = 0 # TBD

    def __init__(self):
        pass

    def __str__(self):
        if self.player != None:
            return str(self.player)
        else:
            return "-"
        
    def __repr__(self):
        return str(self)
    
class Move():
    '''
    Available move class.
    Used as an iterable list of available moves along with each moves value.
    '''
    def __init__(self, row, col, player_score=None, opponent_score=None):
        self.row = row
        self.col = col
        self.player_score = player_score  # player1
        self.opponent_score = opponent_score  # player2

    def __str__(self):
        # only show row/col
        return (f'[Move | row: {self.row}  col: {self.col}]')
        # also show score
        # return (f'[Move | row: {self.row}  col: {self.col}'
        #         f' | P_s: {self.player_score}'
        #         f' | O_s: {self.opponent_score}]')
    def __repr__(self):
        return str(self)
    
def show_possible_moves(possible_moves):
    '''
    Prints the column of the possible moves
    '''
    s = "Possible moves: "
    for move in possible_moves:
        s += f' {move.col}'
    print (s)
    return

def select_move(possible_moves):
    '''
    Gives human player the option of selecting one of the available moves.
    Returns a Move

    returns None if error occurs.
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
            print ("Error: invalid move")
        except:
            print ("Error: invalid move")
    return None

def get_possible_moves():
    '''
    Iterates through the board to find columns that are still available.
    Returns: A list of Move objects that represent valid moves available.
    '''
    possible_moves = []
    cols_taken = []
    for r in range(len(board)-1,-1,-1):
        for c in range(len(board[0])):            
            if board[r][c].player == None and c not in cols_taken:
                possible_moves.append(Move(r,c))
                cols_taken.append(c)
            if len(possible_moves) == 7 or (r == 0 and c == 6):
                possible_moves = sorted(possible_moves, key=lambda move: move.col)
                return possible_moves
    return "FIX ME - get_possible_moves"  # should not get here

def drop_puck(move,player):
    '''
    Sets the chosen square to the players puck.
    '''

    if board[move.row][move.col].player == None:
        board[move.row][move.col].player = player
        print(f"Player {player} dropped puck in col {move.col}")
        return
    print(f"Error - drop_puck: Cannot drop puck in column {move.col}")
    return

def is_winning_move(player, move):
    '''
    Returns True if this move would result in winnning the game.
    False otherwise.
    '''
    count = 0 # number of occupied squares by player in a succession
    total_count = 0 # number of occupied squares irrespective of player 
    iteration_count = 0
    # temporarily drop the puck
    board[move.row][move.col].player = player
    # print("testing move")
    # display_board()
    ### Could avoid doing multiple passes but not a big deal for now

    # Check vertically
    for c in range(len(board[0])):
        for r in range(len(board)-1,-1,-1):
            # print(r,c, board[r][c].player, player)
            # no point in counting the rest
            if (r < 3 and count == 0):
                break
            # this player has the square, increase counter
            if (board[r][c].player == player ):
                count += 1
                if count == 4:
                    return True
            # If empty square move to next column. nothing on top
            elif (board[r][c].player == None ):
                break
            # not this player, reset counter
            else:
                count = 0
        # reset counter for next column
        count = 0

    # Check horizontally
    break_flag = False
    for r in range(len(board)-1,-1,-1):
        for c in range(len(board[0])):
            # iteration_count+=1     
            # print("i: {:>2} count: {}   total count: {}   row: {} col: {}  board: {}  player: {}".format(
            #     iteration_count,count,total_count, r,c, board[r][c].player, player))
            # no point in checking the rest
            # cant make 4 on this row
            if (c > len(board[0]) - 3 and count == 0 and total_count == 0):
                # print("first break")
                break
            # count occupied square
            if (board[r][c].player != None ):
                total_count += 1
            # this player has the square, increase counter
            if (board[r][c].player == player ):
                count += 1
                if count == 4:
                    return True
            # not this player or square is empty, reset counter
            else:
                count = 0
            # if a row is scanned and only counted <= 3 occupied squares
            # cancel searching the board. cannot make 4 above this row
            if (c == len(board[0])-1 and total_count <= 3):
                # print("second break")
                break_flag = True
                break
        # cancel searching the board
        if break_flag:
            break
        # reset counter for next row
        count = 0
        total_count = 0
        # print()


    # lazy check
    # Check diagonal (negative slope)
    for r in range(len(board)-4, -1, -1):
        for c in range(len(board[0])):
            iteration_count+=1     
            # print("i: {:>2} count: {}   total count: {}   row: {} col: {}  board: {}  player: {}".format(
            #     iteration_count,count,total_count, r,c, board[r][c].player, player))
            try:
                if (board[r][c].player == player and 
                    board[r+1][c+1].player == player and
                    board[r+2][c+2].player == player and 
                    board[r+3][c+3].player == player):
                    return True
            except:
                pass
        # print()
            
    # Check diagonal (positive slope)
    for r in range(3, len(board)):
        for c in range(len(board[0])):
            iteration_count+=1     
            # print("i: {:>2} count: {}   total count: {}   row: {} col: {}  board: {}  player: {}".format(
            #     iteration_count,count,total_count, r,c, board[r][c].player, player))
            try:
                if (board[r][c].player == player and 
                    board[r-1][c+1].player == player and
                    board[r-2][c+2].player == player and 
                    board[r-3][c+3].player == player):
                    return True
            except:
                pass
        # print()
            
    # return the sqaure back to normal
    board[move.row][move.col].player = None
    return False
    
    

def generate_board():
    '''
    Generates an empty board. 
    Returns: A 2D list of squares.
    [[square,square,...],[square,square,...], ...]
    '''
    return [[square() for _ in range(7)] for _ in range(6)]


def display_board():
    '''
    Display the current state of the board.
    '''
    r = 0
    for row in board:
        row_string = f'{r} |'
        r += 1
        for sq in row:
            row_string += f' {sq} |'
        print (row_string)
    # print(f'   {'-'*27}')
    # print('    A   B   C   D   E   F   G')
    print('    0   1   2   3   4   5   6')
    return

def switch_player(player):
    if player == player1:
        return player2
    else:
        return player1

if __name__ == "__main__":
    board = generate_board()
    player1, player2 = "R", "Y"
    print ("Player 1 - Red")
    print ("Player 2 - Yellow")
    
    winner = None
    player = player1
    while winner == None:
        display_board()
        possible_moves = get_possible_moves()
        print()
        print(f"--{player}--")
        move = select_move(possible_moves)
        
        if is_winning_move(player, move):
            print (f'Player {player} wins!!!')
            winner = player
            board[move.row][move.col].player = player
            display_board()
        else:
            drop_puck(move, player)

        player = switch_player(player)

    # display_board()
    # possible_moves = get_possible_moves()
    # drop_puck(select_move(possible_moves), player2)



    # possible_moves = get_possible_moves()
    # show_possible_moves(possible_moves)
    # drop_puck(possible_moves[2], player1)

    # for i in range(5):
    #     possible_moves = get_possible_moves()
    #     show_possible_moves(possible_moves)
    #     drop_puck(possible_moves[i], player1)



    # possible_moves = get_possible_moves()
    # show_possible_moves(possible_moves)
    # drop_puck(possible_moves[3], player1)





    # display_board()

    
    # possible_moves = get_possible_moves()
    # move = possible_moves[1]
    # player = player2
    # print ( f"is {move} a winning move for player {player}? {is_winning_move(player, move)}")
    