let keystrokes = [];            // Array to store each key event with timing
let keyDownTime = {};           // Map to record when each key was pressed down
let isSubmitting = false;       // Flag to prevent duplicate form submissions

document.addEventListener('DOMContentLoaded', () => {
    const pw = document.getElementById('password');
    const keyStatus = document.getElementById('keyStatus');
    const togglePassword = document.getElementById('togglePassword');
    const resetPassword = document.getElementById('resetPassword');

    // When a key is pressed, start timing and show visual cue
    pw.addEventListener('keydown', (e) => {
        if (!isSubmitting) {
            keyStatus.classList.add('active');
            keyDownTime[e.key] = performance.now();
        }
    });

    // On key release, record hold time and timestamp
    pw.addEventListener('keyup', (e) => {
        keyStatus.classList.remove('active');
        if (!isSubmitting) {
            const now = performance.now();
            const start = keyDownTime[e.key] || now;
            keystrokes.push({ key: e.key, hold: now - start, time: now });
        }
    });

    // Submit form when Enter is pressed in password field
    pw.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !isSubmitting) {
            e.preventDefault();
            submitForm('login');
        }
    });

    // Toggle between password visibility states
    togglePassword.addEventListener('click', () => {
        const currentType = pw.getAttribute('type');
        const newType = currentType === 'password' ? 'text' : 'password';
        pw.setAttribute('type', newType);
        togglePassword.classList.toggle('fa-eye-slash');
        togglePassword.classList.toggle('fa-eye');
    });

    // Reset input and keystroke history when reset icon is clicked
    resetPassword.addEventListener('click', resetPasswordInput);

    // Also allow Escape key to clear password field
    pw.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            e.preventDefault();
            resetPasswordInput();
        }
    });
});

/**
 * Handle form submission for login or registration
 * @param {string} action - Endpoint to call ("login" or "register")
 */
function submitForm(action) {
    if (isSubmitting) return;

    // Gather input values and UI elements
    const usernameField = document.getElementById('username');
    const passwordField = document.getElementById('password');
    const username = usernameField.value.trim();
    const password = passwordField.value;
    const resultElement = document.getElementById('result');
    const buttons = document.querySelectorAll('button');
    const spinner = document.getElementById('spinner');

    // Basic empty-field check
    if (!username || !password) {
        resultElement.innerText = "Please fill in all fields";
        resultElement.classList.add('error');
        return;
    }

    // Disable UI and show spinner
    isSubmitting = true;
    buttons.forEach(btn => btn.disabled = true);
    spinner.style.display = 'inline-block';
    resultElement.classList.remove('error', 'success');

    // Send keystroke data along with credentials
    fetch(`/${action}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password, keystrokes })
    })
    .then(async res => {
        const data = await res.json();
        if (!res.ok) throw { ...data, status: res.status };
        return data;
    })
    .then(data => {
        // On success, display message and reset fields
        resultElement.innerText = data.message;
        resultElement.classList.add('success');
        usernameField.value = '';
        passwordField.value = '';
        usernameField.focus();
    })
    .catch(err => {
        // Show error message; reset if specific conditions met
        resultElement.innerText = err.message || "An error occurred";
        resultElement.classList.add('error');
        if (err.message === "User already exists" || err.message === "Typing pattern mismatch") {
            resetPasswordInput();
        }
    })
    .finally(() => {
        // Re-enable UI, hide spinner, clear keystroke log
        isSubmitting = false;
        buttons.forEach(btn => btn.disabled = false);
        spinner.style.display = 'none';
        keystrokes = [];
    });
}

/**
 * Clear password field, keystroke data, and reset status indicators
 */
function resetPasswordInput() {
    const pw = document.getElementById('password');
    const keyStatus = document.getElementById('keyStatus');

    pw.value = '';
    keyStatus.classList.remove('active');
    keystrokes = [];
    keyDownTime = {};

    // Blur and refocus to reset input state
    document.activeElement.blur();
    pw.focus();

    document.getElementById('result').innerText = '';
    // Trigger any input listeners if needed
    pw.dispatchEvent(new Event('input'));
}