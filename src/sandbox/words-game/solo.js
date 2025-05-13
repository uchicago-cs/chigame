//Set up game
document.addEventListener("DOMContentLoaded", async () => {
    await loadWords();
    createSquares();
    getNewWord();
    setupKeyboard();
    handlePhysicalKeyboardInput();
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
function loadWords() {
    return fetch('WORDS.txt')
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
    const today = new Date();
    const startDate = new Date('2025-05-03');
    const dayIndex = Math.floor((today - startDate) / (1000 * 60 * 60 * 24));
    const index = dayIndex % allowedWords.length;
    //New Different Word Everyday for 3000Days ie: all words in WORDS.txt is all used.
    word = allowedWords[index];
    console.log(word);

}

//Create boxes/grid for the board container
function createSquares() {
    const gameBoard = document.getElementById("board");

    for (let index = 0; index < 30; index++) {
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

//Returns current word you're ussing
function getCurrentWordArr() {
    const numberOfGuessedWords = guessedWords.length;
    return guessedWords[numberOfGuessedWords - 1];
}

//Checks if there is space and adds letter to current word
function updateGuessedWords(letter) {
    const currentWordArr = getCurrentWordArr();

    if (currentWordArr && currentWordArr.length < 5) {
        currentWordArr.push(letter);

        const availableSpaceEl = document.getElementById(String(availableSpace));
        availableSpace = availableSpace + 1;
        availableSpaceEl.textContent = letter.toUpperCase();
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

async function isValidWord(word) {
    const word_url = url + word;
    try {
        const response = await fetch(word_url);

        if (response.status === 404) {
            showNotification(`"${word}" Is Not a Valid Word.`);
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

    if (currentWordArr.length !== 5) {
        window.alert("Word must be 5 letters");
        return;
    }

    const currentWord = currentWordArr.join("").toLowerCase();

    const valid = await isValidWord(currentWord);
    if (!valid) {
        return;
    }

    const firstLetterId = guessedWordCount * 5 + 1;
    const interval = 200;

    //Adds the Keyboard color + effects
    currentWordArr.forEach((letter, index) => {
        setTimeout(() => {
            const tileColor = getTileColor(letter, index);

            const letterId = firstLetterId + index;
            const letterEl = document.getElementById(letterId);
            letterEl.classList.add("animate__flipInX");
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
        window.alert("Congratulations! 🎉");
        gameOver = true;
        return;
    }

    if (guessedWords.length === 6) {
        window.alert(`Sorry, you have no more guesses! The word was "${word}".`);
        gameOver = true;
        return;
    }

    guessedWords.push([]);
}
