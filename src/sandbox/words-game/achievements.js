// Achievements data structure
const achievements = [
  {
      id: 'first_win',
      title: 'First Win',
      description: 'Win your first game',
      rarity: 'common',
      icon: '🏆'
  },
  {
      id: 'one_week_streak',
      title: 'One Week Streak',
      description: 'Play and win for 7 consecutive days',
      rarity: 'uncommon',
      icon: '📅'
  },
  {
      id: 'one_month_streak',
      title: 'One Month Streak',
      description: 'Play and win for 30 consecutive days',
      rarity: 'rare',
      icon: '🗓️'
  },
  {
      id: 'one_year_streak',
      title: 'One Year Streak',
      description: 'Play and win for 365 consecutive days',
      rarity: 'precious',
      icon: '🎖️'
  },
  {
      id: 'first_guess',
      title: 'First Try',
      description: 'Guess the word correctly on your first try',
      rarity: 'precious',
      icon: '🎯'
  },
  {
      id: 'clutch_guess',
      title: 'Clutch Guess',
      description: 'Win on your very last guess',
      rarity: 'rare',
      icon: '😅'
  },
  {
      id: 'comeback',
      title: 'Comeback',
      description: 'First three guesses have 0 correct letters but still win at the end',
      rarity: 'rare',
      icon: '🔄'
  },
  {
      id: 'gambler',
      title: 'Gambler',
      description: 'Use the same first guess for a whole week',
      rarity: 'rare',
      icon: '🎲'
  },
  {
      id: 'freeze',
      title: 'Freeze',
      description: 'Spend over an hour on one game',
      rarity: 'uncommon',
      icon: '❄️'
  },
  {
      id: 'zero_green',
      title: 'Zero Green',
      description: 'Win a game without ever getting a green tile until the final guess',
      rarity: 'rare',
      icon: '🟩'
  },
  {
      id: 'sixth_sense',
      title: 'Sixth Sense',
      description: 'Solve in exactly 6 guesses, 6 days in a row',
      rarity: 'rare',
      icon: '6️⃣'
  },
  {
      id: 'one_and_done',
      title: 'One and Done',
      description: 'Only make one total guess today — win or lose',
      rarity: 'uncommon',
      icon: '1️⃣'
  },
  {
      id: 'blacked_out',
      title: 'Blacked Out',
      description: 'Lose a game with only gray tiles',
      rarity: 'uncommon',
      icon: '⬛'
  }
];

// Achievement notification queue
const achievementQueue = [];
let isShowingAchievement = false;

// Load user achievements from localStorage
function loadUserAchievements() {
  try {
      const saved = localStorage.getItem("userAchievements");
      return saved ? JSON.parse(saved) : {};
  } catch (e) {
      console.error('Error loading achievements:', e);
      return {};
  }
}

// Save user achievements to localStorage
function saveUserAchievements(userAchievements) {
  try {
      localStorage.setItem("userAchievements", JSON.stringify(userAchievements));
  } catch (e) {
      console.error('Error saving achievements:', e);
  }
}

// Unlock an achievement
function unlockAchievement(achievementId) {
  const userAchievements = loadUserAchievements();

  // If achievement is not already unlocked
  if (!userAchievements[achievementId]) {
      userAchievements[achievementId] = {
          unlocked: true,
          date: new Date().toISOString()
      };

      saveUserAchievements(userAchievements);

      // Add achievement to notification queue
      const achievement = achievements.find(a => a.id === achievementId);
      if (achievement) {
          queueAchievementNotification(achievement);
      }
  }
}

// Queue an achievement notification
function queueAchievementNotification(achievement) {
  achievementQueue.push(achievement);
  processAchievementQueue();
}

// Process the achievement notification queue
function processAchievementQueue() {
  if (isShowingAchievement || achievementQueue.length === 0) {
      return;
  }

  isShowingAchievement = true;
  const achievement = achievementQueue.shift();
  showAchievementNotification(achievement);
}

// Show achievement notification
function showAchievementNotification(achievement) {
  const notification = document.getElementById('notification');
  if (notification) {
      // Clear any existing content and classes
      notification.innerHTML = `
          <div class="achievement-notification">
              <div class="achievement-icon">${achievement.icon}</div>
              <div class="achievement-info">
                  <div class="achievement-title">Achievement Unlocked: ${achievement.title}</div>
                  <div class="achievement-description">${achievement.description}</div>
              </div>
          </div>
      `;

      // Force a reflow to ensure animations work correctly if notifications are in quick succession
      notification.offsetHeight;

      notification.classList.add('show');

      setTimeout(() => {
          notification.classList.remove('show');

          // After notification is removed, wait a short time before showing the next one
          setTimeout(() => {
              isShowingAchievement = false;
              processAchievementQueue();
          }, 500); // Small gap between notifications
      }, 5000);
  } else {
      // If notification element doesn't exist, move to the next achievement
      console.error('Notification element not found');
      isShowingAchievement = false;
      setTimeout(processAchievementQueue, 100);
  }
}

// Toggle achievements panel
function toggleAchievementsPanel() {
  const panel = document.getElementById('achievements-panel');
  const overlay = document.getElementById('menu-overlay');

  if (panel) {
      panel.classList.toggle('visible');

      if (panel.classList.contains('visible')) {
          overlay.classList.add('visible');
          renderAchievements();
      } else {
          overlay.classList.remove('visible');
      }
  }
}

// Close achievements panel
function closeAchievementsPanel() {
  const panel = document.getElementById('achievements-panel');
  const overlay = document.getElementById('menu-overlay');

  if (panel) {
      panel.classList.remove('visible');
      overlay.classList.remove('visible');
  }
}

// Render achievements in the panel
function renderAchievements() {
  const achievementsList = document.querySelector('.achievements-list');
  if (!achievementsList) return;

  // Clear existing achievements
  achievementsList.innerHTML = '';

  // Get user achievements
  const userAchievements = loadUserAchievements();

  // Render each achievement
  achievements.forEach(achievement => {
      const isUnlocked = userAchievements[achievement.id]?.unlocked || false;

      const achievementElement = document.createElement('div');
      achievementElement.className = `achievement-item achievement-${achievement.rarity} ${!isUnlocked ? 'achievement-locked' : ''}`;

      achievementElement.innerHTML = `
          <div class="achievement-icon">${achievement.icon}</div>
          <div class="achievement-info">
              <div class="achievement-title">${achievement.title}</div>
              <div class="achievement-description">${achievement.description}</div>
          </div>
      `;

      achievementsList.appendChild(achievementElement);
  });
}

// Check for achievements to unlock
function checkForAchievements(gameState) {
  // Example achievement checks based on game state
  // This would be expanded with all the actual logic

  if (gameState.won && gameState.guessCount === 1) {
      unlockAchievement('first_guess');
  }

  if (gameState.won && gameState.guessCount === gameState.maxGuesses) {
      unlockAchievement('clutch_guess');
  }

  // Tracking streaks would require checking dates in localStorage

  // Example for comeback achievement
  if (gameState.won && gameState.guessHistory.length >= 3) {
      const firstThreeGuesses = gameState.guessHistory.slice(0, 3);
      const allZeroCorrect = firstThreeGuesses.every(guess =>
          guess.every(letter => letter.state !== 'correct' && letter.state !== 'present'));

      if (allZeroCorrect) {
          unlockAchievement('comeback');
      }
  }

  // More achievement checks would be added here
}

// Initialize achievements
function initAchievements() {
  // Add notification wrapper if not exists
  if (!document.getElementById('notification-wrapper')) {
      const wrapper = document.createElement('div');
      wrapper.id = 'notification-wrapper';

      const notification = document.createElement('div');
      notification.id = 'notification';

      wrapper.appendChild(notification);
      document.body.appendChild(wrapper);
  }

  // Add overlay if not exists
  if (!document.getElementById('menu-overlay')) {
      const overlay = document.createElement('div');
      overlay.id = 'menu-overlay';
      overlay.className = 'menu-overlay';
      overlay.addEventListener('click', closeAchievementsPanel);
      document.body.appendChild(overlay);
  }

  // Add achievements panel if not exists
  if (!document.getElementById('achievements-panel')) {
      const panel = document.createElement('div');
      panel.id = 'achievements-panel';

      panel.innerHTML = `
          <button class="achievements-close" onclick="closeAchievementsPanel()">&times;</button>
          <h2>Achievements</h2>
          <div class="achievements-list"></div>
      `;

      document.body.appendChild(panel);
  }

  // Add achievements button if not exists
  if (!document.getElementById('achievements-btn')) {
      const header = document.querySelector('header') || document.querySelector('.header') || document.querySelector('#header');

      if (header) {
          const button = document.createElement('button');
          button.id = 'achievements-btn';
          button.className = 'achievements-btn';
          button.textContent = 'achievements';
          button.addEventListener('click', toggleAchievementsPanel);

          header.appendChild(button);
      }
  }
}

// Add CSS to head if not already included
function addAchievementsCSS() {
  // Check if achievement CSS is already loaded
  if (!document.querySelector('link[href="achievements.css"]')) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = 'achievements.css';
      document.head.appendChild(link);
  }
}

// Event listeners for achievements testing
document.addEventListener('DOMContentLoaded', function() {
  addAchievementsCSS();
  initAchievements();

  // Example of DOM event listening for achievements
  document.body.addEventListener('gamewon', function(e) {
      if (e.detail) {
          checkForAchievements(e.detail);
          unlockAchievement('first_win');
      }
  });
});

// Create a global Achievements object
window.Achievements = {
  achievements: achievements,
  unlockAchievement: unlockAchievement,
  loadUserAchievements: loadUserAchievements,
  saveUserAchievements: saveUserAchievements,
  showAchievementNotification: showAchievementNotification,
  queueAchievementNotification: queueAchievementNotification,
  renderAchievements: renderAchievements,
  checkForAchievements: checkForAchievements,
  toggleAchievementsPanel: toggleAchievementsPanel,
  closeAchievementsPanel: closeAchievementsPanel
};
