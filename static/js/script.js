function restartGame() {
  window.location.reload();
}

// Create a Socket.IO instance and connect to the server
const socket = io();

// Handle 'connect' event
socket.on("connect", () => {
  "http://" + document.domain + ":" + location.port;
});

function play_move(event) {
  // Get the button element that was clicked
  const button = event.target;

  // Extract the move index from the button's ID
  const move = button.id.split("-")[2];

  const slots = document.querySelectorAll(".column");
  // disable all move buttons
  slots.forEach((slot) => {
    slot.disabled = true;
  });

  // Emit 'human_move' event with the selected move index
  socket.emit("human_move", parseInt(move)); // Ensure move is sent as an integer
}

socket.on("game_state", function (data) {
  // Human Player Icon
  const humanPlayer = document.querySelector(".human-player");

  // Bot Player Icon
  const botPlayer = document.querySelector(".bot-player");
  // Update UI based on the received game state
  console.log("Received game state:", data);
  const board = JSON.parse(data.board);
  winner = data.winner;
  nextPlayer = data.next_player;

  setTimeout(function () {
    const slots = document.querySelectorAll(".column");
    // disable all move buttons
    slots.forEach((slot) => {
      if (slot.classList.contains("full-column") == false) {
        slot.disabled = false;
      }
    });
  }, 1000);

  // Update player turn text
  let currPlayerElem = document.querySelector(".current-turn");
  if (nextPlayer == "H") {
    currPlayerElem.innerHTML = "Human's turn";
    botPlayer.classList.add("not-playing");
    humanPlayer.classList.remove("not-playing");
  } else {
    currPlayerElem.innerHTML = "AI's turn";
    humanPlayer.classList.add("not-playing");
    botPlayer.classList.remove("not-playing");
  }

  for (let i = 0; i < board.length; i++) {
    for (let j = 0; j < board[i].length; j++) {
      const token_type = board[i][j];
      console.log("token_type: " + token_type);
      if (token_type === 1 || token_type === 2) {
        // Find the lowest available slot in the current column
        const slot = document.getElementById(`slot-${i}-${j}`);
        slot.classList.add(token_type === 2 ? "player1" : "player2");

        // if the puck is placed at the very top the disable all the buttons
        // in this column to prevent player from using this move
        if (slot.id.includes("slot-0")) {
          let column = document.querySelectorAll(`.${slot.classList[1]}`);
          column.forEach((row) => {
            row.disabled = true;
            row.classList.add("full-column");
          });
        }
      }
    }
  }

  if (winner != null) {
    // console.log("Winner is: " + winner);

    if (winner == "tie") {
      document.querySelector(".winner").innerHTML = "TIE GAME!";
      let currPlayerElem = document.querySelector(".current-turn");
      currPlayerElem.style.color = "red";
      currPlayerElem.innerHTML = "TIE GAME!";
    } else {
      let result = "Human";
      if (winner == 1) {
        result = "AI";
      }
      document.querySelector(".winner").innerHTML = result + " WINS!";
      let currPlayerElem = document.querySelector(".current-turn");
      currPlayerElem.style.color = "red";
      currPlayerElem.innerHTML = result + " WINS!";
    }

    const slots = document.querySelectorAll(".column");
    // disable all move buttons
    slots.forEach((slot) => {
      slot.disabled = true;
    });

    // show game over screen after 3seconds
    setTimeout(function () {
      document.querySelector(".game-over-container").classList.remove("hidden");
    }, 2000);
  }
});

// Handle 'disconnect' event (optional)
socket.on("disconnect", () => {
  console.log("Disconnected from server");
  socket.close();
});
