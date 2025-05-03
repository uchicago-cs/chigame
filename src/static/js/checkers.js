parent: 'game'

const config = {
  type: Phaser.AUTO,
  width: 640,
  height: 640,
  parent: 'game',
  scene: {
    preload,
    create,
    update,
  },
};

const game = new Phaser.Game(config);

// Constants
const margin = 10;
const BOARD_SIZE = 8;
const TILE_SIZE = (config.width - 2 * margin) / BOARD_SIZE;

const COLORS = {
  light_brown: 0xefbb74,
  dark_brown: 0x6b4415,
  red_piece: 0xff0000,
  black_piece: 0x000000,
};

let board = [];
let pieces = [];
let selectedPiece = null;
let currentPlayer = 'red';
let mustCapturePiece = null; // for multi-captures

// Init
function preload() { }

function create() {
  drawBoard(this);
  createPieces(this);

  this.input.on('pointerdown', (pointer) => {
    handleClick(this, pointer);
  });
}

function update() { }

function drawBoard(scene) {
  for (let y = 0; y < BOARD_SIZE; y++) {
    for (let x = 0; x < BOARD_SIZE; x++) {
      let tileColor = (x + y) % 2 === 0 ? COLORS.light_brown : COLORS.dark_brown;
      scene.add.rectangle(
        margin + x * TILE_SIZE + TILE_SIZE / 2,
        margin + y * TILE_SIZE + TILE_SIZE / 2,
        TILE_SIZE,
        TILE_SIZE,
        tileColor
      );
      board.push({ x, y });
    }
  }
}

function createPieces(scene) {
  for (let y = 0; y < BOARD_SIZE; y++) {
    for (let x = 0; x < BOARD_SIZE; x++) {
      if ((x + y) % 2 !== 0) { // Only dark squares
        if (y < 3) {
          createPiece(scene, x, y, 'black');
        } else if (y > 4) {
          createPiece(scene, x, y, 'red');
        }
      }
    }
  }
}

function createPiece(scene, x, y, color) {
  const piece = scene.add.circle(
    margin + x * TILE_SIZE + TILE_SIZE / 2,
    margin + y * TILE_SIZE + TILE_SIZE / 2,
    TILE_SIZE * 0.4,
    COLORS[color + '_piece']
  );
  piece.setData('color', color);
  piece.setData('boardX', x);
  piece.setData('boardY', y);
  piece.setData('king', false);
  pieces.push(piece);
}

function handleClick(scene, pointer) {
  const x = Math.floor((pointer.x - margin) / TILE_SIZE);
  const y = Math.floor((pointer.y - margin) / TILE_SIZE);

  if (x < 0 || x >= BOARD_SIZE || y < 0 || y >= BOARD_SIZE) return;

  if (selectedPiece) {
    movePiece(scene, x, y);
  } else {
    selectPiece(x, y);
  }
}

function selectPiece(x, y) {
  const piece = getPieceAt(x, y);
  if (piece && piece.getData('color') === currentPlayer) {
    if (mustCapturePiece && piece !== mustCapturePiece) return; // Must continue capture
    selectedPiece = piece;
    selectedPiece.setStrokeStyle(4, 0xffff00);
  }
}

function movePiece(scene, x, y) {
  if (isValidMove(selectedPiece, x, y)) {
    const dx = x - selectedPiece.getData('boardX');
    const dy = y - selectedPiece.getData('boardY');

    let wasCapture = false;

    // Check if it’s a capture move (2 steps)
    if (Math.abs(dx) === 2 && Math.abs(dy) === 2) {
      const midX = selectedPiece.getData('boardX') + dx / 2;
      const midY = selectedPiece.getData('boardY') + dy / 2;
      const captured = getPieceAt(midX, midY);
      if (captured) {
        captured.destroy();
        pieces = pieces.filter(p => p !== captured);
        wasCapture = true; // <-- mark that a capture happened
      }
    }

    selectedPiece.setPosition(
      margin + x * TILE_SIZE + TILE_SIZE / 2,
      margin + y * TILE_SIZE + TILE_SIZE / 2
    );
    selectedPiece.setData('boardX', x);
    selectedPiece.setData('boardY', y);

    // King the piece if reaching opposite side
    if ((selectedPiece.getData('color') === 'red' && y === 0) ||
      (selectedPiece.getData('color') === 'black' && y === 7)) {
      selectedPiece.setData('king', true);
    }

    if (wasCapture && canCapture(selectedPiece)) {
      // If captured and can capture again, allow player to move again
      mustCapturePiece = selectedPiece;
    } else {
      // Otherwise, switch turn
      mustCapturePiece = null;
      togglePlayer();
    }

    selectedPiece.setStrokeStyle();
    selectedPiece = null;
  } else {
    if (selectedPiece) {
      selectedPiece.setStrokeStyle();
      selectedPiece = null;
    }
  }
}


function isValidMove(piece, targetX, targetY) {
  const dx = targetX - piece.getData('boardX');
  const dy = targetY - piece.getData('boardY');

  const targetOccupied = getPieceAt(targetX, targetY);
  if (targetOccupied) return false;

  const absDx = Math.abs(dx);
  const absDy = Math.abs(dy);

  const forwardDir = piece.getData('color') === 'red' ? -1 : 1;

  if (piece.getData('king')) {
    // King can move both directions
    if (absDx === 1 && absDy === 1) return true;
    if (absDx === 2 && absDy === 2) {
      return enemyBetween(piece, targetX, targetY);
    }
  } else {
    // Normal piece
    if (absDx === 1 && dy === forwardDir) return true;
    if (absDx === 2 && dy === forwardDir * 2) {
      return enemyBetween(piece, targetX, targetY);
    }
  }

  return false;
}

function enemyBetween(piece, targetX, targetY) {
  const midX = (piece.getData('boardX') + targetX) / 2;
  const midY = (piece.getData('boardY') + targetY) / 2;
  const midPiece = getPieceAt(midX, midY);

  return midPiece && midPiece.getData('color') !== piece.getData('color');
}

function getPieceAt(x, y) {
  return pieces.find(p => p.getData('boardX') === x && p.getData('boardY') === y);
}

function togglePlayer() {
  currentPlayer = currentPlayer === 'red' ? 'black' : 'red';
}

function canCapture(piece) {
  const x = piece.getData('boardX');
  const y = piece.getData('boardY');
  const dirs = piece.getData('king')
    ? [[1, 1], [1, -1], [-1, 1], [-1, -1]]
    : (piece.getData('color') === 'red'
      ? [[1, -1], [-1, -1]]
      : [[1, 1], [-1, 1]]);

  for (let [dx, dy] of dirs) {
    const midX = x + dx;
    const midY = y + dy;
    const landX = x + dx * 2;
    const landY = y + dy * 2;

    if (landX >= 0 && landX < BOARD_SIZE && landY >= 0 && landY < BOARD_SIZE) {
      if (getPieceAt(landX, landY) === undefined) {
        const midPiece = getPieceAt(midX, midY);
        if (midPiece && midPiece.getData('color') !== piece.getData('color')) {
          return true;
        }
      }
    }
  }
  return false;
}
