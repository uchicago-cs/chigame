//Set up game
window.addEventListener("load", async () => {
    const modal = document.getElementById("word-length-modal");
    const selector = document.getElementById("word-length-selector");
    const startBtn = document.getElementById("start-game-btn");

    startBtn.addEventListener("click", async () => {
        wordLength = parseInt(selector.value);
        modal.style.display = "none";

        await loadWords();
        createSquares();
        getNewWord();
        setupKeyboard();
        handlePhysicalKeyboardInput();
    });
});


const howToPlayBtn = document.getElementById('how-to-play-btn');
const howToPlayText = document.getElementById('how-to-play-text');

//Opens and closes how to play text
howToPlayBtn.addEventListener('click', () => {
    howToPlayText.classList.toggle('visible');
    howToPlayText.classList.toggle('hidden');

    if (howToPlayText.classList.contains('visible')) {
        howToPlayBtn.textContent = "How to Play ▲";
    } else {
        howToPlayBtn.textContent = "How to Play ▼";
    }
});

let guessedWords = [[]];
let availableSpace = 1;
let word = "";
let guessedWordCount = 0;
let allowedWords = [];
let gameOver = false;
const url = "https://api.dictionaryapi.dev/api/v2/entries/en/";

//color constants
const COLOR_CORRECT = "rgb(83, 141, 78)";
const COLOR_OFF = "rgb(181, 159, 59)";
const COLOR_WRONG = "rgb(40, 58, 60)";


//Loads the words from WORDS.txt to the game
function loadWords() {    return fetch(`${wordLength}WORDS.txt`)
        .then(response => response.text())
        .then(text => {
            allowedWords = text.split('\n').map(w => w.trim().toLowerCase());
        })
        .catch(err => {
            console.error('Failed to load words file:', err);
        });
}

//Get a new word to solve
function getNewWord() {
    if (mode === 'game') {
        word = allowedWords[Math.floor(Math.random() * allowedWords.length)];
        console.log(`Today's Word: ${word}`);
    } else if (mode === 'solo') {
        const today = new Date();
        const startDate = new Date('2025-05-03');
        const dayIndex = Math.floor((today - startDate) / (1000 * 60 * 60 * 24));
        const index = dayIndex % allowedWords.length;
        word = allowedWords[index];
        console.log(`Today's Word: ${word}`);
    } else {
        console.error("Unrecognized game mode:", mode);
    }
}

//Create boxes/grid for the board container
function createSquares() {
    const gameBoard = document.getElementById("board");

    //set size based on word-legnth
    gameBoard.style.display = "grid";
    gameBoard.style.gridTemplateColumns = `repeat(${wordLength}, 1fr)`;
    gameBoard.style.gap = "5px";
    const totalTiles = wordLength * 6;
    for (let index = 0; index < totalTiles; index++) {
        let square = document.createElement("div");
        square.classList.add("square");
        square.classList.add("animate__animated");
        square.setAttribute("id", index + 1);
        gameBoard.appendChild(square);
    }

}

//Sends key to board when pressed on the screen
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

//Sends key to board when pressed on your physical keyboard
function handlePhysicalKeyboardInput() {
    document.addEventListener('keydown', (e) => {
        playSound(clickSound);
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

//Returns current word you're using
function getCurrentWordArr() {
    const numberOfGuessedWords = guessedWords.length;
    return guessedWords[numberOfGuessedWords - 1];
}

//Checks if there is space and adds letter to current word
function updateGuessedWords(letter) {
    const currentWordArr = getCurrentWordArr();

    if (currentWordArr && currentWordArr.length < wordLength) {
        currentWordArr.push(letter);

        const availableSpaceEl = document.getElementById(String(availableSpace));
        availableSpace = availableSpace + 1;
        availableSpaceEl.textContent = letter.toUpperCase();
        availableSpaceEl.classList.add("pop-in");
        setTimeout(() => availableSpaceEl.classList.remove("pop-in"), 200);
    }
}

//Deletes one letter from current word
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

//Get tile colors for each letter of the solutionWord
function getTileColor(letter, index) {
    const isCorrectLetter = word.includes(letter);

    if (!isCorrectLetter) {
        return COLOR_WRONG;
    }

    const letterInThatPosition = word.charAt(index);
    const isCorrectPosition = letter === letterInThatPosition;

    if (isCorrectPosition) {
        return COLOR_CORRECT;
    }

    return COLOR_OFF;
}

//Check if Word is a Valid Word
async function isValidWord(word) {
    const word_url = url + word;
    try {
        const response = await fetch(word_url);

        if (response.status === 404) {
            showNotification(`"${word}" Is Not A Valid Word.`);
            shakeRow(guessedWordCount);
            return false;
        }

        const json = await response.json();
        console.log("Dictionary API response:", json);
        return true;
    } catch (error) {
        console.error("Error checking word:", error.message);
        return false;
    }
}

//Handles running the submission of each word
async function handleSubmitWord() {
    if (gameOver) {
        return;
    }
    const currentWordArr = getCurrentWordArr();

    if (currentWordArr.length !== wordLength) {
        showNotification(`Word must be ${wordLength} letters`);
        shakeRow(guessedWordCount);
        return;
    }

    const currentWord = currentWordArr.join("").toLowerCase();

    const valid = await isValidWord(currentWord);
    if (!valid) {
        return;
    }

    const firstLetterId = guessedWordCount * wordLength + 1;
    const interval = 200;

    //Adds the Keyboard color + effects
    currentWordArr.forEach((letter, index) => {
        setTimeout(() => {
            const tileColor = getTileColor(letter, index);

            const letterId = firstLetterId + index;
            const letterEl = document.getElementById(letterId);
            letterEl.style = `background-color:${tileColor};border-color:${tileColor}`;

            //change on-web keyboard color
            const keyButton = document.querySelector(`[data-key="${letter}"]`);
            console.log('Key color:', keyButton);
            if (keyButton) {
                const keyColor = keyButton.style.backgroundColor;

                if (keyColor !== COLOR_CORRECT) {
                    keyButton.style.backgroundColor = tileColor;
                    keyButton.style.borderColor = tileColor;
                }
            }
        }, interval * index);
    });

    guessedWordCount += 1;

    //game end
    if (currentWord === word) {
        showNotification("Congratulations! 🎉");
        playSound(yaySound);
        gameOver = true;
        setTimeout(() => {
            showEndScreen(true);
        }, 1500);
        return;
    }


    if (guessedWords.length === 6) {
        showNotification(`Sorry, you have no more guesses! The word was "${word}".`);
        playSound(loseSound);
        gameOver = true;
        setTimeout(() => {
            showEndScreen(false);
        }, 1500);
        return;
    }

    guessedWords.push([]);
}

//Show Notification
function showNotification(message, duration = 1000) {
    const notification = document.getElementById("notification");
    notification.textContent = message;
    notification.classList.add("show");

    setTimeout(() => {
        notification.classList.remove("show");
        notification.classList.add("hidden");
    }, duration);
}

//Show EndScreen
function showEndScreen(won) {
    const endScreen = document.getElementById("end-screen");
    const endTitle = document.getElementById("end-title");
    const endMessage = document.getElementById("end-message");
    const endGuesses = document.getElementById("end-guesses");

    endScreen.classList.remove("hidden");
    endScreen.classList.add("visible");

    endTitle.textContent = won ? "You Won! 🎉" : "Game Over";
    endMessage.textContent = won ? "Nice job!" : `The word was "${word}"`;

    endGuesses.innerHTML = "";
    guessedWords.forEach(guessArr => {
        const row = document.createElement("div");
        row.textContent = guessArr.join("").toUpperCase();
        endGuesses.appendChild(row);
    });

    endScreen.classList.remove("hidden");
}

//Restart button in EndScreen
document.getElementById("restart-btn").addEventListener("click", () => {
    location.reload();
});

//Animation for shaking the row
function shakeRow(rowIndex) {
    for (let i = 0; i < wordLength; i++) {
        const tile = document.getElementById(rowIndex * wordLength + i + 1);
        tile.classList.add("shake");
        setTimeout(() => tile.classList.remove("shake"), 500);
    }
}

//Settings
document.getElementById("settings-btn").addEventListener("click", toggleSettings);
//Show Setting Screen
function toggleSettings() {
    const settingsScreen = document.getElementById("settings");
    settingsScreen.classList.toggle("hidden");
}

//Dark Mode
document.getElementById("dark-mode-toggle").addEventListener("change", function () {
    document.body.classList.toggle("dark-mode", this.checked);
});

//Color Blind Mode
document.getElementById("colorblind-toggle").addEventListener("change", function () {
    document.body.classList.toggle("colorblind-mode", this.checked);
});

//Sound Controls
const muteToggle = document.getElementById("mute-toggle");
const volumeSlider = document.getElementById("volume");
const yaySound = new Audio('sound/yay.mp3');
const loseSound = new Audio('sound/lose.mp3');
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
