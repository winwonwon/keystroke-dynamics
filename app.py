from flask import Flask, request, render_template, jsonify, send_from_directory
import hashlib, json, os

app = Flask(__name__)

USERS_FILE = "users.json"

if os.path.exists(USERS_FILE):
    try:
        with open(USERS_FILE) as f:
            users = json.load(f)
    except json.JSONDecodeError:
        users = {}
else:
    users = {}


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def extract_features(keystrokes):
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
    return (
        abs(f1["hold_mean"] - f2["hold_mean"]) < 20 and
        abs(f1["flight_mean"] - f2["flight_mean"]) < 20
    )

def average_features(samples):
    if not samples:
        return {"hold_mean": 0, "flight_mean": 0}
    hold_avg = sum(s["hold_mean"] for s in samples) / len(samples)
    flight_avg = sum(s["flight_mean"] for s in samples) / len(samples)
    return {"hold_mean": hold_avg, "flight_mean": flight_avg}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    if username in users:
        return jsonify({"message": "User already exists"}), 400

    features = extract_features(data["keystrokes"])

    users[username] = {
        "password": hash_password(data["password"]),
        "samples": [features]
    }

    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

    return jsonify({"message": "Registered successfully"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data["username"]
    if username not in users:
        return jsonify({"message": "User not found"}), 404

    if users[username]["password"] != hash_password(data["password"]):
        return jsonify({"message": "Incorrect password"}), 401

    current = extract_features(data["keystrokes"])
    stored_samples = users[username]["samples"]
    avg_features = average_features(stored_samples)

    if is_similar(current, avg_features):
        # Optional: add the current sample to the list
        users[username]["samples"].append(current)
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)
        return jsonify({"message": "Login successful!"})
    else:
        return jsonify({"message": "Typing pattern mismatch"}), 403

@app.route('/admin')
def admin_dashboard():
    return render_template("admin.html", users=users)

@app.route('/delete_user/<username>', methods=['POST'])
def delete_user(username):
    if username in users:
        del users[username]
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)
        return jsonify({"message": f"Deleted {username}"})
    return jsonify({"message": "User not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
