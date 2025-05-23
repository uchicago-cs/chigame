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
            <button id="clear-all">Clear All Achievements</button>
            <button id="unlock-all">Unlock All Achievements</button>
            <div>
                <button id="view-storage">View LocalStorage</button>
                <div class="achievement-status" id="achievement-status" style="display: none;"></div>
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
            #dev-panel button {
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
                    window.Achievements.showAchievementNotification(achievement);
                }
            } else {
                alert('Please select an achievement first');
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
