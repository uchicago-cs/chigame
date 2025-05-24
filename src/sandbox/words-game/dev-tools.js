/**
 * DEVELOPMENT TOOLS - TEMPORARY CODE
 *
 * This file contains testing utilities for the achievements system.
 * This code is intended for development purposes only and should be removed before production.
 */

(function() {
    'use strict';

    // Create dev panel elements
    function createDevPanel() {
        // Create toggle button
        const toggle = document.createElement('button');
        toggle.id = 'dev-panel-toggle';
        toggle.textContent = 'Dev Tools';
        document.body.appendChild(toggle);

        // Create panel container
        const panel = document.createElement('div');
        panel.id = 'dev-panel';
        panel.innerHTML = `
            <h3>Achievement Testing</h3>
            <select id="achievement-selector">
                <option value="">-- Select Achievement --</option>
            </select>
            <button id="unlock-achievement">Unlock Achievement</button>
            <button id="lock-achievement">Lock Achievement</button>
            <button id="show-notification">Show Notification</button>
            <button id="unlock-multiple">Unlock Multiple Achievements</button>
            <button id="clear-all">Clear All Achievements</button>
            <button id="unlock-all">Unlock All Achievements</button>
            <div>
                <button id="view-storage">View LocalStorage</button>
                <div class="achievement-status" id="achievement-status" style="display: none;"></div>
            </div>

            <h3>Game Testing</h3>
            <button id="show-target-word">Show Target Word</button>

            <h3>Streak Management</h3>
            <div class="streak-info">
                <p>Solo Streak: <span id="dev-solo-streak">0</span></p>
                <p>Daily Streak: <span id="dev-daily-streak">0</span></p>
            </div>
            <div class="streak-controls">
                <button id="increase-solo-streak">Increase Solo Streak</button>
                <button id="reset-solo-streak">Reset Solo Streak</button>
                <button id="increase-daily-streak">Increase Daily Streak</button>
                <button id="reset-daily-streak">Reset Daily Streak</button>
                <button id="set-custom-streaks">Set Custom Streaks</button>
                <div id="custom-streak-inputs" style="display: none; margin-top: 10px;">
                    <input type="number" id="custom-solo-streak" placeholder="Solo Streak" min="0">
                    <input type="number" id="custom-daily-streak" placeholder="Daily Streak" min="0">
                    <button id="apply-custom-streaks">Apply</button>
                </div>
            </div>
        `;
        document.body.appendChild(panel);

        // Add styles for dev panel
        addDevPanelStyles();
    }

    // Add CSS styles for dev panel
    function addDevPanelStyles() {
        const style = document.createElement('style');
        style.textContent = `
            /* DEVELOPMENT TOOLS - TEMPORARY STYLES */
            #dev-panel-toggle {
                position: fixed;
                bottom: 10px;
                right: 10px;
                background-color: #333;
                color: white;
                padding: 5px 10px;
                border: none;
                cursor: pointer;
                font-size: 12px;
                z-index: 9999;
            }

            #dev-panel {
                position: fixed;
                bottom: 50px;
                right: 10px;
                width: 350px;
                background-color: var(--bg-darker);
                border: 2px solid var(--primary);
                padding: 15px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
                z-index: 9999;
                display: none;
                max-height: 80vh;
                overflow-y: auto;
            }

            #dev-panel.visible {
                display: block;
            }

            #dev-panel h3 {
                margin-top: 0;
                border-bottom: 1px solid var(--primary);
                padding-bottom: 5px;
                margin-bottom: 10px;
            }

            #dev-panel select,
            #dev-panel button,
            #dev-panel input {
                margin: 5px 0;
                padding: 5px;
                width: 100%;
                background-color: var(--card-bg);
                border: 1px solid var(--card-border);
                color: var(--text);
            }

            #dev-panel button {
                cursor: pointer;
                background-color: var(--primary);
                margin-bottom: 10px;
                color: white;
            }

            #dev-panel button:hover {
                background-color: var(--primary-hover);
            }

            #dev-panel .achievement-status {
                margin-top: 10px;
                padding: 5px;
                background-color: #000;
                color: #0f0;
                font-family: monospace;
                max-height: 150px;
                overflow-y: auto;
                white-space: pre;
            }

            #dev-panel .streak-info {
                background-color: var(--card-bg);
                padding: 5px;
                margin-bottom: 10px;
            }

            #dev-panel .streak-info p {
                margin: 5px 0;
            }

            #custom-streak-inputs {
                display: flex;
                flex-direction: column;
                gap: 5px;
            }
        `;
        document.head.appendChild(style);
    }

    // Initialize dev panel functionality
    function initDevTools() {
        if (!window.Achievements) {
            console.error('Dev Tools: Achievements module not found');
            return;
        }

        // Create the panel if it doesn't exist
        if (!document.getElementById('dev-panel')) {
            createDevPanel();
        }

        // Toggle visibility of dev panel
        const devPanelToggle = document.getElementById('dev-panel-toggle');
        const devPanel = document.getElementById('dev-panel');

        devPanelToggle.addEventListener('click', function() {
            devPanel.classList.toggle('visible');
            if (devPanel.classList.contains('visible')) {
                updateStreakDisplay();
            }
        });

        // Populate achievement selector
        const achievementSelector = document.getElementById('achievement-selector');

        // Clear existing options (except the first one)
        while (achievementSelector.options.length > 1) {
            achievementSelector.remove(1);
        }

        // Add achievements to selector
        window.Achievements.achievements.forEach(achievement => {
            const option = document.createElement('option');
            option.value = achievement.id;
            option.textContent = `${achievement.title} (${achievement.rarity})`;
            achievementSelector.appendChild(option);
        });

        // Unlock achievement
        document.getElementById('unlock-achievement').addEventListener('click', function() {
            const achievementId = achievementSelector.value;
            if (achievementId) {
                window.Achievements.unlockAchievement(achievementId);
                alert(`Achievement "${achievementId}" unlocked!`);
            } else {
                alert('Please select an achievement first');
            }
        });

        // Lock achievement
        document.getElementById('lock-achievement').addEventListener('click', function() {
            const achievementId = achievementSelector.value;
            if (achievementId) {
                const userAchievements = window.Achievements.loadUserAchievements();
                if (userAchievements[achievementId]) {
                    delete userAchievements[achievementId];
                    window.Achievements.saveUserAchievements(userAchievements);
                    alert(`Achievement "${achievementId}" locked!`);
                } else {
                    alert(`Achievement "${achievementId}" was not unlocked.`);
                }
            } else {
                alert('Please select an achievement first');
            }
        });

        // Show notification
        document.getElementById('show-notification').addEventListener('click', function() {
            const achievementId = achievementSelector.value;
            if (achievementId) {
                const achievement = window.Achievements.achievements.find(a => a.id === achievementId);
                if (achievement) {
                    window.Achievements.queueAchievementNotification(achievement);
                }
            } else {
                alert('Please select an achievement first');
            }
        });

        // Unlock multiple achievements
        document.getElementById('unlock-multiple').addEventListener('click', function() {
            if (confirm('This will unlock 3 achievements at once to test notification queue. Continue?')) {
                // Unlock a set of predetermined achievements
                const testAchievements = ['first_win', 'first_guess', 'clutch_guess'];

                // Queue these achievements with small delays to simulate them being triggered in sequence
                testAchievements.forEach((achievementId, index) => {
                    window.Achievements.unlockAchievement(achievementId);
                });

                alert('Test complete - 3 achievements were queued for display');
            }
        });

        // Clear all achievements
        document.getElementById('clear-all').addEventListener('click', function() {
            if (confirm('Are you sure you want to clear all achievements?')) {
                localStorage.removeItem('userAchievements');
                alert('All achievements have been cleared.');
            }
        });

        // Unlock all achievements
        document.getElementById('unlock-all').addEventListener('click', function() {
            if (confirm('Are you sure you want to unlock all achievements?')) {
                const userAchievements = {};
                window.Achievements.achievements.forEach(achievement => {
                    userAchievements[achievement.id] = {
                        unlocked: true,
                        date: new Date().toISOString()
                    };
                });
                window.Achievements.saveUserAchievements(userAchievements);
                alert('All achievements have been unlocked.');
            }
        });

        // Toggle localStorage view
        document.getElementById('view-storage').addEventListener('click', function() {
            const statusElement = document.getElementById('achievement-status');
            const button = this;

            if (statusElement.style.display === 'block') {
                // Hide the status display
                statusElement.style.display = 'none';
                button.textContent = 'View LocalStorage';
            } else {
                // Show the status and update content
                const userAchievements = window.Achievements.loadUserAchievements();
                statusElement.textContent = JSON.stringify(userAchievements, null, 2);
                statusElement.style.display = 'block';
                button.textContent = 'Hide LocalStorage';
            }
        });

        // Show Target Word
        document.getElementById('show-target-word').addEventListener('click', function() {
            if (typeof word !== 'undefined') {
                alert(`Current Target Word: "${word}"`);
            } else {
                alert('Word not available. Game may not be initialized yet.');
            }
        });

        // Update streak display in dev panel
        function updateStreakDisplay() {
            // Get streaks from localStorage
            const streaksData = localStorage.getItem("gameStreaks");
            if (streaksData) {
                const streaks = JSON.parse(streaksData);
                document.getElementById('dev-solo-streak').textContent = streaks.soloStreak || 0;
                document.getElementById('dev-daily-streak').textContent = streaks.dailyStreak || 0;
            } else {
                document.getElementById('dev-solo-streak').textContent = 0;
                document.getElementById('dev-daily-streak').textContent = 0;
            }
        }

        // Streak Management Functions
        function getStreaks() {
            const streaksData = localStorage.getItem("gameStreaks");
            if (streaksData) {
                return JSON.parse(streaksData);
            }
            return {
                soloStreak: 0,
                dailyStreak: 0,
                lastDailyWins: {}
            };
        }

        function saveStreaks(streaks) {
            localStorage.setItem("gameStreaks", JSON.stringify(streaks));
            updateStreakDisplay();
            if (typeof updateStreakDisplay === 'function') {
                window.updateStreakDisplay();
            }
        }

        // Increase Solo Streak
        document.getElementById('increase-solo-streak').addEventListener('click', function() {
            const streaks = getStreaks();
            streaks.soloStreak = (streaks.soloStreak || 0) + 1;
            saveStreaks(streaks);
            alert(`Solo streak increased to ${streaks.soloStreak}`);
        });

        // Reset Solo Streak
        document.getElementById('reset-solo-streak').addEventListener('click', function() {
            const streaks = getStreaks();
            streaks.soloStreak = 0;
            saveStreaks(streaks);
            alert('Solo streak reset to 0');
        });

        // Increase Daily Streak
        document.getElementById('increase-daily-streak').addEventListener('click', function() {
            const streaks = getStreaks();
            streaks.dailyStreak = (streaks.dailyStreak || 0) + 1;
            saveStreaks(streaks);
            alert(`Daily streak increased to ${streaks.dailyStreak}`);
        });

        // Reset Daily Streak
        document.getElementById('reset-daily-streak').addEventListener('click', function() {
            const streaks = getStreaks();
            streaks.dailyStreak = 0;
            saveStreaks(streaks);
            alert('Daily streak reset to 0');
        });

        // Set Custom Streaks Toggle
        document.getElementById('set-custom-streaks').addEventListener('click', function() {
            const customInputs = document.getElementById('custom-streak-inputs');
            if (customInputs.style.display === 'none') {
                customInputs.style.display = 'block';
                const streaks = getStreaks();
                document.getElementById('custom-solo-streak').value = streaks.soloStreak || 0;
                document.getElementById('custom-daily-streak').value = streaks.dailyStreak || 0;
            } else {
                customInputs.style.display = 'none';
            }
        });

        // Apply Custom Streaks
        document.getElementById('apply-custom-streaks').addEventListener('click', function() {
            const soloStreakValue = parseInt(document.getElementById('custom-solo-streak').value);
            const dailyStreakValue = parseInt(document.getElementById('custom-daily-streak').value);

            if (isNaN(soloStreakValue) || isNaN(dailyStreakValue) || soloStreakValue < 0 || dailyStreakValue < 0) {
                alert('Please enter valid positive numbers for streaks');
                return;
            }

            const streaks = getStreaks();
            streaks.soloStreak = soloStreakValue;
            streaks.dailyStreak = dailyStreakValue;
            saveStreaks(streaks);

            alert(`Streaks updated - Solo: ${soloStreakValue}, Daily: ${dailyStreakValue}`);
            document.getElementById('custom-streak-inputs').style.display = 'none';
        });

        // Initial streak display update
        updateStreakDisplay();
    }

    // Initialize when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        // Wait for Achievements to be available
        if (window.Achievements) {
            initDevTools();
        } else {
            // Retry after a delay
            setTimeout(function() {
                if (window.Achievements) {
                    initDevTools();
                } else {
                    console.error('Dev Tools: Achievements module not found after delay');
                }
            }, 500);
        }
    });
})();
