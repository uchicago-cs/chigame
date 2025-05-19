document.addEventListener('DOMContentLoaded', function() {
  const slider = document.getElementById('font-size-slider');
  const resetBtn = document.getElementById('reset-font-size');
  const defaultSize = 16;

  // Load saved font size
  const savedSize = localStorage.getItem('kb-font-size');
  if (savedSize) {
    document.body.style.fontSize = savedSize + 'px';
    slider.value = savedSize;
  }

  slider.addEventListener('input', function() {
    document.body.style.fontSize = slider.value + 'px';
    localStorage.setItem('kb-font-size', slider.value);
  });

  resetBtn.addEventListener('click', function() {
    document.body.style.fontSize = defaultSize + 'px';
    slider.value = defaultSize;
    localStorage.removeItem('kb-font-size');
  });
});
