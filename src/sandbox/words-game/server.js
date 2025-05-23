//Set UP
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');
const fs = require('fs');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

// static assets
app.use(express.static(path.join(__dirname, 'Words-Game')));

const words = fs.readFileSync('Words-Game/5WORDS.txt', 'utf8').split('\n').map(w => w.trim().toLowerCase());

let players = new Map(); // socket.id => { socket, word }
const DICTIONARY_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/";

let gameStartTime = null;
const GAME_DURATION_MS = 3 * 60 * 1000; // 3 minutes
const WORD_LENGTH = 5;
let gameTimeout = null;
let sharedWordSequence = [];
const MAX_WORDS = 100;

/* ------------- Sockets ------------- */

//Socket connections
io.on('connection', socket => {
    // Clean up disconnected sockets
    players.forEach((playerData, id) => {
        if (!playerData.socket.connected) {
            players.delete(id);
        }
    });

    //Limit player to 2
    if (players.size >= 2) {
        socket.emit('roomFull', 'Only 2 players allowed.');
        socket.disconnect(true);
        return;
    }

    const playerNum = players.size;
    players.set(socket.id, { socket, word: null, playerNum, score: 0 });
    console.log(`Player ${playerNum} connected: ${socket.id}`);
    socket.emit('welcome', { playerNum });


    //Start game when 2 players join
    if (players.size === 2) {
        console.log(`Both players connected.`);

        sharedWordSequence = generateWordSequence();

        gameStartTime = Date.now();
        players.forEach((playerData, id) => {
            playerData.wordIndex = 0;
            playerData.word = sharedWordSequence[0];

            playerData.socket.emit('startGame', {
                word: sharedWordSequence[0],
                startTime: gameStartTime,
                duration: GAME_DURATION_MS
            });
        });

        gameTimeout = setTimeout(() => {
            console.log("Game over due to timeout.");
            // Determine winner
            const playersArr = Array.from(players.values());
            if (playersArr.length === 2) {
                const [player1, player2] = playersArr;
                const result = player1.score > player2.score
                    ? [true, false] // player1 won
                    : player1.score < player2.score
                        ? [false, true] // player2 won
                        : [null, null]; // draw

                player1.socket.emit('gameOver', {
                    reason: "timeout",
                    win: result[0],
                });

                player2.socket.emit('gameOver', {
                    reason: "timeout",
                    win: result[1],
                });
            }
            players.clear();
            gameTimeout = null;
        }, GAME_DURATION_MS);
    }

    //Submit word for players
    socket.on('submitWord', async (submittedWord) => {
        const playerData = players.get(socket.id);

        if (!playerData.word) return;

        const isValid = await isValidWord(submittedWord);
        if (!isValid) {
            socket.emit('wordResult', {valid: false});
            return;
        }

        const isCorrect = submittedWord.toLowerCase() === playerData.word.toLowerCase();

        //Correct Word
        if (isCorrect) {
            playerData.score += 1;
            playerData.wordIndex++;

            const nextWord = sharedWordSequence[playerData.wordIndex];
            console.log(`Player ${playerNum} advanced to wordIndex ${playerData.wordIndex}: "${nextWord}"`);

            if (!nextWord) {
                socket.emit('gameOver', {
                    reason: "no more words",
                    win: true,
                });
                return;
            }

            playerData.word = nextWord;

            socket.emit('correctGuess', {
                newWord: nextWord,
                score: playerData.score
            });

            socket.broadcast.emit('opponentScored', {
                playerNum,
                score: playerData.score
            });

        } else {
            const colorMap = calculateTileColors(submittedWord.split(""), playerData.word);

            // Send feedback to the submitting player
            socket.emit('wordResult', {
                valid: true,
                word: submittedWord,
                colorMap
            });

            // 🔽 NEW: Send tile data to opponent
            socket.broadcast.emit('opponentGuess', {
                colorMap
            });

        }
    });

    socket.on('lose', (unsolvedWord) => {
        const losingPlayer = players.get(socket.id);

        if (!losingPlayer) return;
        console.log(`Player ${losingPlayer.playerNum} lost. Couldn't solve: ${unsolvedWord}`);

        // Get the other player
        const otherPlayerEntry = Array.from(players.entries()).find(([id, data]) => id !== socket.id);

        if (otherPlayerEntry) {
            const [opponentId, opponentData] = otherPlayerEntry;

            // Notify loser
            losingPlayer.socket.emit('gameOver', {
                reason: `You failed to solve the word "${unsolvedWord}"`,
                win: false
            });

            // Notify winner
            opponentData.socket.emit('gameOver', {
                reason: `Opponent failed to solve the word "${unsolvedWord}"`,
                win: true
            });
        }

        players.clear();
        if (gameTimeout) {
            clearTimeout(gameTimeout);
            gameTimeout = null;
        }
    });


    //Disconnection of socket
    socket.on('disconnect', () => {
        const playerData = players.get(socket.id);
        if (playerData) {
            console.log(`Player ${playerData.playerNum} disconnected`);
        }

        players.delete(socket.id);

        // If one player disconnects, stop the game
        if (gameTimeout) {
            clearTimeout(gameTimeout);
            gameTimeout = null;

            // Notify other player the game is over
            players.forEach(({ socket }) => {
                socket.emit('gameOver', {
                    reason: "opponent disconnected",
                    win: true,
                });
            });

            players.clear();
            console.log("Game ended due to player disconnect.");
        }
    });
});


/* ------------- Helper Functions ------------- */

//Word List for the game
function generateWordSequence() {
    const shuffled = [...words].sort(() => 0.5 - Math.random());
    return shuffled.slice(0, MAX_WORDS);
}

//Tile colors for board
function calculateTileColors(guessArr, correctWord) {
    const colors = Array(WORD_LENGTH).fill("grey");
    const correctLetters = correctWord.split("");
    const guess = [...guessArr];

    for (let i = 0; i < WORD_LENGTH; i++) {
        if (guess[i] === correctLetters[i]) {
            colors[i] = "green";
            correctLetters[i] = null;
        }
    }

    for (let i = 0; i < WORD_LENGTH; i++) {
        if (colors[i] === "grey" && correctLetters.includes(guess[i])) {
            colors[i] = "yellow";
            correctLetters[correctLetters.indexOf(guess[i])] = null;
        }
    }

    return colors;
}

//Check if word is valid
async function isValidWord(word) {
    try {
        const response = await fetch(DICTIONARY_URL + word);
        return response.status !== 404;
    } catch (err) {
        console.error("Error validating word:", err.message);
        return false;
    }
}

//Start/Host the Server
server.listen(3000, () =>
    console.log('Server running on http://localhost:3000')
);
