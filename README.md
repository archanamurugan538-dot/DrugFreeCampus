# DrugFree Campus

**"Choose Your Future. Stay Safe. Stay Drug-Free."**

An Anti-Drug and Safe Campus Awareness Web Application built as a college mini-project.

---

## Tech Stack

| Layer      | Technology                  |
|------------|-----------------------------|
| Frontend   | HTML5, CSS3, JavaScript     |
| Backend    | Python Flask                |
| Database   | SQLite (`drugfree_campus.db`) |
| DB Library | Python built-in `sqlite3`   |

---

## Features

- Student registration and login with secure password hashing
- Flask session management
- Drug awareness module (6 substance categories)
- Effects & risks module (physical, mental, academic, social)
- Peer-pressure decision challenge (5 interactive scenarios)
- 10-question awareness quiz with instant scoring
- Quiz history with attempt tracking
- Healthy alternatives module (12 positive activities)
- Anti-ragging awareness with official UGC helpline
- Help & support with verified Indian helplines
- Drug-Free Campus pledge
- Fully responsive design (desktop, tablet, mobile)

---

## Project Structure

```
DrugFreeCampus/
├── app.py                  # Flask application & all routes
├── database.py             # SQLite connection helper
├── init_db.py              # Database initialisation script
├── requirements.txt        # Python dependencies
├── drugfree_campus.db      # SQLite database (auto-created)
│
├── templates/
│   ├── base.html           # Base layout (navbar, footer, flash messages)
│   ├── index.html          # Home / landing page
│   ├── register.html       # Student registration
│   ├── login.html          # Login page
│   ├── dashboard.html      # Student dashboard with stats
│   ├── awareness.html      # Drug awareness module
│   ├── effects.html        # Effects & risks module
│   ├── decision.html       # Decision challenge
│   ├── quiz.html           # Awareness quiz
│   ├── result.html         # Quiz results
│   ├── quiz_history.html   # Quiz attempt history
│   ├── healthy.html        # Healthy alternatives
│   ├── anti_ragging.html   # Anti-ragging awareness
│   ├── help.html           # Help & support
│   └── pledge.html         # Drug-Free Campus pledge
│
├── static/
│   ├── css/style.css       # Main stylesheet
│   ├── js/
│   │   ├── main.js         # Global JS (navbar, animations)
│   │   ├── register.js     # Registration validation
│   │   ├── login.js        # Login validation
│   │   ├── quiz.js         # Quiz navigation & validation
│   │   └── decision.js     # Decision challenge validation
│   └── images/
│       └── logo.svg        # Application logo
```

---

## Database Tables

| Table              | Purpose                              |
|--------------------|--------------------------------------|
| `users`            | Registered student accounts          |
| `quiz_results`     | All quiz attempt records             |
| `pledge`           | Drug-Free pledge records (one/user)  |
| `decision_results` | Decision challenge attempt records   |

---

## Setup & Run (Windows)

### Step 1 — Prerequisites
- Python 3.8+ installed
- Visual Studio Code (recommended)

### Step 2 — Open project folder
```
Open DrugFreeCampus\ in VS Code
```

### Step 3 — Create virtual environment
```powershell
python -m venv venv
```

### Step 4 — Activate virtual environment
```powershell
venv\Scripts\activate
```

### Step 5 — Install dependencies
```powershell
pip install -r requirements.txt
```

### Step 6 — Initialise the database
```powershell
python init_db.py
```
This creates `drugfree_campus.db` with all four tables.

### Step 7 — Run the application
```powershell
python app.py
```

### Step 8 — Open in browser
```
http://127.0.0.1:5000
```

---

## Routes

| URL                | Method     | Description                  |
|--------------------|------------|------------------------------|
| `/`                | GET        | Home / landing page          |
| `/register`        | GET, POST  | Student registration         |
| `/login`           | GET, POST  | Student login                |
| `/logout`          | GET        | Logout (clears session)      |
| `/dashboard`       | GET        | Student dashboard            |
| `/awareness`       | GET        | Drug awareness module        |
| `/effects`         | GET        | Effects & risks module       |
| `/decision`        | GET, POST  | Decision challenge           |
| `/quiz`            | GET        | Awareness quiz               |
| `/quiz/submit`     | POST       | Quiz submission & scoring    |
| `/quiz/history`    | GET        | Quiz attempt history         |
| `/healthy`         | GET        | Healthy alternatives         |
| `/anti-ragging`    | GET        | Anti-ragging awareness       |
| `/help`            | GET        | Help & support               |
| `/pledge`          | GET, POST  | Drug-Free pledge             |

---

## Common Issues & Solutions

| Problem                          | Solution                                      |
|----------------------------------|-----------------------------------------------|
| `ModuleNotFoundError: flask`     | Run `pip install -r requirements.txt`         |
| Database not found               | Run `python init_db.py` first                 |
| Port 5000 already in use         | Close other Flask apps or change port in app.py |
| Static files not loading         | Ensure you are running from the project root  |
| Session not persisting           | Check that `SECRET_KEY` is set in app.py      |

---

## Security Notes

- Passwords are hashed using `werkzeug.security.generate_password_hash`
- All database queries use parameterised SQLite statements (no raw string interpolation)
- Flask sessions protect all dashboard/quiz/pledge routes
- Backend validation is applied on all form inputs independent of JavaScript

---

## Content Note

All content in this application is strictly prevention and awareness-oriented.
No information promoting, facilitating, or instructing substance use is included.
All helpline numbers displayed are official published sources.

---

*DrugFree Campus — Educate. Prevent. Stay Safe. Choose a Drug-Free Future.*
