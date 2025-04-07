let keystrokes = [];
let keyDownTime = {};

document.addEventListener('DOMContentLoaded', () => {
    const pw = document.getElementById('password');

    pw.addEventListener('keydown', (e) => {
        keyDownTime[e.key] = performance.now();
    });

    pw.addEventListener('keyup', (e) => {
        const time = performance.now();
        const down = keyDownTime[e.key] || time;
        keystrokes.push({ key: e.key, hold: time - down, time });
    });
});

function submitForm(action) {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    fetch(`/${action}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password, keystrokes })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById('result').innerText = data.message;
        keystrokes = [];
    })
    .catch(err => {
        document.getElementById('result').innerText = "Error: " + err.message;
        keystrokes = [];
    });
}
