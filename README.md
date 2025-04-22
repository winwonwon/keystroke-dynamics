## Log-in by Password and Key Stroke Dynamic
By\
6588071 Thareerat Phothithamn\
6588101 Kawin Surakupt\
6588105 Pran Tantipiwatanaskul\
Section 3

A Flask-based authentication system that uses keystroke dynamics (typing biometrics) as a secondary verification factor alongside passwords.

## Features
- Password + keystroke pattern dual authentication
- Adaptive learning of typing patterns (stores last 5 samples)
- User registration/login functionality
- Admin dashboard with user management
- Visual feedback for keypress status and authentication results
- Automatic sample updating after successful logins

## Technology
- **Backend**: Python/Flask
- **Frontend**: HTML/CSS/JavaScript
- **Security**: SHA-256 password hashing
- **Biometrics**: 
  - 40ms tolerance for typing pattern matching
  - Exponential decay weighting for recent samples
  - Measures key hold-time and flight-time between keys

## Installation
1. Clone repository:
```bash
git clone https://github.com/winwonwon/keystroke-dynamics
```
Make sure the file structure is as follows:
```bash
├── templates/
│   ├── index.html          # Login/registration interface
│   ├── homepage.html       # Post-login dashboard
│   └── admin.html          # User management interface
├── static/
│   ├── index.css           # Login page styling
│   ├── script.js           # Keystroke tracking logic
│   ├── homepage.css        # Dashboard styling
│   └── admin.css           # Admin panel styling
├── app.py                  # Flask application core
├── requirements.txt        # Dependencies
└── users.json              # User data storage (auto-created)
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the application:
```bash
python app.py
```

## Usage
1. Access http://localhost:5000 in your browser

2. Register:
    - Enter username/password
    - Type naturally to record your typing pattern
3. Login:
    - Replicate your typing pattern closely
    - System learns from successful attempts
4. Admin Panel:
    - View/delete users from homepage
    - Monitor stored typing samples

## API Endpoints
| Route                   | Method | Description              |
|-------------------------|--------|--------------------------|
| /                       | GET    | Main login interface     |
| /register               | POST   | Handle new registrations |
| /login                  | POST   | Process login attempts   |
| /admin                  | GET    | Admin dashboard          |
| /delete_user/<username> | POST   | Remove user accounts     |
| /homepage/<username>    | GET    | User welcome page        |