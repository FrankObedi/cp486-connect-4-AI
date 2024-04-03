from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import game
import time
import random

app = Flask(__name__)
socketio = SocketIO(app)


# Constants
PLAYER_AI = 1
PLAYER_HUMAN = 2
STR_PLAYER_AI = 'A'
STR_PLAYER_HUMAN = 'H'
ROWS = 6
COLS = 7


# Game state variables
board = None
player = None
winner = None
game_mode = 1


# helper functions
def str_p(player):
    if player == 1:
        return "A"
    return "H"


def check_move(board, move, player):
    winner = None
    board = game.drop_puck(board, move, player)

    if game.is_winning_move(board, player):
        print(f'Player {player} wins!!!')
        winner = player
    elif game.is_game_over(board):
        winner = "tie"
    player = game.switch_player(player)
    str_player = str_p(player)
    return player, str_player, winner, board


def init_game():
    # player1, player2 = "H", "A"
    player = PLAYER_HUMAN
    winner = None
    board = game.generate_board(COLS, ROWS)
    return board, player, winner


# Handle move made by the AI
def handle_ai_move():
    global board, player, winner
    moves_left = len(game.get_possible_moves(board))
    print("moves left:", moves_left)
    if winner == None and moves_left != 0:
        print("game level:", game_mode)
        DEPTH = game_mode
        move, value = game.minimax(
            board, DEPTH, -1000000000000, 1000000000000, True)

        # wait half a second before AI plays move
        time.sleep(0.5)
        player, str_player, winner, board = check_move(board, move, player)
        game.print_board(board)
        json_board = game.get_json_board(board)
        emit('game_state', {'board': json_board, 'winner': winner,
                            'next_player': str_player}, broadcast=True)


@app.route("/", methods=["POST", "GET"])
def home():
    return render_template("index.html")


@app.route("/game", methods=["POST", "GET"])
def game_page():  # Main game UI
    global board
    global player
    global winner
    global game_mode
    board, player, winner = init_game()

    game.display_board(board)
    if request.method == "POST":

        # Set game mode to option selected by users
        user_game_mode = request.form.get('game-mode')
        if user_game_mode is not None:
            game_mode = int(user_game_mode)
    return render_template("game.html", board=board)


@socketio.on('connect')
def handle_connect():  # WebSocket connection event
    emit('connected', {'message': "Connected successfully"})


@socketio.on('human_move')
def handle_human_move(move):  # Human player move event
    global board, player, winner
    possible_moves = game.get_possible_moves(board)
    moves_left = len(possible_moves)

    if winner == None and moves_left != 0:
        selection = int(move)
        move = game.select_move(possible_moves, selection)
        player, str_player, winner, board = check_move(board, move, player)
        game.print_board(board)
        json_board = game.get_json_board(board)
        emit('game_state', {'board': json_board, 'winner': winner,
                            'next_player': str_player}, broadcast=True)

        handle_ai_move()  # Make AI move after human player makes move


@socketio.on('disconnect')
def handle_disconnect():  # Handle server shutdown event
    print("Client disconnected")


if __name__ == '__main__':
    socketio.run(app, debug=True, host='localhost', port=5000)
