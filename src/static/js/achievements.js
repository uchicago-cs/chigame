document.addEventListener('DOMContentLoaded', function () {
  // Remove any existing click handlers by cloning and replacing tabs
  const tabsContainer = document.querySelector('.nav-tabs');
  if (tabsContainer) {
    const newTabsContainer = tabsContainer.cloneNode(true);
    tabsContainer.parentNode.replaceChild(newTabsContainer, tabsContainer);
  }

  // Initialize progress bars
  document.querySelectorAll('[data-progress]').forEach(function (element) {
    const progressValue = element.getAttribute('data-progress');
    if (progressValue) {
      element.style.width = progressValue + '%';
    }
  });

  // Direct and simple tab switching implementation
  document.querySelectorAll('.nav-tabs li').forEach(function (tab) {
    tab.addEventListener('click', function (event) {
      event.preventDefault();
      event.stopPropagation();

      // Get tab ID
      const tabId = this.getAttribute('data-tab');

      // Reset all tabs
      document.querySelectorAll('.nav-tabs li').forEach(function (t) {
        t.classList.remove('active');
      });

      // Activate this tab
      this.classList.add('active');

      // Hide all content
      document.querySelectorAll('.tab-content > div').forEach(function (content) {
        content.classList.remove('active');
        content.style.display = 'none';
      });

      // Show this content - using both class and style for redundancy
      const content = document.getElementById(tabId);
      content.classList.add('active');
      content.style.display = 'block';
      return false; // Ensure no other handlers run
    });
  });

  // Initialize progress bars
  const progressElements = document.querySelectorAll('.progress-fill, .progress-fill-dynamic');
  progressElements.forEach(function (element) {
    const progressValue = element.getAttribute('data-progress');
    if (progressValue) {
      element.style.width = progressValue + '%';
    }
  });

  // Enhanced Search and Filter Functionality
  const searchBox = document.getElementById('searchBox');
  const statusFilter = document.getElementById('statusFilter'); // Get the new dropdown

  function applyAchievementFilters() {
    const searchText = searchBox.value.toLowerCase();
    const selectedStatus = statusFilter.value; // Will be 'all', 'completed', 'in-progress', or 'not-started'
    const gameCards = document.querySelectorAll('.game-card');

    gameCards.forEach(function (card) {
      let hasVisibleAchievementsInThisCard = false;
      const achievementsInCard = card.querySelectorAll('.achievement');

      achievementsInCard.forEach(function (achievementDiv) {
        const titleElement = achievementDiv.querySelector('.achievement-info h4');
        const descElement = achievementDiv.querySelector('.achievement-info .achievement-desc');

        // Get text content, accounting for "???" spoilers
        const titleText = titleElement ? titleElement.textContent.toLowerCase() : '';
        const descText = descElement ? descElement.textContent.toLowerCase() : '';

        // Check text match
        let textSearchSucceeded = true; // Assume true if search box is empty
        if (searchText !== '') {
          textSearchSucceeded = titleText.includes(searchText) || descText.includes(searchText);
        }

        // Check status match based on CSS classes
        let statusFilterSucceeded = false;
        if (selectedStatus === 'all') {
          statusFilterSucceeded = true;
        } else if (selectedStatus === 'completed') {
          statusFilterSucceeded = achievementDiv.classList.contains('completed');
        } else if (selectedStatus === 'in-progress') {
          statusFilterSucceeded = achievementDiv.classList.contains('in-progress');
        } else if (selectedStatus === 'not-started') {
          statusFilterSucceeded = achievementDiv.classList.contains('not-started');
        }

        // Show/hide achievement based on both criteria
        if (textSearchSucceeded && statusFilterSucceeded) {
          achievementDiv.style.display = 'flex'; // Default display for .achievement is flex
          hasVisibleAchievementsInThisCard = true;
        } else {
          achievementDiv.style.display = 'none';
        }
      });

      // Show/hide the entire game card based on whether it has any visible achievements
      if (hasVisibleAchievementsInThisCard) {
        card.style.display = 'block';
      } else {
        card.style.display = 'none';
      }
    });
  }

  // Add event listeners to both search box and status filter
  if (searchBox && statusFilter) {
    searchBox.addEventListener('input', applyAchievementFilters);
    statusFilter.addEventListener('change', applyAchievementFilters);
  }

  // Pin button functionality
  const pinButtons = document.querySelectorAll('.pin-button');

  pinButtons.forEach(function (button) {
    button.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();

      const achievementId = this.getAttribute('data-achievement-id');
      const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

      let url = `/achievements/toggle-pin/${achievementId}/`;

      fetch(url, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        credentials: 'same-origin',
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then((data) => {
          if (data.status === 'success') {
            // Update the all achievements in both tabs with the same id
            const allGamesAchievements = document.querySelectorAll(
              `#all-games .achievement[data-achievement-id="${achievementId}"]`
            );
            allGamesAchievements.forEach(function (achievementElem) {
              const pinBtn = achievementElem.querySelector('.pin-button');
              if (data.pinned) {
                achievementElem.classList.add('pinned');
                if (pinBtn) pinBtn.classList.add('active');
              } else {
                achievementElem.classList.remove('pinned');
                if (pinBtn) pinBtn.classList.remove('active');
              }
            });

            // Unpinning
            if (!data.pinned) {
              // Remove the achievement from the pinned achievements tab
              const pinnedAchievements = document.querySelectorAll(
                `#pinned-achievements .achievement[data-achievement-id="${achievementId}"]`
              );
              pinnedAchievements.forEach(function (achievementElem) {
                achievementElem.style.animation = 'fadeOut 0.3s';
                setTimeout(() => {
                  achievementElem.remove();

                  // check if there are any pinned achievements left
                  const remainingPinnedAchievements = document.querySelectorAll(
                    '#pinned-achievements .achievement'
                  );
                  if (remainingPinnedAchievements.length === 0) {
                    const emptyMessage = document.createElement('div');
                    emptyMessage.className = 'empty-pinned-message';
                    emptyMessage.innerHTML =
                      '<p>No achievements pinned yet. Pin your favorite achievements to see them here!</p>';
                    const achievementsList = document.querySelector(
                      '#pinned-achievements .achievements-list'
                    );
                    if (
                      achievementsList &&
                      !achievementsList.querySelector('.empty-pinned-message')
                    ) {
                      achievementsList.appendChild(emptyMessage);
                    }
                  }
                }, 300);
              });
            }
            // Pinning
            else {
              // Check if the achievement is already in the pinned achievements tab
              const existingInPinned = document.querySelector(
                `#pinned-achievements .achievement[data-achievement-id="${achievementId}"]`
              );

              if (!existingInPinned) {
                // Add the achievement to the pinned achievements tab
                const originalAchievement = document.querySelector(
                  `#all-games .achievement[data-achievement-id="${achievementId}"]`
                );

                if (originalAchievement) {
                  const nameElem = originalAchievement.querySelector('.achievement-info h4');
                  const descElem = originalAchievement.querySelector(
                    '.achievement-info .achievement-desc'
                  );
                  const dateElem = originalAchievement.querySelector(
                    '.achievement-info .achievement-date'
                  );
                  const iconImg = originalAchievement.querySelector('.trophy-icon img');

                  let rarityClass = '';
                  if (originalAchievement.classList.contains('common')) rarityClass = 'common';
                  else if (originalAchievement.classList.contains('uncommon'))
                    rarityClass = 'uncommon';
                  else if (originalAchievement.classList.contains('rare')) rarityClass = 'rare';
                  else if (originalAchievement.classList.contains('precious'))
                    rarityClass = 'precious';

                  const gameCard = originalAchievement.closest('.game-card');
                  const gameName = gameCard
                    ? gameCard.querySelector('.game-title').textContent
                    : '';

                  const rarityMatch = iconImg.src.match(/achievement_icons\/(\d)\.png/);
                  const rarityNumber = rarityMatch ? rarityMatch[1] : '1';

                  let unlockedDate = '';
                  if (dateElem) {
                    const dateMatch = dateElem.textContent.match(/Unlocked on (.+)/);
                    unlockedDate = dateMatch ? dateMatch[1] : 'Not unlocked';
                  }
                  const newPinnedAchievement = `
                <div class="achievement ${rarityClass} pinned" data-achievement-id="${achievementId}">
                  <div class="achievement-icon">
                    <span class="trophy-icon">
                      <img src="/static/images/achievement_icons/${rarityNumber}.png" alt="Achievement Trophy" />
                    </span>
                  </div>
                  <div class="achievement-info">
                    <h4>${nameElem ? nameElem.textContent : 'Achievement'}</h4>
                    <p class="achievement-desc">
                      ${descElem ? descElem.textContent : ''} in ${gameName}
                    </p>
                    <p class="achievement-date">
                    ${
                      unlockedDate && unlockedDate !== 'Not yet unlocked'
                        ? 'Unlocked on ' + unlockedDate
                        : 'Not yet unlocked'
                    }
                    </p>
                  </div>
                  <button class="pin-button active" data-achievement-id="${achievementId}">
                    📌
                  </button>
                </div>
              `;
                  const emptyMessage = document.querySelector(
                    '#pinned-achievements .empty-pinned-message'
                  );
                  if (emptyMessage) {
                    emptyMessage.remove();
                  }
                  const achievementsList = document.querySelector(
                    '#pinned-achievements .achievements-list'
                  );
                  if (achievementsList) {
                    achievementsList.insertAdjacentHTML('beforeend', newPinnedAchievement);

                    // Add event listener to the new pin button
                    const newPinButton = achievementsList.querySelector(
                      `.achievement[data-achievement-id="${achievementId}"] .pin-button`
                    );
                    if (newPinButton) {
                      newPinButton.addEventListener('click', function (e) {
                        e.preventDefault();
                        e.stopPropagation();

                        const achievementId = this.getAttribute('data-achievement-id');
                        const csrftoken = document.querySelector(
                          '[name=csrfmiddlewaretoken]'
                        ).value;

                        let url = `/achievements/toggle-pin/${achievementId}/`;

                        fetch(url, {
                          method: 'POST',
                          headers: {
                            'X-CSRFToken': csrftoken,
                            'Content-Type': 'application/x-www-form-urlencoded',
                          },
                          credentials: 'same-origin',
                        })
                          .then((response) => response.json())
                          .then((data) => {
                            if (data.status === 'success' && !data.pinned) {
                              document
                                .querySelectorAll(
                                  `#all-games .achievement[data-achievement-id="${achievementId}"] .pin-button`
                                )
                                .forEach(function (btn) {
                                  btn.classList.remove('active');
                                  btn.closest('.achievement').classList.remove('pinned');
                                });

                              // Remove the achievement from the pinned achievements tab
                              const achievementItem = this.closest('.achievement');
                              if (achievementItem) {
                                achievementItem.style.animation = 'fadeOut 0.3s';
                                setTimeout(() => {
                                  achievementItem.remove();

                                  // check if there are any pinned achievements left
                                  const remainingPinnedAchievements = document.querySelectorAll(
                                    '#pinned-achievements .achievement'
                                  );
                                  if (remainingPinnedAchievements.length === 0) {
                                    const emptyMessage = document.createElement('div');
                                    emptyMessage.className = 'empty-pinned-message';
                                    emptyMessage.innerHTML =
                                      '<p>No achievements pinned yet. Pin your favorite achievements to see them here!</p>';
                                    document
                                      .querySelector('#pinned-achievements .achievements-list')
                                      .appendChild(emptyMessage);
                                  }
                                }, 300);
                              }
                            }
                          })
                          .catch((error) => {});
                      });
                    }
                  }
                }
              }
            }
          }
        })
        .catch((error) => {});
    });
  });
});
