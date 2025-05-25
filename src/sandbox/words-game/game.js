window.addEventListener("load", async () => {
    const modal = document.getElementById("word-length-modal");
    const selector = document.getElementById("word-length-selector");
    const startBtn = document.getElementById("start-game-btn");
    const modalContent = document.querySelector('.modal-content');
    const overlay = document.getElementById('menu-overlay');

    //restore settings
    restoreSettings();

    // Show the overlay on load for the word length modal - make it immediately visible
    overlay.classList.add('visible');
    overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';

    // Force a reflow to ensure the background change is applied immediately
    overlay.offsetHeight;

    // Stop propagation on modal content to prevent clicks from closing it
    if (modalContent) {
        modalContent.addEventListener('click', (event) => {
            event.stopPropagation();
        });

        // Set initial state for animation
        modalContent.style.transform = 'scale(0.95)';
        modalContent.style.opacity = '0';
    }

    // Ensure modal content shows with animation - with a small delay
    setTimeout(() => {
        if (modal.classList.contains('visible')) {
            modal.style.opacity = '1';
            if (modalContent) {
                modalContent.style.opacity = '1';
                modalContent.style.transform = 'scale(1)';
            }
        }
    }, ANIMATION_DELAY);

    startBtn.addEventListener("click", async () => {
        if(restoreGameState() && !changeLengthToggle){
            return;
        }
        // Reset game state if we're changing length in the middle of a game
        // Reset game state
        const key = mode === 'solo' ? 'soloGameState' : 'dailyGameState';
        localStorage.removeItem(key);
        guessedWords = [[]];
        greenLetters = {};
        yellowLetters = new Set();
        availableSpace = 1;
        guessedWordCount = 0;
        gameOver = false;
        gameWon = false;

        // Clear the keyboard colors
        const keys = document.querySelectorAll(".keyboard-row button");
        keys.forEach(key => {
            key.style.backgroundColor = "";
            key.style.color = "";
        });

        // Clear the board
        const gameBoard = document.getElementById("board");
        gameBoard.innerHTML = "";

        wordLength = parseInt(selector.value);

        // Close with animation
        closeModal(modal);

        await loadWords();
        createSquares();
        getNewWord();
        setupKeyboard();
        changeLengthToggle = false;
    });

    //if there is a current game state then we should restore it on reload
    if(restoreGameState()){
        closeModal(modal);

        //re set up board
        await loadWords();
        createSquares();
        setupKeyboard();

        // render guessed letters
        guessedWords.forEach((wordArr, rowIndex) => {
            const colors = calculateTileColors(wordArr, word);
            wordArr.forEach((letter, letterIndex) => {
                const index = rowIndex * wordLength + letterIndex + 1;
                const square = document.getElementById(index);
                const tileColor = colors[letterIndex];
                square.textContent = letter.toUpperCase();
                square.style.backgroundColor = tileColor;
                square.style.borderColor = tileColor;
                square.style.color = "white";

                const keyButton = document.querySelector(`[data-key="${letter}"]`);
                if (keyButton && keyButton.style.backgroundColor !== COLOR_CORRECT) {
                    if (keyButton.style.backgroundColor !== COLOR_OFF || tileColor === COLOR_CORRECT) {
                        keyButton.style.backgroundColor = tileColor;
                        keyButton.style.borderColor = tileColor;
                        keyButton.style.color = "white";
                    }
                }
            });
        });
        //handle game state saved at end of game
        if(gameOver){
            showEndScreen(gameWon);
        }
    }

    // Attach the single physical keyboard handler once after DOM is loaded
    document.addEventListener('keydown', gameKeyDownHandler);
});

//Buttons (How To Play and Settings)!
const howToPlayBtn = document.getElementById('how-to-play-btn');
const howToPlayText = document.getElementById('how-to-play-text');
const settingsBtn = document.getElementById('settings-btn');
const settingsScreen = document.getElementById('settings');
const changeLengthBtn = document.getElementById('change-length-btn'); // Get reference to existing button in HTML

// Single event handler for physical keyboard input
function gameKeyDownHandler(e) {
    const modal = document.getElementById("word-length-modal");
    // Check if modal is visible
    if (modal.classList.contains('visible')) {
        if (e.key === "Enter") {
            // Allow Enter to submit the modal
            document.getElementById("start-game-btn").click();
        }
        return; // Stop processing game keys if modal is open
    }

    const key = e.key.toLowerCase();

    // Only play sound for valid game interaction keys
    if (key === "enter" || key === "backspace" || /^[a-z]$/.test(key)) {
        playSound(clickSound);
    }

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
}

// Animation timing constants - used to ensure consistency
const ANIMATION_DURATION = 400; // Match with CSS transition time (in ms)
const ANIMATION_DELAY = 50; // Small delay to ensure animations start properly

// Function to reset element state for proper animation start
function resetElementForAnimation(element) {
    // Force a reflow to ensure styles are applied before animation starts
    element.style.opacity = '0';
    element.style.transform = 'translate(-50%, -50%) scale(0.95)';
    element.offsetHeight; // Trigger reflow
}

// Function to open modal with animation
function openModal(modal) {
    // Show the overlay first, before any other operations
    const overlay = document.getElementById('menu-overlay');
    overlay.classList.add('visible');
    overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.7)'; // Force immediate darkening

    // Force a reflow to ensure the background change is applied first
    overlay.offsetHeight;

    // First make the modal visible but transparent
    modal.classList.add('visible');

    // Force reflow
    modal.offsetHeight;

    // Set modal to full opacity
    modal.style.opacity = '1';

    // Make sure the content animates in with the same timing
    const content = modal.querySelector('.modal-content');
    if (content) {
        // Ensure the content is in its initial state (this might be redundant but ensures consistency)
        if (content.style.transform !== 'scale(0.95)' || content.style.opacity !== '0') {
            content.style.transform = 'scale(0.95)';
            content.style.opacity = '0';
            // Force reflow to ensure animation starts from initial state
            content.offsetHeight;
        }

        // Use requestAnimationFrame to ensure the browser has processed the initial state
        requestAnimationFrame(() => {
            // Animate to full scale and opacity
            content.style.opacity = '1';
            content.style.transform = 'scale(1)';
        });
    }
}

// Function to close modal with animation
function closeModal(modal) {
    // Fade out the overlay immediately if no other menu is open
    if (!howToPlayText.classList.contains('visible') &&
        !settingsScreen.classList.contains('visible')) {
        const overlay = document.getElementById('menu-overlay');
        overlay.style.backgroundColor = 'rgba(0, 0, 0, 0)';
    }

    // Set opacity to 0 on the modal
    modal.style.opacity = '0';

    // Scale down the content
    const content = modal.querySelector('.modal-content');
    if (content) {
        content.style.transform = 'scale(0.95)';
        content.style.opacity = '0';
    }

    // Create a specific handler for the transition end
    const handleTransitionEnd = function() {
        // Remove visibility class after animation completes
        modal.classList.remove('visible');
        modal.style.opacity = ''; // Reset for next time

        // Reset content transform
        if (content) {
            content.style.transform = '';
            content.style.opacity = '';
        }

        // Only fully remove the overlay when the modal transition completes
        // and if no other menu is open
        if (!howToPlayText.classList.contains('visible') &&
            !settingsScreen.classList.contains('visible')) {
            // Just remove the visibility class, the fade out already started
            const overlay = document.getElementById('menu-overlay');
            setTimeout(() => {
                overlay.classList.remove('visible');
                overlay.style.backgroundColor = '';
            }, 50); // Small delay to ensure it's synchronized
        }

        // Remove the event listener
        modal.removeEventListener('transitionend', handleTransitionEnd);
    };

    // Listen for the transition to complete
    modal.addEventListener('transitionend', handleTransitionEnd);

    // Fallback in case transition event doesn't fire
    setTimeout(() => {
        if (modal.classList.contains('visible')) {
            modal.classList.remove('visible');
            modal.style.opacity = ''; // Reset for next time

            // Reset content transform
            if (content) {
                content.style.transform = '';
                content.style.opacity = '';
            }

            // Only fully remove the overlay if no other menu is open
            if (!howToPlayText.classList.contains('visible') &&
                !settingsScreen.classList.contains('visible')) {
                const overlay = document.getElementById('menu-overlay');
                overlay.classList.remove('visible');
                overlay.style.backgroundColor = '';
            }
        }
    }, ANIMATION_DURATION + 50); // Slightly longer than transition time to be safe
}

// Handle Change Length button
changeLengthBtn.addEventListener('click', (event) => {
    changeLengthToggle = true;
    // Stop propagation to prevent document click from closing the modal
    event.stopPropagation();

    const modal = document.getElementById("word-length-modal");
    const selector = document.getElementById("word-length-selector");
    const modalContent = modal.querySelector('.modal-content');

    // Set the current word length in the selector
    selector.value = wordLength ? wordLength.toString() : "5"; // Ensure wordLength exists or default

    // Reset the modal content to its initial state before animating
    if (modalContent) {
        modalContent.style.transform = 'scale(0.95)';
        modalContent.style.opacity = '0';

        // Force reflow to ensure styles are applied
        modalContent.offsetHeight;
    }

    // Open with animation
    openModal(modal);

    if (settingsScreen.classList.contains('visible')) {
        animateClose(settingsScreen);
    }

    if (howToPlayText.classList.contains('visible')) {
        animateClose(howToPlayText);
        howToPlayBtn.textContent = "How to Play";
    }
});

// Close the modal when clicking outside of it
window.addEventListener('click', (event) => {
    const modal = document.getElementById("word-length-modal");
    const gameBoard = document.getElementById("board");

    // Check if the click is on the modal overlay itself, not its content
    // Also check if the game has been initialized (board has children)
    if (event.target === modal && modal.classList.contains('visible')) {
        // Only allow closing by clicking outside if the game board has been created
        if (gameBoard && gameBoard.children.length > 0) {
            closeModal(modal);
        } else {
            // Optionally show a notification that they need to select a length first
            showNotification("Please select a word length first", 1500);
        }
    }
});

// Handle How to Play toggle
howToPlayBtn.addEventListener('click', (event) => {
    // Stop propagation to prevent document click from immediately closing the menu
    event.stopPropagation();

    const isVisible = !howToPlayText.classList.contains('visible');
    const overlay = document.getElementById('menu-overlay');

    if (isVisible) {
        // Show overlay first, before any other operations
        overlay.classList.add('visible');
        overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.7)'; // Force immediate darkening

        // Force a reflow to ensure the background change is applied first
        overlay.offsetHeight;

        // Open animation
        resetElementForAnimation(howToPlayText);
        howToPlayText.classList.add('visible');

        // Need to do this in next frame to ensure animation works
        requestAnimationFrame(() => {
            howToPlayText.style.opacity = '1';
            howToPlayText.style.transform = 'translate(-50%, -50%) scale(1)';
        });

        //Hide settings
        if (settingsScreen.classList.contains('visible')) {
            animateClose(settingsScreen);
        }

        howToPlayBtn.textContent = "How to Play";
    } else {
        // Close animation - start fading overlay immediately
        if (!settingsScreen.classList.contains('visible') &&
            !document.getElementById('word-length-modal').classList.contains('visible')) {
            overlay.style.backgroundColor = 'rgba(0, 0, 0, 0)';
        }

        animateClose(howToPlayText);
        howToPlayBtn.textContent = "How to Play";
    }
});

// Handle Settings toggle
settingsBtn.addEventListener('click', (event) => {
    // Stop propagation to prevent document click from immediately closing the menu
    event.stopPropagation();

    const isVisible = !settingsScreen.classList.contains('visible');
    const overlay = document.getElementById('menu-overlay');

    if (isVisible) {
        // Show overlay first, before any other operations
        overlay.classList.add('visible');
        overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.7)'; // Force immediate darkening

        // Force a reflow to ensure the background change is applied first
        overlay.offsetHeight;

        // Open animation
        resetElementForAnimation(settingsScreen);
        settingsScreen.classList.add('visible');

        // Need to do this in next frame to ensure animation works
        requestAnimationFrame(() => {
            settingsScreen.style.opacity = '1';
            settingsScreen.style.transform = 'translate(-50%, -50%) scale(1)';
        });

        // Hide How to Play
        if (howToPlayText.classList.contains('visible')) {
            animateClose(howToPlayText);
        }

        howToPlayBtn.textContent = "How to Play";
    } else {
        // Close animation - start fading overlay immediately
        if (!howToPlayText.classList.contains('visible') &&
            !document.getElementById('word-length-modal').classList.contains('visible')) {
            overlay.style.backgroundColor = 'rgba(0, 0, 0, 0)';
        }

        animateClose(settingsScreen);
    }
});

// Also add stopPropagation to both menus to prevent clicks inside them from closing them
howToPlayText.addEventListener('click', (event) => {
    event.stopPropagation();
});

settingsScreen.addEventListener('click', (event) => {
    event.stopPropagation();
});

// Close How to Play and Settings when clicking outside them
document.addEventListener('click', (event) => {
    const overlay = document.getElementById('menu-overlay');

    // Close How to Play when clicking outside
    if (howToPlayText.classList.contains('visible') &&
        !howToPlayText.contains(event.target) &&
        event.target !== howToPlayBtn) {

        // Start fading the overlay immediately if this is the only open menu
        if (!settingsScreen.classList.contains('visible') &&
            !document.getElementById('word-length-modal').classList.contains('visible')) {
            overlay.style.backgroundColor = 'rgba(0, 0, 0, 0)';
        }

        animateClose(howToPlayText);
        howToPlayBtn.textContent = "How to Play";
    }

    // Close Settings when clicking outside
    if (settingsScreen.classList.contains('visible') &&
        !settingsScreen.contains(event.target) &&
        event.target !== settingsBtn) {

        // Start fading the overlay immediately if this is the only open menu
        if (!howToPlayText.classList.contains('visible') &&
            !document.getElementById('word-length-modal').classList.contains('visible')) {
            overlay.style.backgroundColor = 'rgba(0, 0, 0, 0)';
        }

        animateClose(settingsScreen);
    }
});

let guessedWords = [[]];
let greenLetters = {};
let yellowLetters = new Set();
let availableSpace = 1;
let word = "";
let guessedWordCount = 0;
let allowedWords = [];
let gameOver = false;
let gameWon = false;
let changeLengthToggle = false;//boolean to check if modal was accessed by change length button. This alters how game state should respond.
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

//hashing function for daily word selection
function hashInt(x) {
  x = ((x >>> 16) ^ x) * 0x45d9f3b;
  x = ((x >>> 16) ^ x) * 0x45d9f3b;
  x = (x >>> 16) ^ x;
  return x >>> 0;
}

/*
Process for selecting daily word involves taking today's date as an integer (YYYYMMDD),
hashing it using the above function
*/
function getNewWord() {
    if (mode === 'solo') {
        word = allowedWords[Math.floor(Math.random() * allowedWords.length)];
        console.log(`Today's Word: ${word}`);
    } else if (mode === 'game') {
        const today = new Date();
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const day = String(today.getDate()).padStart(2, '0');
        const dayIndex = parseInt(`${year}${month}${day}`, 10);
        index = hashInt(dayIndex) % allowedWords.length;
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
        gameWon = true;
        saveGameState();
        setTimeout(() => {
            showEndScreen(true);
        }, 1500);
        return;
    }

    if (guessedWords.length === 6) {
        showNotification(`The word was "${word}"`);
        playSound(loseSound);
        gameOver = true;
        gameWon = false;
        saveGameState();
        setTimeout(() => {
            showEndScreen(false);
        }, 1500);
        return;
    }

    guessedWords.push([]);
    saveGameState();
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
    const key = mode === 'solo' ? 'soloGameState' : 'dailyGameState';
    localStorage.removeItem(key);
    location.reload();
});


function shakeRow(rowIndex) {
    for (let i = 0; i < wordLength; i++) {
        const tile = document.getElementById(rowIndex * wordLength + i + 1);
        tile.classList.add("shake");
        setTimeout(() => tile.classList.remove("shake"), 500);
    }
}

//Settings toggles
document.getElementById("dark-mode-toggle").addEventListener("change", function () {
    document.body.classList.toggle("dark-mode", this.checked);
    saveSettings();
});

document.getElementById("colorblind-toggle").addEventListener("change", function () {
    document.body.classList.toggle("colorblind-mode", this.checked);
    saveSettings();
});

document.getElementById("hard-mode-toggle").addEventListener("change", function () {
    document.body.classList.toggle("hard-mode", this.checked);
    saveSettings();
});

document.getElementById("mute-toggle").addEventListener("change", function () {
    saveSettings();
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

function saveGameState(){
    const gameState = {
        guessedWords,
        word,
        wordLength,
        guessedWordCount,
        availableSpace,
        greenLetters,
        yellowLetters: Array.from(yellowLetters),
        gameOver,
        gameWon
    };
    const key = mode === 'solo' ? 'soloGameState' : 'dailyGameState';
    localStorage.setItem(key, JSON.stringify(gameState));
}

function restoreGameState(){
    const key = mode === 'solo' ? 'soloGameState' : 'dailyGameState';
    const gameStateJSON = localStorage.getItem(key);
    if(!gameStateJSON){
        return false;
    }
    const parsedGS = JSON.parse(gameStateJSON);
    guessedWords = parsedGS.guessedWords;
    word = parsedGS.word;
    wordLength = parsedGS.wordLength;
    guessedWordCount = parsedGS.guessedWordCount;
    availableSpace = parsedGS.availableSpace;
    greenLetters = parsedGS.greenLetters;
    yellowLetters = new Set(parsedGS.yellowLetters)
    gameOver = parsedGS.gameOver;
    gameWon = parsedGS.gameWon ?? false;

    return true;
}

//Function to save visual and audio settings
function saveSettings(){
    const settings = {
        darkMode: document.getElementById("dark-mode-toggle").checked,
        colorblindMode: document.getElementById("colorblind-toggle").checked,
        hardMode: document.getElementById("hard-mode-toggle").checked,
        mute: document.getElementById("mute-toggle").checked
    };
    localStorage.setItem("gameSettings", JSON.stringify(settings));
}

//Function restores settings
function restoreSettings() {
    const saved = localStorage.getItem("gameSettings");
    if (!saved){
        return;
    }

    const settings = JSON.parse(saved);

    document.getElementById("dark-mode-toggle").checked = settings.darkMode;
    document.body.classList.toggle("dark-mode", settings.darkMode);

    document.getElementById("colorblind-toggle").checked = settings.colorblindMode;
    document.body.classList.toggle("colorblind-mode", settings.colorblindMode);

    document.getElementById("hard-mode-toggle").checked = settings.hardMode;
    document.body.classList.toggle("hard-mode", settings.hardMode);

    document.getElementById("mute-toggle").checked = settings.mute;

}

// Function to handle closing animation with a delay
function animateClose(element, onComplete = null) {
    // Ensure we trigger a reflow first to ensure animation starts from current state
    element.offsetHeight; // Force reflow

    // Start fading out overlay immediately if no other menu is open
    if (!howToPlayText.classList.contains('visible') &&
        !settingsScreen.classList.contains('visible') &&
        !document.getElementById('word-length-modal').classList.contains('visible') ||
        // Only count the current element as visible because we're about to close it
        (howToPlayText === element && !settingsScreen.classList.contains('visible') &&
        !document.getElementById('word-length-modal').classList.contains('visible')) ||
        (settingsScreen === element && !howToPlayText.classList.contains('visible') &&
        !document.getElementById('word-length-modal').classList.contains('visible'))) {

        // Start the overlay fade out now, to sync with menu closing
        const overlay = document.getElementById('menu-overlay');
        overlay.style.backgroundColor = 'rgba(0, 0, 0, 0)';
    }

    // Set closing styles for the menu
    element.style.opacity = '0';
    element.style.transform = 'translate(-50%, -50%) scale(0.95)';

    // Create a specific handler for the transition end
    const handleTransitionEnd = function() {
        // Remove visibility class after animation completes
        element.classList.remove('visible');

        // Only fully remove the overlay when the menu transition completes
        // and if no other menu is open
        if (!howToPlayText.classList.contains('visible') &&
            !settingsScreen.classList.contains('visible') &&
            !document.getElementById('word-length-modal').classList.contains('visible')) {

            // Just remove the visibility class, the fade out already started
            const overlay = document.getElementById('menu-overlay');
            setTimeout(() => {
                overlay.classList.remove('visible');
                overlay.style.backgroundColor = '';
            }, 50); // Small delay to ensure it's synchronized
        }

        // Run the callback if provided
        if (onComplete) onComplete();

        // Remove the event listener
        element.removeEventListener('transitionend', handleTransitionEnd);
    };

    // Listen for the transition to complete
    element.addEventListener('transitionend', handleTransitionEnd);

    // Fallback in case transition event doesn't fire
    setTimeout(() => {
        if (element.classList.contains('visible')) {
            element.classList.remove('visible');

            // Only fully remove the overlay if no other menu is open
            if (!howToPlayText.classList.contains('visible') &&
                !settingsScreen.classList.contains('visible') &&
                !document.getElementById('word-length-modal').classList.contains('visible')) {

                // Just remove the visibility class, the fade out already started
                const overlay = document.getElementById('menu-overlay');
                overlay.classList.remove('visible');
                overlay.style.backgroundColor = '';
            }

            if (onComplete) onComplete();
        }
    }, ANIMATION_DURATION + 50); // Slightly longer than transition time to be safe
}
