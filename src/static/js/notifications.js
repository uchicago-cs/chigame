function dismissNotification(notificationId) {
  fetch(`/users/act_on_inbox_notification/${notificationId}/delete`, {
    method: 'GET',
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
    },
  })
  .then(response => {
    if (response.ok) {
      const notifEl = document.getElementById(`notification-${notificationId}`);
      if (notifEl) notifEl.remove();
      updateNotificationBadgeCount();
    } else {
      console.error("Failed to dismiss notification.");
    }
  });
}

function updateNotificationBadgeCount() {
  const badge = document.querySelector('#notification-btn .badge');
  const remaining = document.querySelectorAll('.notifications-dropdown .dropdown-item').length;
  if (badge) {
    if (remaining === 0) {
      badge.remove();
    } else {
      badge.innerText = remaining;
    }
  }
}
