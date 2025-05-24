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

const PLAYER_RED = 'RED';
const PLAYER_BLACK = 'BLACK';

let playerColors = {
  [PLAYER_RED]: COLORS.red,
  [PLAYER_BLACK]: COLORS.black,
};

let pieces = [];
let selectedPiece = null;
let myColor = PLAYER_ID === 1 ? COLORS.red : COLORS.black;
let currentTurnColor = CURRENT_TURN_PLAYER_ID === 1 ? COLORS.red : COLORS.black;
// change to adjust the piece size, any value less than 2 would make the pieces
// bigger than the tiles
const RADIUS_SCALE_FACTOR = 2.5;
// selected piece highlight stroke width
const HIGHLIGHT_SIZE = 3;
let highlightedTiles = [];
// prevent player from moving pieces too quickly
let moveInProgress = false;

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

// ---INIT FUNCTIONS----------------------------------------------------------
function preload() {

}

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

function update() {

}
// ----------------------------------------------------------------------------

// Mirror and Unmirrors the board by transforming the coordinates
// This depends on whether they are player 2 or not
function maybeMirrorCoord(x, y) {
  return PLAYER_ID === 2 ? [BOARD_SIZE - 1 - x, BOARD_SIZE - 1 - y] : [x, y];
}

function maybeUnmirrorCoord(x, y) {
  return PLAYER_ID === 2 ? [BOARD_SIZE - 1 - x, BOARD_SIZE - 1 - y] : [x, y];
}

// Draw the game board
function drawBoard(scene) {
  // loop over the entire game board (y is column, x is row)
  for (let y = 0; y < BOARD_SIZE; y++) {
    for (let x = 0; x < BOARD_SIZE; x++) {
      const [logicalX, logicalY] = [x, y]; // store logical (unflipped) coordinates
      const [drawX, drawY] = maybeMirrorCoord(x, y);
      // setting tile colors: even tiles = light brown, odd tiles = dark brown
      let tile_color = (x + y) % 2 === 0 ? COLORS.light_brown : COLORS.dark_brown;

      // draw tiles
      const tile = scene.add
        .rectangle(
          // phaser actually positions shape based on the center, not top-left
          // margin + x returns the top-left location of each tile
          // tile size / 2 returns the center of the tile
          MARGIN + drawX * TILE_SIZE + TILE_SIZE / 2, // x position
          MARGIN + drawY * TILE_SIZE + TILE_SIZE / 2, // y position
          TILE_SIZE, // width
          TILE_SIZE, // height
          tile_color
        )
        // make the tiles selectable so players can click on them to move pieces
        .setInteractive();

      tile.logicalX = logicalX;
      tile.logicalY = logicalY;

      // listens for clicks on tiles
      tile.on('pointerdown', function () {
        if (!selectedPiece || selectedPiece.ownerId !== PLAYER_ID) return;

        // see if there are any pieces at the selected square
        const targetPiece = getPiece(this.logicalX, this.logicalY);

        // if there's no piece on the selected square
        // and it is a valid move for the selected piece,
        // move the piece and end the player turn
        if (!targetPiece && isValidMove(selectedPiece, this.logicalX, this.logicalY)) {
          movePiece(selectedPiece, this.logicalX, this.logicalY);
          // endTurn();
        }
      });
    }
  }
}

function createPiece(x, y, logicalColor, scene) {
  const owner = logicalColor === COLORS.red ? PLAYER_RED : PLAYER_BLACK;
  const ownerId = owner === PLAYER_RED ? 1 : 2; // You can use Django to inject real IDs

  const [drawX, drawY] = maybeMirrorCoord(x, y);

  const piece = {
    x,
    y,
    owner,
    ownerId, // <--- Add this to store which player owns the piece
    color: playerColors[owner],
    sprite: scene.add.circle(
      MARGIN + drawX * TILE_SIZE + TILE_SIZE / 2,
      MARGIN + drawY * TILE_SIZE + TILE_SIZE / 2,
      TILE_SIZE / RADIUS_SCALE_FACTOR,
      playerColors[owner]
    ),
  };

  piece.sprite.setInteractive();
  piece.sprite.on('pointerdown', () => {
    if (!selectedPiece && piece.ownerId !== PLAYER_ID) {
      // Not your piece
      return;
    }

    if (selectedPiece === piece) {
      selectedPiece.sprite.setStrokeStyle();
      selectedPiece = null;
      clearHighlights();
    } else if (piece.owner === getCurrentPlayerOwner()) {
      if (selectedPiece) selectedPiece.sprite.setStrokeStyle();
      selectedPiece = piece;
      piece.sprite.setStrokeStyle(HIGHLIGHT_SIZE, COLORS.white);
      highlightValidMoves(scene, piece);
    }
  });

  pieces.push(piece);
}


function getCurrentPlayerOwner() {
  return currentTurnColor === COLORS.red || currentTurnColor === COLORS.colorblind_orange
    ? PLAYER_RED
    : PLAYER_BLACK;
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
  const direction = piece.owner === PLAYER_RED ? -1 : 1; // in js, y=0 at the top

  // Normal move (1 step diagonally)
  if (Math.abs(dx) === 1 && dy === direction) {
    return true;
  }

  // Jump move (2 steps diagonally)
  if (Math.abs(dx) === 2 && dy === 2 * direction) {
    // get the piece that was jumped over
    const captured = getPiece(piece.x + dx / 2, piece.y + dy / 2);
    // make sure there exists a piece that was jumped over, and it most be an opposing piece
    return captured && captured.owner !== piece.owner;
  }

  // return false if it's not a normal or jump move
  // (meaning the move is not a diagonal move of 1 or 2 steps)
  return false;
}

// helper function to highlight the valid moves for the selected piece
function highlightValidMoves(scene, piece) {
  // clear old highlights
  clearHighlights();

  // iterate through the board
  for (let y = 0; y < BOARD_SIZE; y++) {
    for (let x = 0; x < BOARD_SIZE; x++) {
      // check that the tile is not occupied and is a valid move
      if (!getPiece(x, y) && isValidMove(piece, x, y)) {
        const [drawX, drawY] = maybeMirrorCoord(x, y);

        // add a slighlty transparent white square on top of that tile to make
        // the tile appear highlighted
        const highlight = scene.add.rectangle(
          MARGIN + drawX * TILE_SIZE + TILE_SIZE / 2,
          MARGIN + drawY * TILE_SIZE + TILE_SIZE / 2,
          TILE_SIZE,
          TILE_SIZE,
          COLORS.white,
          0.3
        );

        // Track it for later cleanup
        highlightedTiles.push(highlight);
      }
    }
  }
}

// helper function to clear all the highlighted tiles
function clearHighlights() {
  while (highlightedTiles.length > 0) {
    highlightedTiles.pop().destroy();
  }
}


function movePiece(piece, moveX, moveY) {
  if (moveInProgress) return;
  moveInProgress = true;

  updateScore();

  if (PLAYER_ID !== CURRENT_TURN_PLAYER_ID) {
    return;
  }

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
  const [drawX, drawY] = maybeMirrorCoord(moveX, moveY);
  piece.sprite.x = MARGIN + drawX * TILE_SIZE + TILE_SIZE / 2;
  piece.sprite.y = MARGIN + drawY * TILE_SIZE + TILE_SIZE / 2;


  // Log the current state
  const currentState = getBoardState();
  console.log("Current board state:", currentState);

  fetch(`/games/checkers/${BOARD_ID}/update/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      state: currentState,
      next_player_id: PLAYER_ID === 1 ? 2 : 1,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (!data.success) {
        console.error("Failed to update board:", data.error);
      } else {
        console.log("Board updated successfully.");
        endTurn();
      }
    })
    .catch((err) => {
      console.error("Network error:", err);
    })
    .finally(() => {
      moveInProgress = false;
    });
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
  currentTurnColor = (currentTurnColor === COLORS.red) ? COLORS.black : COLORS.red;
  clearHighlights();
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
      if (piece.owner == PLAYER_RED) {
        board[row][col] = 1; // Red piece
      } else {
        board[row][col] = 2; // Black piece
      }
    }
  }

  return board;
}

// Updates score on frontend
function updateScore() {
  const redCount = pieces.filter(p => p.owner === PLAYER_RED).length;
  const blackCount = pieces.filter(p => p.owner === PLAYER_BLACK).length;

  const redCaptured = 12 - blackCount;
  const blackCaptured = 12 - redCount;

  const score = document.getElementById('score');
  score.innerHTML = `Red: ${redCaptured}<br>Black: ${blackCaptured}`;
}


// If you have more than one tab open it will automatically update by calling
// from the server

let lastKnownState = JSON.stringify(getBoardState());

function reloadBoardFromState(state) {
  // Clear existing pieces
  pieces.forEach(p => p.sprite.destroy());
  pieces = [];

  // Re-populate pieces
  populatePiecesFromState(checkers.scene.scenes[0], state);
}

function update() {
  updateScore();
  // Every 2 seconds, poll server for board state
  if (!window.lastPollTime || Date.now() - window.lastPollTime > 2000) {
    window.lastPollTime = Date.now();
    fetch(`/games/checkers/${BOARD_ID}/state/`)
      .then(res => res.json())
      .then(data => {
        const newState = JSON.stringify(data.state);
        CURRENT_TURN_PLAYER_ID = data.current_turn_player_id;
        currentTurnColor = CURRENT_TURN_PLAYER_ID === 1 ? COLORS.red : COLORS.black;
        if (newState !== lastKnownState) {
          lastKnownState = newState;
          reloadBoardFromState(data.state);
        }
      })
      .catch(err => console.error("Polling error:", err));
  }
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
function changePieceColor(newBlack, newRed) {
  playerColors[PLAYER_BLACK] = newBlack;
  playerColors[PLAYER_RED] = newRed;

  pieces.forEach((piece) => {
    const newColor = playerColors[piece.owner];
    piece.color = newColor;
    piece.sprite.setFillStyle(newColor);
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

// Coordinates overlay button
document.addEventListener('DOMContentLoaded', () => {
  const toggleCoordinatesBtn = document.getElementById('toggle-coordinates');
  let coordsVisible = false;
  const coordElements = [];

  toggleCoordinatesBtn.addEventListener('click', () => {
    coordsVisible = !coordsVisible;

    if (coordsVisible) {
      // get board position on screen
      const gameDiv = document.getElementById('game');
      const rect = gameDiv.getBoundingClientRect();

      // for each index, create a top label and a left label
      for (let i = 0; i < BOARD_SIZE; i++) {
        // Column label
        const colLabel = document.createElement('div');
        colLabel.textContent = i + 1;
        Object.assign(colLabel.style, {
          position: 'absolute',
          left: `${rect.left + MARGIN + i * TILE_SIZE + TILE_SIZE / 2}px`,
          top: `${rect.top - 20}px`,
          transform: 'translateX(-50%)',
          fontFamily: '"Outfit", sans-serif',
          color: '#3b2f2a',
          userSelect: 'none',
          pointerEvents: 'none',
        });
        document.body.appendChild(colLabel);
        coordElements.push(colLabel);

        // Row label
        const rowLabel = document.createElement('div');
        rowLabel.textContent = i + 1;
        Object.assign(rowLabel.style, {
          position: 'absolute',
          left: `${rect.left - 20}px`,
          top: `${rect.top + MARGIN + i * TILE_SIZE + TILE_SIZE / 2}px`,
          transform: 'translateY(-50%)',
          fontFamily: '"Outfit", sans-serif',
          color: '#3b2f2a',
          userSelect: 'none',
          pointerEvents: 'none',
        });
        document.body.appendChild(rowLabel);
        coordElements.push(rowLabel);
      }

    } else {
      // remove coordinates
      coordElements.forEach(el => document.body.removeChild(el));
      coordElements.length = 0;
    }
  });
});
