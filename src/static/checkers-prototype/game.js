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
};
let pieces = [];
let selectedPiece = null;
let currentPlayer = COLORS.red; // red starts first
// change to adjust the piece size, any value less than 2 would make the pieces
// bigger than the tiles
const RADIUS_SCALE_FACTOR = 2.5;
// selected piece highlight stroke width
const HIGHLIGHT_SIZE = 3;

// ------------------- Get Board State ----------------------------------------
// From Database

async function fetchInitialBoardState() {
  try {
    const response = await fetch(`/games/checkers/${BOARD_ID}/state/`);
    if (!response.ok) {
      throw new Error("Failed to fetch board state");
    }
    const data = await response.json();
    return data.state;
  } catch (error) {
    console.error("Error loading board state:", error);
    return null;
  }
}

// ---INIT FUNCTIONS-----------------------------------------------------------
function preload() { }

async function create() {
  const state = await fetchInitialBoardState();
  if (state) {
    drawBoard(this);
    populatePiecesFromState(this, state);
  } else {
    console.warn("Using default board because state failed to load.");
    drawBoard(this);
    populatePieces(this); // fallback
  }
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
        // does nothing if no pieces were selected
        if (!selectedPiece) return;

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
      // highligt the current piece that is being selected and set them as 'selectedPiece'
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


function populatePiecesFromState(scene, state) {
  for (let y = 0; y < state.length; y++) {
    for (let x = 0; x < state[y].length; x++) {
      const cell = state[y][x];
      if (cell === 1) {
        createPiece(x, y, COLORS.red, scene);
      } else if (cell === 2) {
        createPiece(x, y, COLORS.black, scene);
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
    // make sure there exists a piece that was jumped over, and it most be an opposing piece
    return (
      captured && captured.color !== piece.color // must be an opponent piece
    );
  }

  // return false if it's not a normal or jump move
  // (meaning the move is not a diagonal move of 1 or 2 steps)
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
    }
  }

  // Move the piece
  // update the game state
  piece.x = moveX;
  piece.y = moveY;
  // update the display state
  piece.sprite.x = MARGIN + piece.x * TILE_SIZE + TILE_SIZE / 2;
  piece.sprite.y = MARGIN + piece.y * TILE_SIZE + TILE_SIZE / 2;

  // Log the current state
  const currentState = getBoardState();
  console.log("Current board state:", currentState);

  fetch(`/games/checkers/${BOARD_ID}/update/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ state: currentState }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (!data.success) {
        console.error("Failed to update board:", data.error);
      } else {
        console.log("Board updated successfully.");
      }
    })
    .catch((error) => console.error("Fetch error:", error));
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

// If you have more than one tab open it will automatically update by calling
// from the server

let lastKnownState = JSON.stringify(getBoardState());

function reloadBoardFromState(state) {
  // Clear existing pieces
  pieces.forEach(p => p.sprite.destroy());
  pieces = [];

  // Re-populate piece
  populatePiecesFromState(checkers.scene.scenes[0], state);
}

function update() {
  // Every 2 seconds, poll server for board state
  if (!window.lastPollTime || Date.now() - window.lastPollTime > 2000) {
    window.lastPollTime = Date.now();
    fetch(`/games/checkers/${BOARD_ID}/state/`)
      .then(res => res.json())
      .then(data => {
        const newState = JSON.stringify(data.state);
        if (newState !== lastKnownState) {
          lastKnownState = newState;
          reloadBoardFromState(data.state);
        }
      })
      .catch(err => console.error("Polling error:", err));
  }
}
