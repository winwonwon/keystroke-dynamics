from flask import Flask, request, render_template, jsonify
import hashlib, json, os

app = Flask(__name__)
USERS_FILE = "users.json"
MAX_SAMPLES = 5

# Load or initialize stored user profiles
if os.path.exists(USERS_FILE):
    try:
        with open(USERS_FILE) as f:
            users = json.load(f)
    except (json.JSONDecodeError, IOError):
        users = {}
else:
    users = {}


def hash_password(password):
    """Return a SHA-256 hash of the given password."""
    return hashlib.sha256(password.encode()).hexdigest()


def extract_features(keystrokes):
    """
    Compute average key-hold and flight times from raw keystroke events.
    - hold_times: duration each key was held down
    - flight_times: time between consecutive key presses
    """
    hold_times = [k['hold'] for k in keystrokes]
    flight_times = [
        keystrokes[i+1]['time'] - keystrokes[i]['time']
        for i in range(len(keystrokes) - 1)
    ]
    return {
        "hold_mean": sum(hold_times) / len(hold_times) if hold_times else 0,
        "flight_mean": sum(flight_times) / len(flight_times) if flight_times else 0
    }


def is_similar(f1, f2):
    """
    Compare two feature dicts; allow tolerance of 40ms for both hold and flight times.
    """
    return (
        abs(f1["hold_mean"] - f2["hold_mean"]) < 40
        and abs(f1["flight_mean"] - f2["flight_mean"]) < 40
    )


def average_features(samples):
    """
    Compute a weighted average of past typing samples,
    giving more weight to recent entries.
    """
    if not samples:
        return {"hold_mean": 0, "flight_mean": 0}
    # exponential decay weights
    weights = [0.5 ** (len(samples) - i) for i in range(len(samples))]
    total = sum(weights)
    hold = sum(s["hold_mean"] * w for s, w in zip(samples, weights)) / total
    flight = sum(s["flight_mean"] * w for s, w in zip(samples, weights)) / total
    return {"hold_mean": hold, "flight_mean": flight}


@app.route('/')
def index():
    """Render the login/register page."""
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    if username in users:
        # Prevent duplicate registrations
        return jsonify({"message": "User already exists"}), 400

    # Store new user with hashed password and initial typing sample
    users[username] = {
        "password": hash_password(data["password"]),
        "samples": [extract_features(data["keystrokes"])]
    }

    # Persist to disk
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

    return jsonify({"message": "Registered successfully"})


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data["username"]

    if username not in users:
        return jsonify({"message": "User not found"}), 404

    # Verify password hash
    if users[username]["password"] != hash_password(data["password"]):
        return jsonify({"message": "Incorrect password"}), 401

    # Compare current typing features to stored profile
    current = extract_features(data["keystrokes"])
    stored_samples = users[username]["samples"]
    avg = average_features(stored_samples)

    if is_similar(current, avg):
        # Update sample history, keeping at most MAX_SAMPLES
        if len(stored_samples) >= MAX_SAMPLES:
            users[username]["samples"] = stored_samples[-(MAX_SAMPLES-1):] + [current]
        else:
            users[username]["samples"].append(current)

        with open(USERS_FILE, "w") as f:
            json.dump(users, f)

        return jsonify({"message": "Login successful!"})

    # Reject if typing pattern doesn't match
    return jsonify({"message": "Typing pattern mismatch"}), 403


@app.route('/admin')
def admin_dashboard():
    """Show admin page listing all registered users."""
    return render_template("admin.html", users=users)


@app.route('/delete_user/<username>', methods=['POST'])
def delete_user(username):
    """Remove a user account and update storage."""
    if username in users:
        del users[username]
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)
        return jsonify({"message": f"Deleted {username}"})
    return jsonify({"message": "User not found"}), 404


if __name__ == '__main__':
    # Start Flask development server
    app.run(debug=True)
