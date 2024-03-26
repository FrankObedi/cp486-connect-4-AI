from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import game
import time

app = Flask(__name__)
socketio = SocketIO(app)

# Game state variables
board = None
player = None
winner = None

# Initialize the game


def check_move(board, player, move):
    winner = None
    if game.is_winning_move(board, player, move, False):
        print(f'Player {player} wins!!!')
        winner = player
        board[move.row][move.col].player = player
    else:
        # print(f"{player} dropping puck on real board at {move}")
        game.drop_puck(board, move, player)
        player = game.switch_player(player)
    return player, winner


def init_game():
    player1, player2 = "H", "A"
    player = player1
    winner = None
    board = game.generate_board()
    return board, player1, player2, player, winner


# Handle move made by the AI
def handle_ai_move():
    global board, player, winner
    if winner == None:
        move = game.minimax(board, None, 3, player)
        time.sleep(0.5)
        player, winner = check_move(board, player, move)
        json_board = [[square.json_serializable() for square in row]
                      for row in board]
        emit('game_state', {'board': json_board, 'winner': winner,
                            'next_player': player}, broadcast=True)


@app.route("/")
def home():  # Main game UI
    global board
    global player1
    global player2
    global player
    global winner
    board, player1, player2, player, winner = init_game()
    return render_template("game.html", board=board)


@socketio.on('connect')
def handle_connect():  # WebSocket connection event
    emit('connected', {'message': "Connected successfully"})


@socketio.on('human_move')
def handle_human_move(move):  # Human player move event
    global board, player, winner
    if winner == None:
        selection = int(move)
        possible_moves = game.get_possible_moves(board)
        for move in possible_moves:
            move.value = game.calc_move_score(board, move, player)
        move = game.select_move(possible_moves, selection)
        player, winner = check_move(board, player, move)
        json_board = [[square.json_serializable() for square in row]
                      for row in board]
        emit('game_state', {'board': json_board, 'winner': winner,
                            'next_player': player}, broadcast=True)

        handle_ai_move()  # Make AI move after human player makes move


@socketio.on('disconnect')
def handle_disconnect():  # Handle server shutdown event
    print("Client disconnected")
    socketio.close()  # Close WebSocket connection


if __name__ == '__main__':
    socketio.run(app)
