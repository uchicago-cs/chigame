document.addEventListener('DOMContentLoaded', () => {
  const menu = document.getElementById('message-menu');
  let clickCount = 0;
  let clickTimer = null;

  // Helper to reset our click counter
  function resetClicks() {
    clickCount = 0;
    if (clickTimer) clearTimeout(clickTimer);
  }

  // Show the menu just under the clicked message
  function showMenu(msgEl) {
    const rect = msgEl.getBoundingClientRect();
    menu.style.top  = `${rect.bottom + window.scrollY}px`;
    menu.style.left = `${rect.left + window.scrollX}px`;
    menu.style.display = 'block';
  }

  // Attach to every message
  document.querySelectorAll('.chat-message').forEach(msgEl => {
    msgEl.addEventListener('click', e => {
      clickCount++;
      if (clickCount === 3) {
        showMenu(msgEl);
        resetClicks();
      } else {
        // if no third click within 600ms, reset
        if (clickTimer) clearTimeout(clickTimer);
        clickTimer = setTimeout(resetClicks, 600);
      }
    });
  });

  // Clicking anywhere else hides the menu
  document.addEventListener('click', e => {
    if (!menu.contains(e.target) && !e.target.closest('.chat-message')) {
      menu.style.display = 'none';
    }
  });
});
