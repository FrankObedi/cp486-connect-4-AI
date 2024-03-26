// // document.addEventListener("DOMContentLoaded", function () {
// //   document.querySelector(".current-turn").innerHTML = "Human player's Star";
// // });

// function play_move(event) {
//   // Get the button element that was clicked
//   const button = event.target;

//   // Get the class list of the button
//   const move = button.id.split("-")[2];
//   console.log("Move: " + move);

//   // print id of button
//   get_board(move);
// }

// // function to get get updated board and update the visual correspondingly
// function get_board(selection) {
//   fetch("/", {
//     method: "POST",
//     headers: {
//       "Content-Type": "application/json",
//     },
//     body: JSON.stringify({ move: selection }),
//   })
//     .then((response) => {
//       if (!response.ok) {
//         throw new Error("Network response was not ok");
//       }
//       return response.json();
//     })
//     .then((data) => {
//       const board = data.board;
//       winner = data.winner;
//       const aiPlayed = data.aiPlayed; // Check if AI has played

//       // Update player turn text
//       let currPlayerElem = document.querySelector(".current-turn");
//       nextPlayer = data.nextPlayer;
//       if (nextPlayer == "H") {
//         currPlayerElem.innerHTML = "Human's turn";
//       } else {
//         currPlayerElem.innerHTML = "AI's turn";
//       }

//       // Update UI to reflect AI move if AI has played
//       if (aiPlayed) {
//         console.log("AI Played:" + aiPlayed);
//       }

//       console.log("Next Player: " + nextPlayer);

//       const slots = document.querySelectorAll(".column");

//       if (winner != null) {
//         let result = "Human";
//         if (winner == "A") {
//           result = "AI";
//         }
//         document.querySelector(".winner").innerHTML = result + " wins!!";
//         currPlayerElem.innerHTML = result + " wins!!";

//         // disable all move buttons
//         slots.forEach((slot) => {
//           slot.disabled = true;
//         });

//         // show game over screen after 3seconds
//         setTimeout(function () {
//           document
//             .querySelector(".game-over-container")
//             .classList.remove("hidden");
//         }, 2000);
//       }

//       // Update the UI to reflect current board
//       for (let i = 0; i < board.length; i++) {
//         for (let j = 0; j < board[i].length; j++) {
//           const curr_player = board[i][j].player;
//           if (curr_player === "H" || curr_player === "A") {
//             // Find the lowest available slot in the current column
//             const slot = document.getElementById(`slot-${i}-${j}`);
//             slot.classList.add(curr_player === "H" ? "player1" : "player2");

//             // if the puck is placed at the very top the disable all the buttons
//             // in this column to prevent player from using this move
//             if (slot.id.includes("slot-0")) {
//               let column = document.querySelectorAll(`.${slot.classList[1]}`);
//               column.forEach((row) => {
//                 row.disabled = true;
//               });
//             }
//           }
//         }
//       }
//     })
//     .catch((error) => {
//       console.error("There was a problem with the fetch operation:", error);
//     });
// }

// function restartGame() {
//   window.location.reload();
// }

// Create a Socket.IO instance and connect to the server
const socket = io();

// Handle 'connect' event (optional)
socket.on("connect", () => {
  "http://" + document.domain + ":" + location.port;
});

function play_move(event) {
  // Get the button element that was clicked
  const button = event.target;

  // Extract the move index from the button's ID
  const move = button.id.split("-")[2];
  console.log("Move: " + move);

  // Emit 'human_move' event with the selected move index
  socket.emit("human_move", parseInt(move)); // Ensure move is sent as an integer
}

socket.on("game_state", function (data) {
  // Update UI based on the received game state
  // Example:
  console.log("Received game state:", data);
  const board = data.board;
  winner = data.winner;
  nextPlayer = data.next_player;

  // Update player turn text
  let currPlayerElem = document.querySelector(".current-turn");
  if (nextPlayer == "H") {
    currPlayerElem.innerHTML = "Human's turn";
  } else {
    currPlayerElem.innerHTML = "AI's turn";
  }

  for (let i = 0; i < board.length; i++) {
    for (let j = 0; j < board[i].length; j++) {
      const curr_player = board[i][j].player;
      if (curr_player === "H" || curr_player === "A") {
        // Find the lowest available slot in the current column
        const slot = document.getElementById(`slot-${i}-${j}`);
        slot.classList.add(curr_player === "H" ? "player1" : "player2");

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

  if (winner != null) {
    console.log("Winner is: " + winner);

    let result = "Human";
    if (winner == "A") {
      result = "AI";
    }
    document.querySelector(".winner").innerHTML = result + " wins!!";
    let currPlayerElem = document.querySelector(".current-turn");
    currPlayerElem.innerHTML = result + " wins!!";

    const slots = document.querySelectorAll(".column");
    // disable all move buttons
    slots.forEach((slot) => {
      slot.disabled = true;
    });
  }
});

// Handle 'disconnect' event (optional)
socket.on("disconnect", () => {
  console.log("Disconnected from server");
});
