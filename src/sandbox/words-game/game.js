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

//Buttons (How To Play and Settings)!
const howToPlayBtn = document.getElementById('how-to-play-btn');
const howToPlayText = document.getElementById('how-to-play-text');
const settingsBtn = document.getElementById('settings-btn');
const settingsScreen = document.getElementById('settings');

// Handle How to Play toggle
howToPlayBtn.addEventListener('click', () => {
    const isVisible = !howToPlayText.classList.contains('visible');

    howToPlayText.classList.toggle('visible', isVisible);
    howToPlayText.classList.toggle('hidden', !isVisible);

    //Hide settings
    settingsScreen.classList.add('hidden');

    if (isVisible) {
    howToPlayBtn.textContent = "How to Play ▲";
    } else {
    howToPlayBtn.textContent = "How to Play ▼";
    }
});

// Handle Settings toggle
settingsBtn.addEventListener('click', () => {

    settingsScreen.classList.toggle('hidden');

    // Always hide How to Play
    howToPlayText.classList.remove('visible');
    howToPlayText.classList.add('hidden');
    howToPlayBtn.textContent = "How to Play ▼";
});
let guessedWords = [[]];
let greenLetters = {};
let yellowLetters = new Set();
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

function loadWords() {
    return fetch(`${wordLength}WORDS.txt`)
        .then(response => response.text())
        .then(text => {
            allowedWords = text.split('\n').map(w => w.trim().toLowerCase());
        })
        .catch(err => {
            console.error('Failed to load words file:', err);
        });
}

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

    if (currentWordArr && currentWordArr.length < wordLength) {
        currentWordArr.push(letter);

        const availableSpaceEl = document.getElementById(String(availableSpace));
        availableSpace = availableSpace + 1;
        availableSpaceEl.textContent = letter.toUpperCase();
        availableSpaceEl.classList.add("pop-in");
        setTimeout(() => availableSpaceEl.classList.remove("pop-in"), 200);
    }
}

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



//Checks if word is Valid
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

    //hard mode
    const hardToggle = document.getElementById("hard-mode-toggle");
    if (hardToggle.checked) {
        //check if all green letters are in the right position
        for (let index in greenLetters) {
            if (currentWordArr[parseInt(index)] !== greenLetters[index]) {
                showNotification(`Hard mode: Letter "${greenLetters[index].toUpperCase()}" must be in position ${parseInt(index) + 1}`);
                shakeRow(guessedWordCount);
                return;
            }
        }
        //check if all yellow letters in this guess
        for (let letter of yellowLetters) {
            if (!currentWordArr.includes(letter)) {
                showNotification(`Hard mode: Letter "${letter.toUpperCase()}" must be used`);
                shakeRow(guessedWordCount);
                return;
            }
        }
    }

    const firstLetterId = guessedWordCount * wordLength + 1;
    const interval = 200;

    // Calculate the colors using the Wordle algorithm
    const tileColors = calculateTileColors(currentWordArr, word);


    tileColors.forEach((color, index) => {//add letters to colors array for hard mode
        if (color === COLOR_CORRECT) {
            greenLetters[index] = currentWordArr[index];
        }
        if (color === COLOR_OFF) {
            yellowLetters.add(currentWordArr[index]);
        }
    });

    // Apply the colors to the UI
    currentWordArr.forEach((letter, index) => {
        setTimeout(() => {
            const tileColor = tileColors[index];

            const letterId = firstLetterId + index;
            const letterEl = document.getElementById(letterId);
            letterEl.style = `background-color:${tileColor};border-color:${tileColor};color: white`; //keep white no matter light or dark mode

            // Update keyboard colors
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
        }, interval * index);
    });

    guessedWordCount += 1;

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
        showNotification(`The word was "${word}"`);
        playSound(loseSound);
        gameOver = true;
        setTimeout(() => {
            showEndScreen(false);
        }, 1500);
        return;
    }

    guessedWords.push([]);
}

/**
 * Calculate tile colors using the standard Wordle algorithm
 * @param {string[]} guess - Array of guess letters
 * @param {string} target - Target word
 * @returns {string[]} - Array of color values for each letter
 */
function calculateTileColors(guess, target) {
    // Convert target to array for easier handling
    const targetArr = target.split('');
    const colors = Array(guess.length).fill(null);

    // Track which positions in target word are already matched (for green)
    const targetUsed = Array(targetArr.length).fill(false);

    // First pass: find all green matches
    for (let i = 0; i < guess.length; i++) {
        if (guess[i] === targetArr[i]) {
            colors[i] = COLOR_CORRECT; // Green
            targetUsed[i] = true;
        }
    }

    // Second pass: find yellow and grey matches
    for (let i = 0; i < guess.length; i++) {
        if (colors[i] !== null) continue; // Skip already matched positions

        // Look for an unused match in the target word
        let foundYellow = false;

        for (let j = 0; j < targetArr.length; j++) {
            if (!targetUsed[j] && guess[i] === targetArr[j]) {
                colors[i] = COLOR_OFF; // Yellow
                targetUsed[j] = true;
                foundYellow = true;
                break;
            }
        }

        // If no unused match found, it's grey
        if (!foundYellow) {
            colors[i] = COLOR_WRONG; // Grey
        }
    }

    return colors;
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

//End Screen
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

}
document.getElementById("restart-btn").addEventListener("click", () => {
    location.reload();
});


function shakeRow(rowIndex) {
    for (let i = 0; i < wordLength; i++) {
        const tile = document.getElementById(rowIndex * wordLength + i + 1);
        tile.classList.add("shake");
        setTimeout(() => tile.classList.remove("shake"), 500);
    }
}


document.getElementById("dark-mode-toggle").addEventListener("change", function () {
    document.body.classList.toggle("dark-mode", this.checked);
});

document.getElementById("colorblind-toggle").addEventListener("change", function () {
    document.body.classList.toggle("colorblind-mode", this.checked);
});

document.getElementById("hard-mode-toggle").addEventListener("change", function () {
    document.body.classList.toggle("hard-mode", this.checked);
});



//Sound
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
