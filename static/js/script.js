document.addEventListener("DOMContentLoaded", function () {
  document.querySelector(".current-turn").innerHTML = "Red player's turn";
});

function play_move(event) {
  // Get the button element that was clicked
  const button = event.target;

  // Get the class list of the button
  const move = button.id.split("-")[2];

  // print id of button
  get_board(move);
}

// function to get get updated board and update the visual correspondingly
function get_board(selection) {
  fetch("/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ move: selection }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      const board = data.board;
      winner = data.winner;

      // show whose turn it is to play next
      let currPlayerElem = document.querySelector(".current-turn");
      nextPlayer = data.nextPlayer;
      if (nextPlayer == "R") {
        currPlayerElem.innerHTML = "Red player's turn";
      } else {
        currPlayerElem.innerHTML = "Yellow player's turn";
      }

      console.log("Next Player: " + nextPlayer);

      const slots = document.querySelectorAll(".column");

      if (winner != null) {
        let result = "Red";
        if (winner == "Y") {
          result = "Yellow";
        }
        document.querySelector(".winner").innerHTML = result + " wins!!";
        currPlayerElem.innerHTML = result + " wins!!";

        // disable all move buttons
        slots.forEach((slot) => {
          slot.disabled = true;
        });

        // show game over screen after 3seconds
        setTimeout(function () {
          document
            .querySelector(".game-over-container")
            .classList.remove("hidden");
        }, 2000);
      }

      // Update the UI to reflect current board
      for (let i = 0; i < board.length; i++) {
        for (let j = 0; j < board[i].length; j++) {
          const curr_player = board[i][j].player;
          if (curr_player === "R" || curr_player === "Y") {
            // Find the lowest available slot in the current column
            const slot = document.getElementById(`slot-${i}-${j}`);
            slot.classList.add(curr_player === "R" ? "player1" : "player2");

            // if the puck is placed at the very top the disable all the buttons
            // in this column to prevent player from using this move
            if (slot.id.includes("slot-0")) {
              let column = document.querySelectorAll(`.${slot.classList[1]}`);
              column.forEach((row) => {
                row.disabled = true;
              });
            }
          }
        }
      }
    })
    .catch((error) => {
      console.error("There was a problem with the fetch operation:", error);
    });
}

function restartGame() {
  window.location.reload();
}
