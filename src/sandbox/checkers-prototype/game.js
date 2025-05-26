// ---GAME CONSTANTS----------------------------------------------------------------
const START_WIDTH = 650;
const START_HEIGHT = 650;
const START_MARGIN = 10;
const START_HIGHLIGHT_SIZE = 3;

const config = {
  type: Phaser.AUTO,
  width: START_WIDTH,
  height: START_HEIGHT,
  parent: 'game',
  scene: {
    preload,
    create,
    update,
  },
};

const checkers = new Phaser.Game(config);

// 8x8 board
const BOARD_SIZE = 8;
let margin = START_MARGIN;

/*
I made the canvas background color black. Therefore, by making the game board
smaller to account for the margin, it'll appear as if there's a black border.
*/
let tiles = [];
let tile_size = (config.width - 2 * START_MARGIN) / BOARD_SIZE;

// global variables for the coordinates overlay
let coordsVisible = false;
const coordElements = [];

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
let lightPiece = COLORS.red;
let darkPiece = COLORS.black;
let pieces = [];
let selectedPiece = null;
let currentPlayer = lightPiece; // red starts first
let redCaptured = 0; // Number of pieces that red has captured
let blackCaptured = 0; // Number of pieces that black has captured
// change to adjust the piece size, any value less than 2 would make the pieces
// bigger than the tiles
const RADIUS_SCALE_FACTOR = 2.5;
// selected piece highlight stroke width
let highlight_size = START_HIGHLIGHT_SIZE;

// an array to keep track of the highlighted tiles (valid moves)
let highlightedTiles = [];
let gameOver = false;
let drawOffered = false;
let drawOfferedBy = null;
// Initial time for each player
let redTime = 300;
let blackTime = 300;
// this will determine whose timer to decrement
let activeTimer = null;

//BOT SETTINGS
let botMode = 'none'; //OFF -> EASY -> MEDIUM ->HARD

// track mute state outside of phaser game
let muted = false;

// default volume
let volumeAmount = 1;

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
  const endPieceDiv = document.getElementById('endScreenPiece');

  drawBoard(this);
  populatePieces(this);

  // https://docs.phaser.io/api-documentation/namespace/input-keyboard-events#key_down
  // Listen for the 'h' key, give hint if pressed
  this.input.keyboard.on('keydown-H', () => {
    // Play hint sound effect
    this.sound.play('hint', { volume: volumeAmount });

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
  const botToggle = document.getElementById('toggle-bot');

  // Score display
  const score = document.getElementById('score');

  function resetGame() {
    // Clear all pieces
    pieces.forEach((piece) => piece.sprite.destroy());
    pieces = [];

    // Reset game state
    gameOver = false;
    selectedPiece = null;
    currentPlayer = lightPiece;
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

    // reset the timers
    stopPlayerTimer();
    redTime = 300;
    blackTime = 300;
    updateTimerDisplay();
    startPlayerTimer();
  }

  playAgainYes.addEventListener('click', resetGame);
  playAgainNo.addEventListener('click', () => {
    // hide the play‐again prompt and game‐over overlay
    playAgainPrompt.style.display = 'none';
    gameOverPrompts.classList.remove('show');
    gameOverMessage.classList.remove('show');

    const msg = gameOverMessage.textContent || '';
    // only proceed on a win (not on a draw)
    if (msg.includes('wins')) {
      // determine if it’s a black‐win or red‐win
      const isBlackWin = msg.includes('Black wins');
      const winnerHex = isBlackWin ? '#000000' : '#ff0000';

      // show & color the spinner
      endPieceDiv.classList.remove('hidden');
      endPieceDiv.classList.add('show');
      endPieceDiv.style.color = winnerHex;

      // show & set the overlay text in the same color
      const textDiv = document.getElementById('endScreenText');
      textDiv.textContent = isBlackWin ? 'Black Wins!' : 'Red Wins!';
      textDiv.style.color = winnerHex;
      textDiv.classList.remove('hidden');
      textDiv.classList.add('show');
    }
  });

  forfeitBtn.addEventListener('click', () => {
    if (!gameOver && currentPlayer === lightPiece) {
      gameOver = true;
      stopPlayerTimer();
      gameOverPrompts.classList.add('show');
      gameOverMessage.textContent = 'Red player has forfeited! Black wins!';
      gameOverMessage.classList.add('show');
      document.getElementById('playAgainPrompt').style.display = 'flex';
      document.getElementById('forfeitBtn').style.display = 'none';
      document.getElementById('drawBtn').style.display = 'none';
    } else if (!gameOver && currentPlayer === darkPiece) {
      gameOver = true;
      stopPlayerTimer();
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
      if (currentPlayer === lightPiece) {
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
      stopPlayerTimer();
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

  botToggle.textContent = 'Bot: OFF';
  botToggle.addEventListener('click', () => {
    if (botMode === 'none'){botMode = 'easy';}
    else if (botMode === 'easy'){botMode = 'medium';}
    else if(botMode === 'medium'){botMode = 'hard';}
    else {botMode = 'none';}
    const labels = { none: 'OFF', easy: 'Easy', medium: 'Medium', hard: 'Hard' };
    botToggle.textContent = `Bot: ${labels[botMode]}`;
    if (currentPlayer === COLORS.black && botMode !== 'none'){
        const func = botMode === 'easy' ? easyBot
        : botMode === 'medium' ? mediumBot
        : hardBot;
        scene.time.delayedCall(300, func, [scene], scene)
    }
  updateTimerDisplay(); // initial display
  startPlayerTimer(); // red starts first
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
      let tile = scene.add
        .rectangle(
          // phaser actually positions shape based on the center, not top-left
          // margin + x returns the top-left location of each tile
          // tile size / 2 returns the center of the tile
          margin + x * tile_size + tile_size / 2, // x position
          margin + y * tile_size + tile_size / 2, // y position
          tile_size, // width
          tile_size, // height
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
      tiles.push(tile);
    }
  }
}

// function to create a single piece. Adds the piece to the pieces array
function createPiece(x, y, color, scene) {
  // create a piece
  let piece = {
    x,
    y,
    color,
    isking: false,
    sprite: scene.add.circle(
      // same center position as when we create the board tiles/squares
      margin + x * tile_size + tile_size / 2,
      margin + y * tile_size + tile_size / 2,
      // circle radius
      tile_size / RADIUS_SCALE_FACTOR,
      color
    ),
  };

  // make the piece clickable
  piece.sprite.setInteractive();
  piece.sprite.on('pointerdown', () => {
    const settingsContainer = document.getElementById('settings-container');

    // don't allow piece selection if menu is open;
    if (settingsContainer.classList.contains('show')) return;

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
      piece.sprite.setStrokeStyle(highlight_size, COLORS.white);
      highlightValidMoves(scene, piece);
    }
  });

  // push to array
  pieces.push(piece);
}

// function to populate the board with pieces, added to the pieces array
function populatePieces(scene) {
  // black has three rows
  for (let y = 0; y < 3; y++) {
    for (let x = 0; x < BOARD_SIZE; x++) {
      // create black pieces on odd/dark tiles
      if ((x + y) % 2 === 1) {
        createPiece(x, y, darkPiece, scene);
      }
    }
  }

  // create red pieces at the bottom 3 rows
  for (let y = 5; y < 8; y++) {
    for (let x = 0; x < BOARD_SIZE; x++) {
      // create red pieces on odd/dark tiles
      if ((x + y) % 2 === 1) {
        createPiece(x, y, lightPiece, scene);
      }
    }
  }
}

// Finds all possible paths the selected piece can take
// This function finds all possible jump paths for a given piece,
// including single and multi-jump chains.
// Each path includes a list of moves and the pieces captured along the way.
function getJumpPaths(piece) {
  var allPaths = []; // Store all possible jump paths

  // Recursive helper function to explore jump chains
  function explore(x, y, capturedPieces, movePath, visited) {
    var extended = false;

    // Define possible jump directions (left or right)
    var dxList = [-2, 2];

    // Determine vertical jump direction (up for red, down for black)
    var dy;
    if (piece.color === lightPiece) {
      dy = -2;
    } else {
      dy = 2;
    }

    // Loop through both left and right diagonal jump options
    for (var i = 0; i < dxList.length; i++) {
      var dx = dxList[i];

      // Calculate target tile for the jump
      var newX = x + dx;
      var newY = y + dy;

      // Calculate coordinates of the piece being jumped over (in between)
      var midX = x + dx / 2;
      var midY = y + dy / 2;
      var midKey = midX + ',' + midY; // used to track visited mid-pieces

      // Make sure the jump destination is on the board and not occupied
      if (
        newX >= 0 && newX < BOARD_SIZE &&
        newY >= 0 && newY < BOARD_SIZE &&
        !getPiece(newX, newY)
      ) {
        var midPiece = getPiece(midX, midY);

        // Check if there's an opponent's piece to jump over,
        // and it hasn't been jumped already in this chain
        if (
          midPiece &&
          midPiece.color !== piece.color &&
          !visited.has(midKey)
        ) {
          // Clone visited set and mark this piece as visited
          var newVisited = new Set(visited);
          newVisited.add(midKey);

          // Clone the list of captured pieces and add this one
          var newCaptured = capturedPieces.slice();
          newCaptured.push(midPiece);

          // Clone the move path and add the new position
          var newPath = movePath.slice();
          newPath.push({ x: newX, y: newY });

          // Save this partial or full jump path
          allPaths.push({
            path: newPath.slice(),
            captures: newCaptured.slice()
          });

          // Recursively explore further jumps from this new position
          explore(newX, newY, newCaptured, newPath, newVisited);

          extended = true;
        }
      }
    }
  }

  // Start exploring from the piece's current position with an empty path
  explore(piece.x, piece.y, [], [], new Set());

  // Return all valid jump chains
  return allPaths;
}

// check if a move is valid
function isValidMove(piece, moveX, moveY) {
  // calculate the change in y and x
  const dx = moveX - piece.x;
  const dy = moveY - piece.y;

  // with our current orientation, red pieces always move up and black pieces move down
  // may need to fix this once we introduce multiplayer, which would require
  // us to flip the board for different players
  const direction = piece.color === lightPiece ? -1 : 1; // in js, y=0 at the top

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

// function to move a piece
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
      if (currentPlayer === lightPiece) {
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

  const newX = margin + moveX * tile_size + tile_size / 2;
  const newY = margin + moveY * tile_size + tile_size / 2;

  // Animate movement
  checkers.scene.scenes[0].tweens.add({
    targets: piece.sprite,
    x: newX,
    y: newY,
    duration: 250, // I think best to have this in 200-300 ms range
    ease: 'Power3',
    // onComplete is needed so crown icon only loads after animation is over
    onComplete: () => {
      // Check for king promotion
      if (
        (piece.color === lightPiece && piece.y === 0) ||
        (piece.color === darkPiece && piece.y === BOARD_SIZE - 1)
      ) {
        if (!piece.isKing) {
          piece.isKing = true;
          const crown = piece.sprite.scene.add.image(newX, newY, 'crown');
          crown.setDisplaySize(tile_size, tile_size);
          piece.kingIcon = crown;
        }
      }
    },
  });

  // Play move sound effect
  piece.sprite.scene.sound.play('slide', { volume: volumeAmount });
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

  //console.log('Current board state:', getBoardState());
}

// Check if the game is over due to all pieces of one color being captured
function checkGameOver() {
  const redPieces = pieces.filter((p) => p.color === lightPiece);
  const blackPieces = pieces.filter((p) => p.color === darkPiece);

  if (redPieces.length === 0) {
    gameOver = true;
    stopPlayerTimer();
    const gameOverPrompts = document.getElementById('gameOverPrompts')
    const gameOverMessage = document.getElementById('gameOverMessage');
    gameOverPrompts.classList.add('show');
    gameOverMessage.textContent = 'All red pieces captured! Black wins!';
    gameOverMessage.classList.add('show');
    document.getElementById('playAgainPrompt').style.display = 'flex';
    document.getElementById('drawBtn').style.display = 'none';
    document.getElementById('forfeitBtn').style.display = 'none';
  } else if (blackPieces.length === 0) {
    gameOver = true;
    stopPlayerTimer();
    const gameOverPrompts = document.getElementById('gameOverPrompts')
    const gameOverMessage = document.getElementById('gameOverMessage');
    gameOverPrompts.classList.add('show');
    gameOverMessage.textContent = 'All black pieces captured! Red wins!';
    gameOverMessage.classList.add('show');
    document.getElementById('playAgainPrompt').style.display = 'flex';
    document.getElementById('drawBtn').style.display = 'none';
    document.getElementById('forfeitBtn').style.display = 'none';
  }
}

// helper function to get a piece from its x, y location on the board
function getPiece(x, y) {
  return pieces.find((p) => p.x === x && p.y === y);
}

// end the turn
function endTurn(scene) {
  stopPlayerTimer(); // stop current timer
  // remove the selected piece and its highlight
  if (selectedPiece) {
    selectedPiece.sprite.setStrokeStyle();
  }
  selectedPiece = null;

  // switch between red and black player turn

  currentPlayer = currentPlayer  === lightPiece ? darkPiece : lightPiece;
  //if black and bot is on, schedule bot move
  if (currentPlayer === darkPiece) {
    if (botMode === 'easy')   scene.time.delayedCall(300, easyBot,   [scene], scene);
    if (botMode === 'medium') scene.time.delayedCall(300, mediumBot, [scene], scene);
    if (botMode === 'hard')   scene.time.delayedCall(300, hardBot,   [scene], scene);
  }
  startPlayerTimer(); // start next player’s timer
  // remove the highlight after a move is made
  clearHighlightedTiles();

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
      `Hint: Move ${currentPlayer === lightPiece ? 'red' : 'black'} piece at (row ${
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

  var jumpPaths = getJumpPaths(piece);

  if (jumpPaths.length > 0) {
    // Highlight all final landing squares of all jump paths
    for (var i = 0; i < jumpPaths.length; i++) {
      var jump = jumpPaths[i];
      var finalMove = jump.path[jump.path.length - 1];

      // draw the tile highlight
      var highlight = scene.add.rectangle(
        margin + finalMove.x * tile_size + tile_size / 2,
        margin + finalMove.y * tile_size + tile_size / 2,
        tile_size,
        tile_size,
        0xffffff,
        0.3
      );

      highlight.setInteractive();

      // Allow clicking to perform full jump path (even if it’s just 1 jump)
      highlight.on('pointerdown', (function (jumpData) {
        return function () {
          executeJumpChain(piece, jumpData);
          endTurn(scene);
        };
      })(jump));

      highlightedTiles.push(highlight);
    }

    return; // only jumps allowed when available
  }

  // If no jumps, fallback to normal diagonal move
  var dxOptions = [-1, 1];
  var dy = 1;
  if (piece.color === lightPiece) {
    dy = -1;
  }

  for (var i = 0; i < dxOptions.length; i++) {
    var dx = dxOptions[i];
    var newX = piece.x + dx;
    var newY = piece.y + dy;

    if (
      newX >= 0 && newX < BOARD_SIZE &&
      newY >= 0 && newY < BOARD_SIZE &&
      !getPiece(newX, newY)
    ) {
      // adds a slightly transparent square
      var highlight = scene.add.rectangle(
        margin + newX * tile_size + tile_size / 2,
        margin + newY * tile_size + tile_size / 2,
        tile_size,
        tile_size,
        0xffffff,
        0.3
      );

      highlight.setInteractive();
      highlight.on('pointerdown', (function (x, y) {
        return function () {
          movePiece(piece, x, y);
          endTurn(scene);
        };
      })(newX, newY));

      highlightedTiles.push(highlight);
    }
  }
}

// function to execute a multiple jump chain
function executeJumpChain(piece, jump) {
  for (var i = 0; i < jump.captures.length; i++) {
    var captured = jump.captures[i];
    captured.sprite.destroy();
    pieces = pieces.filter(function (p) {
      return p !== captured;
    });

    if (currentPlayer === lightPiece) {
      redCaptured++;
    } else {
      blackCaptured++;
    }
  }

  updateScore();
  checkGameOver();

  var final = jump.path[jump.path.length - 1];
  piece.x = final.x;
  piece.y = final.y;
  piece.sprite.x = margin + final.x * tile_size + tile_size / 2;
  piece.sprite.y = margin + final.y * tile_size + tile_size / 2;

  // move the king icon if applicable
  if (piece.isKing && piece.kingIcon) {
    piece.kingIcon.x = piece.sprite.x;
    piece.kingIcon.y = piece.sprite.y;
  }

  // check for king promotion
  if (
    (piece.color === lightPiece && piece.y === 0) ||
    (piece.color === darkPiece && piece.y === BOARD_SIZE - 1)
  ) {
    if (!piece.isKing) {
      piece.isKing = true;
      const crown = piece.sprite.scene.add.image(
        margin + piece.x * tile_size + tile_size / 2,
        margin + piece.y * tile_size + tile_size / 2,
        'crown'
      );
      crown.setDisplaySize(tile_size, tile_size);
      piece.kingIcon = crown;
    }
  }

  piece.sprite.scene.sound.play('slide');
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
      if (piece.color == lightPiece) {
        board[row][col] = 1; // Red piece
      } else {
        board[row][col] = 2; // Black piece
      }
    }
  }

  return board;
}

// makes a post request to the server with the current board state
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
      changeColorButton.classList.add('selected');
      lightPiece = COLORS.colorblind_orange;
      darkPiece = COLORS.colorblind_blue;
      if (currentPlayer === COLORS.red) {
        currentPlayer = lightPiece;
      } else {
        currentPlayer = darkPiece;
      }
    }
    // if the first piece is a colorblind color, change to default colors
    else {
      changePieceColor(COLORS.black, COLORS.red);
      changeColorButton.classList.remove('selected');
      lightPiece = COLORS.red;
      darkPiece = COLORS.black;
      if (currentPlayer === COLORS.colorblind_orange) {
        currentPlayer = lightPiece;
      } else {
        currentPlayer = darkPiece;
      }
    }
    changePieceColor(darkPiece, lightPiece);
  });
});

// Event listener for the volume slider
document.addEventListener('DOMContentLoaded', () => {
  const volumeSlider = document.getElementById("volume-slider");
  const volumeDisplay = document.getElementById("volume-display");

  function updateVolume() {
    volumeAmount = volumeSlider.value / 100;
    volumeDisplay.textContent = `${volumeSlider.value}%`;

    // math to align the slider
    const thumbX = (volumeSlider.value - volumeSlider.min) /
      (volumeSlider.max - volumeSlider.min) *
      (volumeSlider.getBoundingClientRect().width -
        parseFloat(window.getComputedStyle(volumeSlider).getPropertyValue('height'))) +
      volumeSlider.offsetLeft;

    volumeDisplay.style.left = `${thumbX}px`;
    volumeDisplay.style.top = `${volumeSlider.offsetTop - 25}px`;
    volumeDisplay.style.transform = `translate(-25%, 0)`;
  }

  volumeSlider.addEventListener("input", updateVolume);
  volumeSlider.addEventListener("mouseover", () => {
    volumeDisplay.style.opacity = "100";
    volumeDisplay.style.visibility = "visible";
    updateVolume();
  });

  volumeSlider.addEventListener("mouseout", () => {
    volumeDisplay.style.opacity = "0";
    volumeDisplay.style.visibility = "hidden";
  });
});

//function to determine if a given move is a capture for bot use
function is_capture(piece, x, y) {
    return Math.abs(x - piece.x) === 2 && Math.abs(y - piece.y) === 2;
}
//coordinate dist from peice coords to board center for bot use
function get_dist_from_center(x, y) {
    const center = (BOARD_SIZE - 1) / 2;
    return Math.hypot(x - center, y - center);
  }
//function to simulate a move on a copy of the board, returns board
function simMove(board, {piece, x, y}){
    //get board copy
    const copy = board.map(r => r.slice());
    //get val in pieces spot
    const val = board[piece.y][piece.x];
    //clear out
    copy[piece.y][piece.x] = 0;

    //if it a capture, remove captured piece
    if (Math.abs(x - piece.x) === 2) {
    const capture_col = (x + piece.x) / 2 | 0; //col of captured p
    const capture_row = (y + piece.y) / 2 | 0; //row of captured peice
    copy[capture_row][capture_col] = 0; //remove
    }

    copy[y][x] = val;
    return copy

}
//function to compute optimality of pos for black for comparison in hard bot
//inputs board and returns score of how good it is for black
function scoreBoard(board){
    let score = 0; //init score
    const center = (BOARD_SIZE -1)/2; //get center of board
    //loop through board
    for (let y = 0; y<BOARD_SIZE; y++){
        for (let x = 0; x<BOARD_SIZE; x++){
            const sq_val = board[y][x];
            if (sq_val === 2){ //if there is a black piece
            score += 100;
            score -= Math.hypot(x-center, y-center);//Black far from center = bad
            }
            else if (sq_val === 1){
                //if there is a red piece
                score -= 100;
                score += Math.hypot(x-center, y-center);
            }
        }
    }
    //add 5 points to score for black legal moves and -5 for red legal moves
    score += getLegalMoves(COLORS.black).length *5;
    score -= getLegalMoves(COLORS.red).length *5;
    return score;

}
//in order for the hard bot to "be smart", we are going to  have it "think ahead"
//In order to do this effeciently, we need to iterate over all possible moves
//that can be made by either player, and the responses to those moves
//Then once it has done that it finds the best board for black
//Then it assumes black will max the scoreBoard and red will min it
//So basically we are looking for the move where if red and black play optimally
//This is the best move for black
//Similar to the road trip game problem from HW#8 CMSC 27200, where each player
//is trying to pick the bet move, and assume the opponent is also picking the best move for themselves
//i.e Bot wants to max the score and player wants to min the score
function minimax(board, depth, alpha, beta, maximizing) {
    //check for leaf
    if (depth === 0) return scoreBoard(board);
    //pick legal moves for black when maxxing, red when minning
    const player = maximizing ? COLORS.black : COLORS.red;
    const moves = getLegalMoves(player).map(([m]) => m);//get and unpack legal moves
    if (moves.length === 0) {
      // if no moves, you're donezo
      return maximizing ? -Infinity : +Infinity;
      //- inf = worst for black, pos inf = worst for red
    }
    if (maximizing) { //we are working with black here
      let value = -Infinity; //set initial val at lowest possible val
      for (const mv of moves) { //loop over black moves
        const child = simMove(board, mv); //sim the move to get new pos
        //recusrivly call func with depth-1, and set maximizing false bc red's turn
        //take max of val and score of recursive call to choose maxed score
        value = Math.max(value, minimax(child, depth-1, alpha, beta, false));
        alpha = Math.max(alpha, value); //Best score black can guarentee
        if (alpha >= beta) break;  //Red can force the score to at most beta, so red will never allow aplha>=beta,
        //so we do not need to look at further moves here, because they won't be able to beat that
      }
      return value;//return best score black can get
    } else {  //now do the same thing for red
      let value = +Infinity;
      for (const mv of moves) {
        const child = simMove(board, mv);
        value = Math.min(value, minimax(child, depth-1, alpha, beta, true));
        beta = Math.min(beta, value);
        if (alpha >= beta) break;
      }
      return value;
    }
  }



//return arr of legal moves for given player
function getLegalMoves(color) {
  //arr to store legal moves
  const moves = [];
  //moving up or down board?
  const direction = color === lightPiece ? -1 : 1;

  //loop thru pieces
  pieces.forEach((piece) => {
    if (piece.color !== color) return; //return for other p;layer peices
    // simple moves
    [-1, 1].forEach(diagonal => { //try L and R diagonals
      const x = piece.x + diagonal; //new col
      const y = piece.y + direction; //new row
      if ( //check if mvoe is valid
        x >= 0 && x < BOARD_SIZE && y >= 0 && y < BOARD_SIZE &&
        !getPiece(x, y) && isValidMove(piece, x, y)) {
            move = {piece, x, y};//gather the move
            capture_bool = is_capture(piece, x, y);//is it a capture?
            center_dist = get_dist_from_center(x, y);//how far from middle
            //add move, if it is a capture, and how far from center to arr
            moves.push([move, capture_bool, center_dist]); //add move to arr
      }
    });
    // jump moves for captures
    [-2, 2].forEach(jump => {
      const x = piece.x + jump;
      const y = piece.y + 2 * direction;
      if (
        x >= 0 && x < BOARD_SIZE && y >= 0 && y < BOARD_SIZE &&
        !getPiece(x, y) && isValidMove(piece, x, y)) {
            move = {piece, x, y}; //gather the move
            capture_bool = is_capture(piece, x, y);//is it a capture?
            center_dist = get_dist_from_center(x, y);//how far from middle
            moves.push([move, capture_bool, center_dist]);
      }
    });
  });

  return moves;
}

// Easy bot: pick a random legal move and play it
function easyBot(scene) {
  // get legal moves
  // check if game over
  // it not do a random legal move
  const legalMoves = getLegalMoves(darkPiece);
  // if No legal moves
  if (legalMoves.length === 0) {
    console.log('Cant move');
    return;
  }
  //get random move
  const [move] = Phaser.Utils.Array.GetRandom(legalMoves);
  //execute move
  movePiece(move.piece, move.x, move.y);
  // end bot's turn
  endTurn(scene);
}

//Easy bot: Prioritizes 1) Captures 2 central moves
function mediumBot(scene){
    const moves = getLegalMoves(COLORS.black);
    if (moves.length === 0){//no moves
        console.log('Cant move');
        return;
    }
    let [bestMove, capture, closestDist] = moves[0]; //init first move as best move
    for(const[move, c_bool, dist] of moves){ //loop through moves
        if (c_bool){
            bestMove = move;
            break; //whatever the first capture is we do it
        }
        if (!capture && dist < closestDist){ //if dist is closer to middle
            bestMove = move; //this is new best move
            closestDist = dist; //this is new closest dist
        }

    }   //end loop
    movePiece(bestMove.piece, bestMove.x, bestMove.y);
    endTurn(scene);
}

//Hard bot: thinks ahead and calculates best move
function hardBot(scene) {
    const board = getBoardState(); //get 2D board rep
    const legal = getLegalMoves(COLORS.black).map(([m]) => m); //get and unpack legals
    if (legal.length === 0) {
        return console.log('Cant move');}//no moves
    let best = legal[0]; //best is the best move
    let bestScore = -Infinity; //best score is the max minimix for black
    for (const move of legal) { //loop over black moves
      const child = simMove(board, move); //sim
        //call minimax to search pos child w depth 4, next move is red
        //returns score of the play
      const score = minimax(child, 4, -Infinity, +Infinity, false);
      if (score > bestScore) {
        bestScore = score;
        best = move;
      }
    }//end loop
    movePiece(best.piece, best.x, best.y);
    endTurn(scene);
  }

// function to enable or disable the coordinates overlay
function toggleCoordinateVisibility() {
  const toggleCoordinatesBtn = document.getElementById('toggle-coordinates');
  toggleCoordinatesBtn.classList.add('selected');
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
        left: `${(rect.left + margin) + (i * tile_size) + (tile_size / 2)}px`,
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
        top: `${rect.top + margin + i * tile_size + tile_size / 2}px`,
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
    toggleCoordinatesBtn.classList.remove('selected');
  }
}

// Coordinates overlay button
document.addEventListener('DOMContentLoaded', () => {
  const toggleCoordinatesBtn = document.getElementById('toggle-coordinates');

  toggleCoordinatesBtn.addEventListener('click', () => {
    toggleCoordinateVisibility();
  });
});

// Mute button + “M” key shortcut
document.addEventListener('DOMContentLoaded', () => {
  const toggleMuteBtn = document.getElementById('toggle-mute');

  // set initial label
  toggleMuteBtn.textContent = muted ? 'Unmute' : 'Mute';

  toggleMuteBtn.addEventListener('click', () => {
    // flip mute state first
    muted = !muted;
    checkers.sound.mute = muted;
    // then update the label
    toggleMuteBtn.textContent = muted ? 'Unmute' : 'Mute';
  });

  // listen for “m” or “M” anywhere
  document.addEventListener('keydown', (e) => {
    if (e.key.toLowerCase() === 'm') {
      // do exactly the same toggle logic:
      muted = !muted;
      checkers.sound.mute = muted;
      toggleMuteBtn.textContent = muted ? 'Unmute' : 'Mute';
    }
  });
});

// function to resize the board based on the given percentage
function resizeGame(percentage) {
  // Calculate new dimensions
  const newWidth = Math.floor(START_WIDTH * percentage);
  const newHeight = Math.floor(START_HEIGHT * percentage);

  // Update game configuration
  checkers.scale.resize(newWidth, newHeight);

  // Update margin and tile size and highlight size
  margin = START_MARGIN * percentage;
  tile_size = (newWidth - 2 * margin) / BOARD_SIZE;
  highlight_size = START_HIGHLIGHT_SIZE * percentage;

  // clear old highlighted tiles
  clearHighlightedTiles();

  // Update the positions of the tiles
  tiles.forEach((tile, index) => {
    const x = index % BOARD_SIZE;
    const y = Math.floor(index / BOARD_SIZE);
    tile.setPosition(
      margin + x * tile_size + tile_size / 2,
      margin + y * tile_size + tile_size / 2
    );
    tile.setSize(tile_size, tile_size);
  });

  // update the positions of the piece sprites
  pieces.forEach((piece) => {
    // destroy the old sprite
    piece.sprite.destroy();
    // create a new sprite with the updated position and size
    piece.sprite = checkers.scene.scenes[0].add.circle(
      margin + piece.x * tile_size + tile_size / 2,
      margin + piece.y * tile_size + tile_size / 2,
      tile_size / RADIUS_SCALE_FACTOR,
      piece.color
    ).setInteractive();

    if (piece.isKing) {
      // remove the old crown icon
      if (piece.kingIcon) {
        piece.kingIcon.destroy();
      }
      // create a new crown icon with the updated position and size
      piece.kingIcon = checkers.scene.scenes[0].add.image(
        margin + piece.x * tile_size + tile_size / 2,
        margin + piece.y * tile_size + tile_size / 2,
        'crown'
      );
      piece.kingIcon.setDisplaySize(tile_size, tile_size);
    }

    // add onclick functionality to the new sprite
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
        // highlight the current piece that is being selected and set them as
        // 'selectedPiece', highlighting the tiles the piece can move to
        selectedPiece = piece;
        piece.sprite.setStrokeStyle(highlight_size, COLORS.white);
        highlightValidMoves(checkers.scene.scenes[0], piece);
      }
    });

    // If this piece was selected, update the selectedPiece reference to the new sprite
    if (selectedPiece === piece) {
      selectedPiece.sprite = piece.sprite;
      piece.sprite.setStrokeStyle(highlight_size, COLORS.white);
      // redraw the highlighted tiles for valid moves with the new size
      highlightValidMoves(checkers.scene.scenes[0], piece);
    }

  });
  // redraw the highlighted tiles

  // if the coordinates are visible, update their size by redrawing them
  if (coordsVisible) {
    toggleCoordinateVisibility();
    toggleCoordinateVisibility();
  }
}

// Event listener for the resize slider
document.addEventListener('DOMContentLoaded', () => {
  const resizeSlider = document.getElementById('resize-slider');
  const resizeValue = document.getElementById('resize-value');

  resizeSlider.addEventListener('input', () => {
    const percent = parseInt(resizeSlider.value, 10);
    resizeValue.textContent = percent + '%';
    resizeGame(percent / 100);
  });
});

// functions for the timers
function startPlayerTimer() {
  // stop the current running timer
  stopPlayerTimer();

  // https://stackoverflow.com/questions/5978519/how-can-i-use-setinterval-and-clearinterval
  activeTimer = setInterval(() => {
    if (currentPlayer === lightPiece) {
      redTime--; // subtract 1 second from red's timer
      // Black wins if red runs out of time
      if (redTime <= 0) {
        endGameOnTimeout(darkPiece);
      }
    } else {
      blackTime--; // subtract 1 second from black's timer
      // Red wins if black runs out of time
      if (blackTime <= 0) {
        endGameOnTimeout(lightPiece);
      }
    }
    // update the time
    updateTimerDisplay();
  }, 1000); // function runs every 1000ms, aka 1 second
}

function stopPlayerTimer() {
  if (activeTimer) {
    // stop the currently running timer
    clearInterval(activeTimer);
    // reset timer ref to null
    activeTimer = null;
  }
}

function updateTimerDisplay() {
  // get the HTML elements
  const redDisplay = document.getElementById('red-timer');
  const blackDisplay = document.getElementById('black-timer');

  // change format to mm:ss
  // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/padStart
  const redMin = Math.floor(redTime / 60);
  const redSec = String(redTime % 60).padStart(2, '0');
  const blackMin = Math.floor(blackTime / 60);
  const blackSec = String(blackTime % 60).padStart(2, '0');

  // update the innerHTML
  redDisplay.textContent = `Red: ${redMin}:${redSec}`;
  blackDisplay.textContent = `Black: ${blackMin}:${blackSec}`;
}

function endGameOnTimeout(winnerColor) {
  stopPlayerTimer(); // stop the timer so that it doesn't go into the negatives
  gameOver = true;

  const message = document.getElementById('gameOverMessage');
  const gameOverPrompts = document.getElementById('gameOverPrompts');
  const winner = winnerColor === lightPiece ? 'Red' : 'Black';

  // Show message
  message.textContent = `${winner === 'Red' ? 'Black' : 'Red'} ran out of time! ${winner} wins!`;
  message.classList.add('show');
  gameOverPrompts.classList.add('show');

  // Show "play again" option
  document.getElementById('playAgainPrompt').style.display = 'block';
  document.getElementById('drawBtn').style.display = 'none';
  document.getElementById('forfeitBtn').style.display = 'none';
}
