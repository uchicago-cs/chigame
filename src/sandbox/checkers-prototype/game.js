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
  yellow: 0xffff00,
};
let pieces = [];
let selectedPiece = null;
let currentPlayer = COLORS.red; // red starts first
let redCaptured = 0; // Number of pieces that red has captured
let blackCaptured = 0; // Number of pieces that black has captured
// change to adjust the piece size, any value less than 2 would make the pieces
// bigger than the tiles
const RADIUS_SCALE_FACTOR = 2.5;
// selected piece highlight stroke width
const HIGHLIGHT_SIZE = 3;

// an array to keep track of the highlighted tiles (valid moves)
let highlightedTiles = [];
let gameOver = false;
let drawOffered = false;
let drawOfferedBy = null;

//BOT SETTINGS
let vsEasyBot = true;

// ----------------------------------------------------------------------------

// ---INIT FUNCTIONS-----------------------------------------------------------
function preload() {
  this.load.image('crown', 'img/crown.svg');
  this.textures.get('crown').setFilter(Phaser.Textures.FilterMode.LINEAR);
  // load in the soundeffects
  this.load.audio('slide', 'sfx/slide.mp3');
  this.load.audio('hint', 'sfx/bling.mp3');
}

function create() {
  // Store reference to the scene
  const scene = this;

  drawBoard(this);
  populatePieces(this);

  // https://docs.phaser.io/api-documentation/namespace/input-keyboard-events#key_down
  // Listen for the 'h' key, give hint if pressed
  this.input.keyboard.on('keydown-H', () => {
    // Play hint sound effect
    this.sound.play('hint');

    giveHint();
  });

  // Set up forfeit and draw buttons
  const gameOverPrompts = document.getElementById('gameOverPrompts');
  const forfeitBtn = document.getElementById('forfeitBtn');
  const drawBtn = document.getElementById('drawBtn');
  const declineDrawBtn = document.getElementById('declineDrawBtn');
  const gameOverMessage = document.getElementById('gameOverMessage');
  const playAgainPrompt = document.getElementById('playAgainPrompt');
  const playAgainYes = document.getElementById('playAgainYes');
  const playAgainNo = document.getElementById('playAgainNo');
  const easyBot = document.getElementById('toggle-bot');

  // Score display
  const score = document.getElementById('score');

  function resetGame() {
    // Clear all pieces
    pieces.forEach((piece) => piece.sprite.destroy());
    pieces = [];

    // Reset game state
    gameOver = false;
    selectedPiece = null;
    currentPlayer = COLORS.red;
    drawOffered = false;
    drawOfferedBy = null;
    redCaptured = 0;
    blackCaptured = 0;

    // Reset UI
    gameOverPrompts.classList.remove('show');
    gameOverMessage.textContent = '';
    gameOverMessage.classList.remove('show');
    playAgainPrompt.style.display = 'none';
    drawBtn.style.display = 'block';
    drawBtn.textContent = 'Offer Draw';
    forfeitBtn.style.display = 'block';
    declineDrawBtn.style.display = 'none';
    score.innerHTML = 'Red: 0<br>Black: 0';

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
      gameOverPrompts.classList.add('show');
      gameOverMessage.textContent = 'Red player has forfeited! Black wins!';
      gameOverMessage.classList.add('show');
      document.getElementById('playAgainPrompt').style.display = 'flex';
      document.getElementById('forfeitBtn').style.display = 'none';
      document.getElementById('drawBtn').style.display = 'none';
    } else if (!gameOver && currentPlayer === COLORS.black) {
      gameOver = true;
      gameOverPrompts.classList.add('show');
      gameOverMessage.textContent = 'Black player has forfeited! Red wins!';
      gameOverMessage.classList.add('show');
      document.getElementById('playAgainPrompt').style.display = 'flex';
      document.getElementById('forfeitBtn').style.display = 'none';
      document.getElementById('drawBtn').style.display = 'none';
    }
  });

  function resetDrawOffer() {
    drawOffered = false;
    drawOfferedBy = null;
    gameOverPrompts.classList.remove('show');
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
        gameOverMessage.textContent =
          'Red player has offered a draw. Black player, please accept or decline.';
      } else {
        gameOverMessage.textContent =
          'Black player has offered a draw. Red player, please accept or decline.';
      }
      gameOverPrompts.classList.add('show');
      gameOverMessage.classList.add('show');
      drawBtn.textContent = 'Accept Draw';
      declineDrawBtn.style.display = 'flex';
    } else {
      // Accept Draw (second click)
      gameOver = true;
      gameOverPrompts.classList.add('show');
      gameOverMessage.textContent = 'Draw accepted! Game over!';
      gameOverMessage.classList.add('show');
      drawBtn.style.display = 'none';
      declineDrawBtn.style.display = 'none';
      forfeitBtn.style.display = 'none';
      document.getElementById('playAgainPrompt').style.display = 'flex';
    }
  });

  declineDrawBtn.addEventListener('click', () => {
    if (drawOffered) {
      resetDrawOffer();
    }
  });
  easyBot.textContent = `Easy Bot: ${vsEasyBot ? 'ON' : 'OFF'}`;
  easyBot.addEventListener('click', () => {
    vsEasyBot = !vsEasyBot;
    easyBot.textContent = `Easy Bot: ${vsEasyBot ? 'ON' : 'OFF'}`;
  });
}

function update() {}
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
          endTurn(scene);
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
    isking: false,
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
      clearHighlightedTiles();

      // if player selects their own pieces (does nothing if they click on opponent pieces)
    } else if (piece.color === currentPlayer) {
      // clear previous selected piece
      if (selectedPiece) {
        selectedPiece.sprite.setStrokeStyle();
      }
      // highlight the current piece that is being selected and set them as 'selectedPiece'

      // also highlight the tiles the piece can move to
      selectedPiece = piece;
      piece.sprite.setStrokeStyle(HIGHLIGHT_SIZE, COLORS.white);
      highlightValidMoves(scene, piece);
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

  const isKing = piece.isKing;

  // if the piece is a king, it can move in both y directions
  const validDirection = isKing ? Math.abs(dy) === 1 : dy === direction;
  const validJumpDirection = isKing ? Math.abs(dy) === 2 : dy === 2 * direction;

  // Normal move (1 step diagonally)
  if (Math.abs(dx) === 1 && validDirection) {
    return true;
  }

  // Jump move (2 steps diagonally)
  if (Math.abs(dx) === 2 && validJumpDirection) {
    // get the piece that was jumped over
    const captured = getPiece(piece.x + dx / 2, piece.y + dy / 2);
    // make sure there exists a piece that was jumped over, and it must be an opposing piece
    return captured && captured.color !== piece.color;
  }

  // return false if it's not a normal or jump move
  return false;
}

// Updates score on frontend
function updateScore() {
  const score = document.getElementById('score');
  score.innerHTML = 'Red: ' + redCaptured + '<br>Black: ' + blackCaptured;
}

function movePiece(piece, moveX, moveY) {
  const dx = moveX - piece.x;
  const dy = moveY - piece.y;

  // If it's a jump, remove the captured piece
  if (Math.abs(dx) === 2 && Math.abs(dy) === 2) {
    const captured = getPiece(piece.x + dx / 2, piece.y + dy / 2);
    if (captured) {
      captured.sprite.destroy(); // delete the sprite (remove from display state)
      if (captured.kingIcon) captured.kingIcon.destroy(); // destroy the icon as well
      pieces = pieces.filter((p) => p !== captured); // remove it from the array (game state)
      if (currentPlayer === COLORS.red) {
        redCaptured++;
      } else {
        blackCaptured++;
      }
      updateScore();

      // Check for game over after capturing a piece
      checkGameOver();
    }
  }

  // Move the piece
  piece.x = moveX;
  piece.y = moveY;

  const newX = MARGIN + moveX * TILE_SIZE + TILE_SIZE / 2;
  const newY = MARGIN + moveY * TILE_SIZE + TILE_SIZE / 2;

  // Animate movement
  checkers.scene.scenes[0].tweens.add({
    targets: piece.sprite,
    x: newX,
    y: newY,
    duration: 300,
    ease: 'Power3',
    onComplete: () => {
      // Check for king promotion
      if (
        (piece.color === COLORS.red && piece.y === 0) ||
        (piece.color === COLORS.black && piece.y === BOARD_SIZE - 1)
      ) {
        if (!piece.isKing) {
          piece.isKing = true;

          const crown = piece.sprite.scene.add.image(newX, newY, 'crown');
          crown.setDisplaySize(TILE_SIZE, TILE_SIZE);
          piece.kingIcon = crown;
        }
      }
    },
  });

  // Move king icon if applicable
  if (piece.isKing && piece.kingIcon) {
    checkers.scene.scenes[0].tweens.add({
      targets: piece.kingIcon,
      x: newX,
      y: newY,
      duration: 300,
      ease: 'Power3',
    });
  }

  // Play move sound
  piece.sprite.scene.sound.play('slide');

  console.log('Current board state:', getBoardState());
}

// Check if the game is over due to all pieces of one color being captured
function checkGameOver() {
  const redPieces = pieces.filter((p) => p.color === COLORS.red);
  const blackPieces = pieces.filter((p) => p.color === COLORS.black);

  if (redPieces.length === 0) {
    gameOver = true;
    const gameOverPrompts = document.getElementById('gameOverPrompts');
    const gameOverMessage = document.getElementById('gameOverMessage');
    gameOverPrompts.classList.add('show');
    gameOverMessage.textContent = 'All red pieces captured! Black wins!';
    gameOverMessage.classList.add('show');
    document.getElementById('playAgainPrompt').style.display = 'flex';
    document.getElementById('drawBtn').style.display = 'none';
    document.getElementById('forfeitBtn').style.display = 'none';
  } else if (blackPieces.length === 0) {
    gameOver = true;
    const gameOverPrompts = document.getElementById('gameOverPrompts');
    const gameOverMessage = document.getElementById('gameOverMessage');
    gameOverPrompts.classList.add('show');
    gameOverMessage.textContent = 'All black pieces captured! Red wins!';
    gameOverMessage.classList.add('show');
    document.getElementById('playAgainPrompt').style.display = 'flex';
    document.getElementById('drawBtn').style.display = 'none';
    document.getElementById('forfeitBtn').style.display = 'none';
  }
}

// helper function to get the piece
function getPiece(x, y) {
  return pieces.find((p) => p.x === x && p.y === y);
}

// end the turn
function endTurn(scene) {
  // remove the selected piece and its highlight
  if (selectedPiece) {
    selectedPiece.sprite.setStrokeStyle();
  }
  selectedPiece = null;

  // switch between red and black player turn
  currentPlayer = currentPlayer === COLORS.red ? COLORS.black : COLORS.red;
  // remove the highlight after a move is made
  clearHighlightedTiles();
}

// helper function to highlight the valid moves for the selected piece
function highlightValidMoves(scene, piece) {
  clearHighlightedTiles(); // remove any previous highlights

  // iterate through the board
  for (let y = 0; y < BOARD_SIZE; y++) {
    for (let x = 0; x < BOARD_SIZE; x++) {
      // check that the tile is not occupied and is a valid move
      if (!getPiece(x, y) && isValidMove(piece, x, y)) {
        // add a slighlty transparent white square on top of that tile to make
        // the tile appear highlighted
        const highlight = scene.add.rectangle(
          MARGIN + x * TILE_SIZE + TILE_SIZE / 2,
          MARGIN + y * TILE_SIZE + TILE_SIZE / 2,
          TILE_SIZE,
          TILE_SIZE,
          0xffffff,
          0.3
        );
        // add the game object to the array (so we can keep track and delete later)
        highlightedTiles.push(highlight);
      }
    }
  }
}

// helper function to clear all the highlighted tiles
function clearHighlightedTiles() {
  // remove each rect from the screen and then pop the reference from the array
  while (highlightedTiles.length > 0) {
    highlightedTiles.pop().destroy();
  }
}

// generate a random valid move
// after we finish implementing a bot, we could it make give an actual good suggestion
function giveHint() {
  // get all of the pieces of the current player
  const playerPieces = pieces.filter((p) => p.color === currentPlayer);
  let validMoves = [];

  // get all of the valid moves for all of the pieces
  for (const piece of playerPieces) {
    for (let y = 0; y < BOARD_SIZE; y++) {
      for (let x = 0; x < BOARD_SIZE; x++) {
        if (!getPiece(x, y) && isValidMove(piece, x, y)) {
          // add it to the array
          // (this is a shorthand to initialize objects btw if you don't know)
          validMoves.push({ piece, x, y });
        }
      }
    }
  }

  // We have yet to implement a feature where it checks whether there are valid
  // moves remaining for a player after each turn. In a real game of checkers
  // if there are no moves left, the player loses the game.
  if (validMoves.length > 0) {
    // Math.random() only returns floating point from 0 to 1 and would require a
    // separate helper function to return a random index from the array...
    // https://docs.phaser.io/phaser/concepts/math
    // phaser.math.rnd.pick() selects a random element from the array
    const randomHint = Phaser.Math.RND.pick(validMoves);
    // unlike chess, where there's rank and file, I don't think there's a proper
    // way of calling a specific square on the board. For now, I just have it return
    // the row and col on the matrix.
    alert(
      `Hint: Move ${currentPlayer === COLORS.red ? 'red' : 'black'} piece at (row ${
        randomHint.piece.y
      }, column ${randomHint.piece.x}) to (row ${randomHint.y}, column ${randomHint.x})`
    );
  } else {
    // in a normal checkers game, the player loses if there are no moves left
    alert('No valid moves.');
  }

  // remove the highlight after a move is made
  clearHighlightedTiles();
}

// helper function to highlight the valid moves for the selected piece
function highlightValidMoves(scene, piece) {
  clearHighlightedTiles(); // remove any previous highlights

  // iterate through the board
  for (let y = 0; y < BOARD_SIZE; y++) {
    for (let x = 0; x < BOARD_SIZE; x++) {
      // check that the tile is not occupied and is a valid move
      if (!getPiece(x, y) && isValidMove(piece, x, y)) {
        // add a slighlty transparent white square on top of that tile to make
        // the tile appear highlighted
        const highlight = scene.add.rectangle(
          MARGIN + x * TILE_SIZE + TILE_SIZE / 2,
          MARGIN + y * TILE_SIZE + TILE_SIZE / 2,
          TILE_SIZE,
          TILE_SIZE,
          0xffffff,
          0.3
        );
        // add the game object to the array (so we can keep track and delete later)
        highlightedTiles.push(highlight);
      }
    }
  }
}

// helper function to clear all the highlighted tiles
function clearHighlightedTiles() {
  // remove each rect from the screen and then pop the reference from the array
  while (highlightedTiles.length > 0) {
    highlightedTiles.pop().destroy();
  }
}

// generate a random valid move
// after we finish implementing a bot, we could it make give an actual good suggestion
function giveHint() {
  // get all of the pieces of the current player
  const playerPieces = pieces.filter((p) => p.color === currentPlayer);
  let validMoves = [];

  // get all of the valid moves for all of the pieces
  for (const piece of playerPieces) {
    for (let y = 0; y < BOARD_SIZE; y++) {
      for (let x = 0; x < BOARD_SIZE; x++) {
        if (!getPiece(x, y) && isValidMove(piece, x, y)) {
          // add it to the array
          // (this is a shorthand to initialize objects btw if you don't know)
          validMoves.push({ piece, x, y });
        }
      }
    }
  }

  // We have yet to implement a feature where it checks whether there are valid
  // moves remaining for a player after each turn. In a real game of checkers
  // if there are no moves left, the player loses the game.
  if (validMoves.length > 0) {
    // Math.random() only returns floating point from 0 to 1 and would require a
    // separate helper function to return a random index from the array...
    // https://docs.phaser.io/phaser/concepts/math
    // phaser.math.rnd.pick() selects a random element from the array
    const randomHint = Phaser.Math.RND.pick(validMoves);
    // unlike chess, where there's rank and file, I don't think there's a proper
    // way of calling a specific square on the board. For now, I just have it return
    // the row and col on the matrix.
    alert(
      `Hint: Move ${currentPlayer === COLORS.red ? 'red' : 'black'} piece at (row ${
        randomHint.piece.y
      }, column ${randomHint.piece.x}) to (row ${randomHint.y}, column ${randomHint.x})`
    );
  } else {
    // in a normal checkers game, the player loses if there are no moves left
    alert('No valid moves.');
  }

  // reset draw offer if it was made by the current player
  if (drawOffered && drawOfferedBy === currentPlayer) {
    const gameOverPrompts = document.getElementById('gameOverPrompts');
    const gameOverMessage = document.getElementById('gameOverMessage');
    const drawBtn = document.getElementById('drawBtn');
    const declineDrawBtn = document.getElementById('declineDrawBtn');
    drawOffered = false;
    drawOfferedBy = null;
    gameOverMessage.textContent = '';
    gameOverMessage.classList.remove('show');
    gameOverPrompts.classList.remove('show');
    drawBtn.textContent = 'Offer Draw';
    declineDrawBtn.style.display = 'none';
  }
  //if black and bot is on, schedule bot move
  if (vsEasyBot && currentPlayer === COLORS.black) {
    //delay so user has time to process bot movw after their own
    scene.time.delayedCall(300, easyBot, [scene], scene);
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
    } else {
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

//return arr of legal moves for given player
function getLegalMoves(color) {
  //arr to store legal moves
  const moves = [];
  //moving up or down board?
  const direction = color === COLORS.red ? -1 : 1;

  //loop thru pieces
  pieces.forEach((piece) => {
    if (piece.color !== color) return; //return for other p;layer peices
    // simple moves
    [-1, 1].forEach((diagonal) => {
      //try L and R diagonals
      const col = piece.x + diagonal; //new col
      const row = piece.y + direction; //new row
      if (
        //check if mvoe is valid
        col >= 0 &&
        col < BOARD_SIZE &&
        row >= 0 &&
        row < BOARD_SIZE &&
        !getPiece(col, row) &&
        isValidMove(piece, col, row)
      ) {
        moves.push({ piece, x: col, y: row }); //add move to arr
      }
    });
    // jump moves for captures
    [-2, 2].forEach((jump) => {
      const jump_col = piece.x + jump;
      const jump_row = piece.y + 2 * direction;
      if (
        jump_col >= 0 &&
        jump_col < BOARD_SIZE &&
        jump_row >= 0 &&
        jump_row < BOARD_SIZE &&
        !getPiece(jump_col, jump_row) &&
        isValidMove(piece, jump_col, jump_row)
      ) {
        moves.push({ piece, x: jump_col, y: jump_row });
      }
    });
  });

  return moves;
}

// Easy bot: pick a random legal move and play it
function easyBot(scene) {
  //get legal moves
  //check if game over
  //it not do a random legal move
  const legalMoves = getLegalMoves(COLORS.black);
  //if No legal moves
  if (legalMoves.length === 0) {
    console.log('Cant move');
    return;
  }
  //get random move
  const move = Phaser.Utils.Array.GetRandom(legalMoves);
  //execute move
  movePiece(move.piece, move.x, move.y);
  // end bot's turn
  endTurn(scene);
}

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
      coordElements.forEach((el) => document.body.removeChild(el));
      coordElements.length = 0;
    }
  });
});
