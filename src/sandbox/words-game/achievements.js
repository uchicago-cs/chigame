export const ACHIEVEMENTS = [
  {
    name: "First Win",
    rarity: "Common",
    check: (game) => game.won,
  },
  {
    name: "One Week Streak",
    rarity: "Uncommon",
    check: (game) => game.streak >= 7,
  },
  {
    name: "One Month Streak",
    rarity: "Rare",
    check: (game) => game.streak >= 30,
  },
  {
    name: "One Year Streak",
    rarity: "Precious",
    check: (game) => game.streak >= 365,
  },
  {
    name: "Correct on the First Guess",
    rarity: "Precious",
    check: (game) => game.won && game.attempts === 1,
  },
  {
    name: "Clutch Guess",
    rarity: "Rare",
    check: (game) => game.won && game.attempts === 6,
  },
  {
    name: "Comeback",
    rarity: "Rare",
    check: (game) =>
      game.won && game.firstThreeGuesses.every(guess => countGreenTiles(guess) === 0),
  },
  {
    name: "Gambler",
    rarity: "Rare",
    check: (game) => game.sameFirstGuessForWeek === true,
  },
  {
    name: "Freeze",
    rarity: "Uncommon",
    check: (game) => game.timeTaken >= 3600,
  },
  {
    name: "Zero Green",
    rarity: "Rare",
    check: (game) =>
      game.won &&
      game.guessesBeforeWin.every(guess => countGreenTiles(guess) === 0),
  },
  {
    name: "Sixth Sense",
    rarity: "Rare",
    check: (game) => game.solvedInSixGuessStreak === 6,
  },
  {
    name: "One and Done",
    rarity: "Uncommon",
    check: (game) => game.totalGuessesToday === 1,
  },
  {
    name: "Blacked Out",
    rarity: "Uncommon",
    check: (game) =>
      !game.won &&
      game.totalCorrectLetters === 0 &&
      game.totalGreenTiles === 0,
  }
];

function countGreenTiles(guess) {
  if (!Array.isArray(guess)) return 0;
  return guess.reduce((count, letterObj) => {
    return count + (letterObj && letterObj.color === "green" ? 1 : 0);
  }, 0);
}
