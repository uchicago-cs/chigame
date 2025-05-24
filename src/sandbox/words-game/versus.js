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
socket.on('wordResult', ({ valid, reason, word, colorMap }) => {
    if (!valid) {
        showNotification("Invalid Word");
        shakeRow(guessedWordCount);
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

    if (guessedWordCount === ROWS) {
        showNotification("Game Over.");
        gameOver = true;
        socket.emit('lose', word);

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
socket.on('gameOver', ({ reason, win }) => {
    clearInterval(timerInterval);
    showNotification(`Game Over: ${reason}`);
    gameOver = true;

    let message = `Game Over: ${reason}`;
    if (win === true) {
        message += "You Win!";
        showEndScreen(true);   // You won
        playSound(yaySound);
    } else if (win === false) {
        message += "You Lose";
        showEndScreen(false);  // You lost
        playSound(loseSound);
    } else {
        message += "It's a draw!";
        showEndScreen(null);   // Draw
        playSound(drawSound);
    }

    showNotification(message);

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
        square.classList.add("animate__animated");
        square.setAttribute("id", index + 1);
        board.appendChild(square);
    }
}

//Set up ingame keyboard
function setupKeyboard() {
    const keys = document.querySelectorAll(".keyboard-row button");
    for (let i = 0; i < keys.length; i++) {
        keys[i].onclick = ({ target }) => {
            playSound(clickSound);
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
        playSound(clickSound);

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
        availableSpaceEl.classList.add("pop-in");
        setTimeout(() => availableSpaceEl.classList.remove("pop-in"), 200);
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
    if (lastLetterEl) {
        lastLetterEl.classList.add("pop-out");
        setTimeout(() => {
            lastLetterEl.classList.remove("pop-out");
        }, 150);
        lastLetterEl.textContent = "";
    }
}

//Enter a guess
function handleSubmitWord() {
    if (gameOver) return;

    const currentWordArr = getCurrentWordArr();
    if (currentWordArr.length !== WORD_LENGTH) {
        showNotification(`Word must be ${WORD_LENGTH} letters`);
        shakeRow(guessedWordCount);
        return;
    }

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
            showNotification("Time's up!");
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

const settingsBtn = document.getElementById('settings-btn');
const settingsScreen = document.getElementById('settings');

// Handle Settings toggle
settingsBtn.addEventListener('click', () => {

    settingsScreen.classList.toggle('hidden');
});


document.getElementById("dark-mode-toggle").addEventListener("change", function () {
    document.body.classList.toggle("dark-mode", this.checked);
});

document.getElementById("colorblind-toggle").addEventListener("change", function () {
    document.body.classList.toggle("colorblind-mode", this.checked);
});

//Sound
const muteToggle = document.getElementById("mute-toggle");
const volumeSlider = document.getElementById("volume");
const yaySound = new Audio('sound/yay.mp3');
const loseSound = new Audio('sound/lose.mp3');
const drawSound = new Audio('sound/draw.mp3');

const clickSound = new Audio('sound/click.mp3');

yaySound.volume = volumeSlider.value / 100;
loseSound.volume = volumeSlider.value / 100;
clickSound.volume = volumeSlider.value / 100;

function setVolume(volume) {
    yaySound.volume = volume;
    loseSound.volume = volume;
    clickSound.volume = volume
}

function playSound(audio) {
    if (!muteToggle.checked) {
        audio.currentTime = 0;
        audio.play();
    }
}

volumeSlider.addEventListener("input", function () {
    const volume = this.value / 100;
    setVolume(volume);
    console.log("Volume set to:", volume);
});

//End Screen
function showEndScreen(won) {
    const endScreen = document.getElementById("end-screen");
    const endTitle = document.getElementById("end-title");
    const endMessage = document.getElementById("end-message");

    endScreen.classList.remove("hidden");
    endScreen.classList.add("visible");

    if (won === true) {
        endTitle.textContent = "You Won!";
        endMessage.textContent = "Nice job!";
    } else if (won === false) {
        endTitle.textContent = "You Lost";
        endMessage.textContent = "You tried your best";
    } else {
        endTitle.textContent = "It's a Draw!";
        endMessage.textContent = "try winning next time";
    }

    setTimeout(() => {
        endScreen.classList.remove("visible");
        endScreen.classList.add("hidden");
    }, 10000);
}

function shakeRow(rowIndex) {
    for (let i = 0; i < WORD_LENGTH; i++) {
        const tile = document.getElementById(rowIndex * WORD_LENGTH + i + 1);
        tile.classList.add("shake");
        setTimeout(() => tile.classList.remove("shake"), 500);
    }
}
