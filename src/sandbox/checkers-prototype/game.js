// ---GAME CONSTANTS----------------------------------------------------------------
const config = {
  type: Phaser.AUTO,
  width: 650,
  height: 650,
  parent: 'game',
  scene: {
    preload,
    create,
    update,
  },
};

const checkers = new Phaser.Game(config);

// 8x8 board
const MARGIN = 10;
const BOARD_SIZE = 8;
/*
I made the canvas background color black. Therefore, by making the game board
smaller to account for the margin, it'll appear as if there's a black border.
*/
const TILE_SIZE = (config.width - 2 * MARGIN) / BOARD_SIZE;
// colors we will use in this game
const COLORS = {
  light_brown: 0xefbb74,
  dark_brown: 0x6b4415,
  black: 0x000000,
  red: 0xff0000,
  white: 0xffffff,
  colorblind_blue: 0x1e88e5,
  colorblind_orange: 0xffc107,
};
let pieces = [];
let selectedPiece = null;
let currentPlayer = COLORS.red; // red starts first
// change to adjust the piece size, any value less than 2 would make the pieces
// bigger than the tiles
const RADIUS_SCALE_FACTOR = 2.5;
// selected piece highlight stroke width
const HIGHLIGHT_SIZE = 3;
let gameOver = false;
let drawOffered = false;
let drawOfferedBy = null;

// ----------------------------------------------------------------------------

// ---INIT FUNCTIONS-----------------------------------------------------------
function preload() { }

function create() {
  // Store reference to the scene
  const scene = this;

  drawBoard(this);
  populatePieces(this);

  // Set up forfeit and draw buttons
  const forfeitBtn = document.getElementById('forfeitBtn');
  const drawBtn = document.getElementById('drawBtn');
  const declineDrawBtn = document.getElementById('declineDrawBtn');
  const gameOverMessage = document.getElementById('gameOverMessage');
  const playAgainPrompt = document.getElementById('playAgainPrompt');
  const playAgainYes = document.getElementById('playAgainYes');
  const playAgainNo = document.getElementById('playAgainNo');

  function resetGame() {
    // Clear all pieces
    pieces.forEach(piece => piece.sprite.destroy());
    pieces = [];

    // Reset game state
    gameOver = false;
    selectedPiece = null;
    currentPlayer = COLORS.red;
    drawOffered = false;
    drawOfferedBy = null;

    // Reset UI
    gameOverMessage.textContent = '';
    gameOverMessage.classList.remove('show');
    playAgainPrompt.style.display = 'none';
    drawBtn.style.display = 'block';
    drawBtn.textContent = 'Offer Draw';
    forfeitBtn.style.display = 'block';
    declineDrawBtn.style.display = 'none';

    // Repopulate the board using the stored scene reference
    populatePieces(scene);
  }

  playAgainYes.addEventListener('click', resetGame);
  playAgainNo.addEventListener('click', () => {
    playAgainPrompt.style.display = 'none';
  });

  forfeitBtn.addEventListener('click', () => {
    if (!gameOver && currentPlayer === COLORS.red) {
      gameOver = true;
      gameOverMessage.textContent = 'Red player has forfeited! Black wins!';
      gameOverMessage.classList.add('show');
      document.getElementById('playAgainPrompt').style.display = 'block';
    } else if (!gameOver && currentPlayer === COLORS.black) {
      gameOver = true;
      gameOverMessage.textContent = 'Black player has forfeited! Red wins!';
      gameOverMessage.classList.add('show');
      document.getElementById('playAgainPrompt').style.display = 'block';
    }
  });

  function resetDrawOffer() {
    drawOffered = false;
    drawOfferedBy = null;
    gameOverMessage.textContent = '';
    gameOverMessage.classList.remove('show');
    drawBtn.textContent = 'Offer Draw';
    declineDrawBtn.style.display = 'none';
  }

  drawBtn.addEventListener('click', () => {
    if (gameOver) return;

    if (!drawOffered) {
      drawOffered = true;
      drawOfferedBy = currentPlayer;
      if (currentPlayer === COLORS.red) {
        gameOverMessage.textContent = 'Red player has offered a draw. Black player, please accept or decline.';
      } else {
        gameOverMessage.textContent = 'Black player has offered a draw. Red player, please accept or decline.';
      }
      gameOverMessage.classList.add('show');
      drawBtn.textContent = 'Accept Draw';
      declineDrawBtn.style.display = 'block';

    } else {
      // Accept Draw (second click)
      gameOver = true;
      gameOverMessage.textContent = 'Draw accepted! Game over!';
      gameOverMessage.classList.add('show');
      drawBtn.style.display = 'none';
      declineDrawBtn.style.display = 'none';
      forfeitBtn.style.display = 'none';
      document.getElementById('playAgainPrompt').style.display = 'block';
    }
  });

  declineDrawBtn.addEventListener('click', () => {
    if (drawOffered) {
      resetDrawOffer();
    }
  });
}

function update() { }
// ----------------------------------------------------------------------------

// Draw the game board
function drawBoard(scene) {
  // loop over the entire game board (y is column, x is row)
  for (let y = 0; y < BOARD_SIZE; y++) {
    for (let x = 0; x < BOARD_SIZE; x++) {
      // setting tile colors: even tiles = light brown, odd tiles = dark brown
      let tile_color = (x + y) % 2 === 0 ? COLORS.light_brown : COLORS.dark_brown;

      // draw tiles
      const tile = scene.add
        .rectangle(
          // phaser actually positions shape based on the center, not top-left
          // margin + x returns the top-left location of each tile
          // tile size / 2 returns the center of the tile
          MARGIN + x * TILE_SIZE + TILE_SIZE / 2, // x position
          MARGIN + y * TILE_SIZE + TILE_SIZE / 2, // y position
          TILE_SIZE, // width
          TILE_SIZE, // height
          tile_color
        )
        // make the tiles selectable so players can click on them to move pieces
        .setInteractive();

      // listens for clicks on tiles
      tile.on('pointerdown', () => {
        // does nothing if no pieces were selected or game is over
        if (!selectedPiece || gameOver) return;

        // see if there are any pieces at the selected square
        const targetPiece = getPiece(x, y);

        // if there's no piece on the selected square
        // and it is a valid move for the selected piece,
        // move the piece and end the player turn
        if (!targetPiece && isValidMove(selectedPiece, x, y)) {
          movePiece(selectedPiece, x, y);
          endTurn();
        }
      });
    }
  }
}

function createPiece(x, y, color, scene) {
  // create a piece
  const piece = {
    x,
    y,
    color,
    sprite: scene.add.circle(
      // same center position as when we create the board tiles/squares
      MARGIN + x * TILE_SIZE + TILE_SIZE / 2,
      MARGIN + y * TILE_SIZE + TILE_SIZE / 2,
      // circle radius
      TILE_SIZE / RADIUS_SCALE_FACTOR,
      color
    ),
  };

  // make the piece clickable
  piece.sprite.setInteractive();
  piece.sprite.on('pointerdown', () => {
    // don't allow piece selection if game is over
    if (gameOver) return;

    // deselect and remove highlight if click a selected piece
    if (selectedPiece === piece) {
      selectedPiece.sprite.setStrokeStyle();
      selectedPiece = null;

      // if player selects their own pieces (does nothing if they click on opponent pieces)
    } else if (piece.color === currentPlayer) {
      // clear previous selected piece
      if (selectedPiece) {
        selectedPiece.sprite.setStrokeStyle();
      }
      // highlight the current piece that is being selected and set them as 'selectedPiece'
      selectedPiece = piece;
      piece.sprite.setStrokeStyle(HIGHLIGHT_SIZE, COLORS.white);
    }
  });

  // push to array
  pieces.push(piece);
}

function populatePieces(scene) {
  // black has three rows
  for (let y = 0; y < 3; y++) {
    for (let x = 0; x < BOARD_SIZE; x++) {
      // create black pieces on odd/dark tiles
      if ((x + y) % 2 === 1) {
        createPiece(x, y, COLORS.black, scene);
      }
    }
  }

  // create red pieces at the bottom 3 rows
  for (let y = 5; y < 8; y++) {
    for (let x = 0; x < BOARD_SIZE; x++) {
      // create red pieces on odd/dark tiles
      if ((x + y) % 2 === 1) {
        createPiece(x, y, COLORS.red, scene);
      }
    }
  }
}

// check if a move is valid
function isValidMove(piece, moveX, moveY) {
  // calculate the change in y and x
  const dx = moveX - piece.x;
  const dy = moveY - piece.y;

  // with our current orientation, red pieces always move up and black pieces move down
  // may need to fix this once we introduce multiplayer, which would require
  // us to flip the board for different players
  const direction = piece.color === COLORS.red ? -1 : 1; // in js, y=0 at the top

  // Normal move (1 step diagonally)
  if (Math.abs(dx) === 1 && dy === direction) {
    return true;
  }

  // Jump move (2 steps diagonally)
  if (Math.abs(dx) === 2 && dy === 2 * direction) {
    // get the piece that was jumped over
    const captured = getPiece(piece.x + dx / 2, piece.y + dy / 2);
    // make sure there exists a piece that was jumped over, and it must be an opposing piece
    return (
      captured && captured.color !== piece.color
    );
  }

  // return false if it's not a normal or jump move
  return false;
}

function movePiece(piece, moveX, moveY) {
  const dx = moveX - piece.x;
  const dy = moveY - piece.y;

  // If it's a jump, remove the captured piece
  if (Math.abs(dx) === 2 && Math.abs(dy) === 2) {
    const captured = getPiece(piece.x + dx / 2, piece.y + dy / 2);
    if (captured) {
      captured.sprite.destroy(); // delete the sprite (remove from display state)
      pieces = pieces.filter((p) => p !== captured); // remove it from the array (game state)

      // Check for game over after capturing a piece
      checkGameOver();
    }
  }

  // Move the piece
  piece.x = moveX;
  piece.y = moveY;
  piece.sprite.x = MARGIN + piece.x * TILE_SIZE + TILE_SIZE / 2;
  piece.sprite.y = MARGIN + piece.y * TILE_SIZE + TILE_SIZE / 2;

  console.log("Current board state:", getBoardState());
}

// Check if the game is over due to all pieces of one color being captured
function checkGameOver() {
  const redPieces = pieces.filter(p => p.color === COLORS.red);
  const blackPieces = pieces.filter(p => p.color === COLORS.black);

  if (redPieces.length === 0) {
    gameOver = true;
    const gameOverMessage = document.getElementById('gameOverMessage');
    gameOverMessage.textContent = 'All red pieces captured! Black wins!';
    gameOverMessage.classList.add('show');
    document.getElementById('playAgainPrompt').style.display = 'block';
    document.getElementById('drawBtn').style.display = 'none';
    document.getElementById('forfeitBtn').style.display = 'none';
  } else if (blackPieces.length === 0) {
    gameOver = true;
    const gameOverMessage = document.getElementById('gameOverMessage');
    gameOverMessage.textContent = 'All black pieces captured! Red wins!';
    gameOverMessage.classList.add('show');
    document.getElementById('playAgainPrompt').style.display = 'block';
    document.getElementById('drawBtn').style.display = 'none';
    document.getElementById('forfeitBtn').style.display = 'none';
  }
}

// helper function to get the piece
function getPiece(x, y) {
  return pieces.find((p) => p.x === x && p.y === y);
}

// end the turn
function endTurn() {
  // remove the selected piece and its highlight
  if (selectedPiece) {
    selectedPiece.sprite.setStrokeStyle();
  }
  selectedPiece = null;

  // switch between red and black player turn
  currentPlayer = currentPlayer === COLORS.red ? COLORS.black : COLORS.red;

  // reset draw offer if it was made by the current player
  if (drawOffered && drawOfferedBy === currentPlayer) {
    const gameOverMessage = document.getElementById('gameOverMessage');
    const drawBtn = document.getElementById('drawBtn');
    const declineDrawBtn = document.getElementById('declineDrawBtn');
    drawOffered = false;
    drawOfferedBy = null;
    gameOverMessage.textContent = '';
    gameOverMessage.classList.remove('show');
    drawBtn.textContent = 'Offer Draw';
    declineDrawBtn.style.display = 'none';
  }
}

// Retrieves a 2D array representation of the board state where 0 are unoccupied
// positions, 1 are red pieces, 2 are black pieces
function getBoardState() {
  const board = [];
  for (let row = 0; row < BOARD_SIZE; row++) {
    const newRow = [];
    for (let col = 0; col < BOARD_SIZE; col++) {
      newRow.push(0);
    }
    board.push(newRow);
  }

  for (const piece of pieces) {
    const col = piece.x;
    const row = piece.y;

    if (row >= 0 && row < BOARD_SIZE && col >= 0 && col < BOARD_SIZE) {
      if (piece.color == COLORS.red) {
        board[row][col] = 1; // Red piece
      } else {
        board[row][col] = 2; // Black piece
      }
    }
  }

  return board;
}

function sendBoardToServer(boardState) {
  fetch('/api/board-state/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken(),
    },
    body: JSON.stringify({ board: boardState }),
  });
}

// Event Listener for Settings Menu
document.addEventListener('DOMContentLoaded', () => {
  const settingsContainer = document.getElementById('settings-container');

  settingsContainer.addEventListener('mouseover', () => {
    settingsContainer.classList.add('show');
  });

  settingsContainer.addEventListener('mouseout', () => {
    settingsContainer.classList.remove('show');
  });
});

// Function to change the color of all pieces
function changePieceColor(newColorOne, newColorTwo) {
  const firstPieceColor = pieces[0].color;
  pieces.forEach((piece) => {
    if (piece.color === firstPieceColor) {
      piece.color = newColorOne;
      piece.sprite.setFillStyle(newColorOne);
    }
    else {
      piece.color = newColorTwo;
      piece.sprite.setFillStyle(newColorTwo);
    }
  });
}

// Event listener for the toggle colorblind button
document.addEventListener('DOMContentLoaded', () => {
  const changeColorButton = document.getElementById('toggle-colorblind');
  changeColorButton.addEventListener('click', () => {
    const firstPieceColor = pieces[0].color;
    // if the first piece is a default color, change to colorblind colors
    if (firstPieceColor === COLORS.red || firstPieceColor === COLORS.black) {
      changePieceColor(COLORS.colorblind_blue, COLORS.colorblind_orange);
      changeColorButton.classList.add('selected');
    }
    // if the first piece is a colorblind color, change to default colors
    else {
      changePieceColor(COLORS.black, COLORS.red);
      changeColorButton.classList.remove('selected');

    }
  });
});
