from flask import Flask, redirect, request, render_template, jsonify
import game

app = Flask(__name__)


def start_game():
    # Initialize the board
    board = game.generate_board()

    player1, player2 = "R", "Y"
    winner = None
    print("Player 1 - Red")
    print("Player 2 - Yellow")
    return board, player1, player2, winner


board = None
player = None
winner = None


@app.route("/", methods=["POST", "GET"])  # home page
def home():
    global board
    global player
    global winner

    if request.method == "GET":
        board, player1, player2, winner = start_game()
        player = player1

    if (winner == None) and (request.method == "POST"):

        # get json from request
        # This is the column player chose to play in
        data = request.json
        selection = int(data.get('move'))

        possible_moves = game.get_possible_moves(board)
        move = game.select_move(possible_moves, board, selection)

        if game.is_winning_move(player, move, board):
            print(f'Player {player} wins!!!')
            winner = player
            board[move.row][move.col].player = player
        else:
            if game.drop_puck(move, player, board):
                player = game.switch_player(player)

        json_board = [[square.json_serializable() for square in row]
                      for row in board]
        game.display_board(board)
        return jsonify({"board": json_board, "winner": winner, "nextPlayer": str(player)})
    return render_template("index.html", board=board)


if __name__ == "__main__":
    app.run(debug=True)
