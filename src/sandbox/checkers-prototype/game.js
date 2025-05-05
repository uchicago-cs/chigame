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

// 8x8 board
const margin = 10;
const BOARD_SIZE = 8;
/*
I made the canvas background color black. Therefore, by making the game board
smaller to account for the margin, it'll appear as if there's a black border.
*/
const TILE_SIZE = (config.width - 2 * margin) / BOARD_SIZE;

// colors we will use in this game
const COLORS = {
  light_brown: 0xefbb74,
  dark_brown: 0x6b4415,
  black: 0x000000,
};

// the init functions
function preload() {}

function create() {
  drawBoard(this);
}

function update() {}

// Draw the game board
function drawBoard(scene) {
    // loop over the entire game board (y is column, x is row)
  for (let y = 0; y < BOARD_SIZE; y++) {
    for (let x = 0; x < BOARD_SIZE; x++) {
      // setting tile colors: even tiles = light brown, odd tiles = dark brown
      let tile_color = (x + y) % 2 === 0 ? COLORS.light_brown : COLORS.dark_brown;

      // draw tiles
      scene.add.rectangle(
        // phaser actually positions shape based on the center, not top-left
        // margin + x returns the top-left location of each tile
        // tile size / 2 returns the center of the tile
        margin + x * TILE_SIZE + TILE_SIZE / 2, // x position
        margin + y * TILE_SIZE + TILE_SIZE / 2, // y position
        TILE_SIZE, // width
        TILE_SIZE, // height
        tile_color
      );
    }
  }
}
