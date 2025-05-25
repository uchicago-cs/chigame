const WORD_LENGTH = 5;
const ROWS = 6;

const socket = io();
let playerNum = null;
let word = "";
let guessedWords = [[]];
let availableSpace = 1;
let guessedWordCount = 0;
let opponentGuessedWordCount = 0;
let timerInterval = null;
let gameOver = false;
const url = "https://api.dictionaryapi.dev/api/v2/entries/en/";
const COLOR_CORRECT = "rgb(83, 141, 78)";
const COLOR_OFF = "rgb(181, 159, 59)";
const COLOR_WRONG = "rgb(40, 58, 60)";

/* ------------- Socket Setup ------------- */
socket.on('connect', () => {
    console.log('connected →', socket.id);
});

//Load player
socket.on('welcome', (data) => {
    playerNum = data.playerNum;

    window.addEventListener('DOMContentLoaded', () => {
        const playerHeader = document.querySelector(`#player${playerNum} h2`);
        if (playerHeader) {
            playerHeader.textContent = `Player ${playerNum} (you)`;
        }
    });
});

//Start Game
socket.on('startGame', ({ word: secret, startTime, duration }) => {
    console.log('Secret word is:', secret);
    word = secret.toLowerCase();
    startCountdownTimer(startTime, duration);
});

//Correct guess
socket.on('correctGuess', ({ newWord, score }) => {
    word = newWord.toLowerCase();
    guessedWords = [[]];
    guessedWordCount = 0;
    availableSpace = 1;
    gameOver = false;

    const scoreElement = document.getElementById(`player1-score`);
    if (scoreElement) {
        scoreElement.textContent = `Score: ${score}`;
    }

    console.log(`🎯 New word is: ${word}`);

    // Clear and reinitialize the board for player 1
    const board = document.getElementById('board-1');
    board.innerHTML = '';
    createSquares('board-1');

    const keys = document.querySelectorAll(".keyboard-row button");
    keys.forEach(key => {
        key.style.backgroundColor = "";
        key.style.borderColor = "";
        key.style.color = "";
    });

    showNotification("Correct! New word loaded.");
});

//Opponent Solving a Wordle
socket.on('opponentScored', ({ playerNum, score }) => {
    const board = document.getElementById('board-2');

    const scoreElement = document.getElementById(`player2-score`);
    if (scoreElement) {
        scoreElement.textContent = `Score: ${score}`;
    }
    //lear and reinitialize the board for opponent
    board.innerHTML = '';
    createSquares('board-2');
    showNotification(`Opponent guessed the word!`, 1500);
});

//Result from entering a guess
socket.on('wordResult', ({ valid, reason, word, correct, colorMap }) => {
    if (!valid) {
        showNotification(reason);
        return;
    }

    const firstLetterId = guessedWordCount * WORD_LENGTH;

    word.split("").forEach((letter, index) => {
        const tileColor = colorMap[index];

        const letterId = firstLetterId + index + 1;
        const letterEl = document.getElementById(letterId);
        letterEl.style = `background-color:${tileColor};border-color:${tileColor};color: white`;

        const keyButton = document.querySelector(`[data-key="${letter}"]`);
        if (keyButton) {

            // Only upgrade the key color (grey → yellow → green), never downgrade
            const currentKeyColor = keyButton.style.backgroundColor;

            if (currentKeyColor !== COLOR_CORRECT) {
                if (currentKeyColor !== COLOR_OFF || tileColor === COLOR_CORRECT) {
                    keyButton.style.backgroundColor = tileColor;
                    keyButton.style.borderColor = tileColor;
                    keyButton.style.color = "white"; //keep white no matter light or dark mode
                }
            }
        }
    });

    guessedWordCount++;
    guessedWords.push([]);

    if (correct) {
        showNotification("You Win! 🎉");
        gameOver = true;
        return;
    }

    if (guessedWordCount === ROWS) {
        showNotification("Game Over.");
        gameOver = true;
    }
});

//Displaying Opponents guesses
socket.on('opponentGuess', ({ colorMap }) => {
    const board = document.getElementById('board-2');

    const startIndex = Array.from(board.children).findIndex(
        (el) => !el.style.backgroundColor
    );

    for (let i = 0; i < colorMap.length; i++) {
        const tile = board.children[startIndex + i];
        const color = colorMap[i];
        tile.style.backgroundColor = color;
        tile.style.borderColor = color;
        tile.textContent = "";
    }
});

//Game Over
socket.on('gameOver', ({ reason }) => {
    clearInterval(timerInterval); // Stop the timer
    showNotification(`Game Over: ${reason}`);
    gameOver = true;

    const timerElement = document.querySelector('#header h1:nth-of-type(2)');
    timerElement.textContent = 'Game Over';
});



/* ------------- DOM Setup ------------- */
window.addEventListener('DOMContentLoaded', () => {
    createSquares('board-1');
    createSquares('board-2');
    setupKeyboard();
    handlePhysicalKeyboardInput();
});

/* ------------- Game Logic ------------- */

//Create Squares for board screen
function createSquares(boardId) {
    const board = document.getElementById(boardId);
    board.style.display = 'grid';
    board.style.gridTemplateColumns = `repeat(${WORD_LENGTH}, 1fr)`;
    board.style.gap = '6px';

    const totalTiles = WORD_LENGTH * ROWS;
    for (let index = 0; index < totalTiles; index++) {
        let square = document.createElement("div");
        square.classList.add("square");
        square.setAttribute("id", index + 1);
        board.appendChild(square);
    }
}

//Set up ingame keyboard
function setupKeyboard() {
    const keys = document.querySelectorAll(".keyboard-row button");
    for (let i = 0; i < keys.length; i++) {
        keys[i].onclick = ({ target }) => {
            const letter = target.getAttribute("data-key").toLowerCase();

            if (letter === "enter") {
                handleSubmitWord();
                return;
            }

            if (letter === "del") {
                handleDeleteLetter();
                return;
            }

            updateGuessedWords(letter);
        };
    }
}

//Set up physical keyboard
function handlePhysicalKeyboardInput() {
    document.addEventListener('keydown', (e) => {
        const key = e.key.toLowerCase();

        if (key === "enter") {
            handleSubmitWord();
            return;
        }

        if (key === "backspace") {
            handleDeleteLetter();
            return;
        }

        if (/^[a-z]$/.test(key)) {
            updateGuessedWords(key);
        }
    });
}

function getCurrentWordArr() {
    const numberOfGuessedWords = guessedWords.length;
    return guessedWords[numberOfGuessedWords - 1];
}

function updateGuessedWords(letter) {
    const currentWordArr = getCurrentWordArr();

    if (currentWordArr && currentWordArr.length < WORD_LENGTH) {
        currentWordArr.push(letter);

        const availableSpaceEl = document.getElementById(String(availableSpace));
        availableSpace = availableSpace + 1;
        availableSpaceEl.textContent = letter.toUpperCase();
    }
}

//Delete a letter
function handleDeleteLetter() {
    const currentWordArr = getCurrentWordArr();
    if (!currentWordArr.length) return;


    if (availableSpace > 1) {
        availableSpace -= 1;
    }

    currentWordArr.pop();

    const lastLetterEl = document.getElementById(String(availableSpace));
    lastLetterEl.textContent = "";
}

//Enter a guess
function handleSubmitWord() {
    if (gameOver) return;

    const currentWordArr = getCurrentWordArr();
    if (currentWordArr.length !== WORD_LENGTH) return;

    const currentWord = currentWordArr.join("").toLowerCase();
    socket.emit('submitWord', currentWord);
}

//Countdown timer linked with server.js
function startCountdownTimer(startTime, duration) {
    if (timerInterval) clearInterval(timerInterval);

    const timerElement = document.querySelector('#header h1:nth-of-type(2)');

    function update() {
        const now = Date.now();
        const elapsed = now - startTime;
        const remaining = Math.max(0, duration - elapsed);

        const minutes = Math.floor(remaining / 60000);
        const seconds = Math.floor((remaining % 60000) / 1000);
        timerElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;

        if (remaining <= 0) {
            clearInterval(timerInterval);
            showNotification("⏰ Time's up!");
            gameOver = true;
        }
    }

    update();
    timerInterval = setInterval(update, 1000);
}

//Show Notification
function showNotification(message, duration = 1000) {
    const notification = document.getElementById("notification");
    notification.textContent = message;

    notification.classList.add("show");

    setTimeout(() => {
        notification.classList.remove("show");
    }, duration);
}
