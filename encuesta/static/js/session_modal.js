const warningTime = 25 * 60 * 1000; // 25 minutos
const modalTimeout = 30 * 1000; // 30 segundos

let warningTimer, logoutTimer, countdownInterval;

function showSessionModal() {
  const modal = new bootstrap.Modal(document.getElementById('sessionTimeoutModal'));
  modal.show();

  let secondsLeft = Math.floor(modalTimeout / 1000);
  const countdownElem = document.getElementById('modal-countdown');
  countdownElem.textContent = secondsLeft;

  countdownInterval = setInterval(() => {
    secondsLeft -= 1;
    countdownElem.textContent = secondsLeft;
    if (secondsLeft <= 0) {
      clearInterval(countdownInterval);
    }
  }, 1000);

  logoutTimer = setTimeout(() => {
    clearInterval(countdownInterval);
    document.querySelector('#sessionTimeoutModal form').submit();
  }, modalTimeout);
}

function resetTimers() {
  clearTimeout(warningTimer);
  clearTimeout(logoutTimer);
  clearInterval(countdownInterval);
  warningTimer = setTimeout(showSessionModal, warningTime);
}

['click', 'mousemove', 'keydown', 'scroll', 'touchstart'].forEach(evt => {
  document.addEventListener(evt, resetTimers, true);
});

document.getElementById('sessionTimeoutModal').addEventListener('hidden.bs.modal', resetTimers);

resetTimers();