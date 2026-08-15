"""
app.py
------
DrugFree Campus – Main Flask Application
Run:  python app.py
"""

import os
from functools import wraps
from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, jsonify)
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection

# ---------------------------------------------------------------------------
# App Configuration
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "drugfree_campus_secret_2024_xK9!mP")


# ---------------------------------------------------------------------------
# Login-required decorator
# ---------------------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to access that page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Helper – fetch current user
# ---------------------------------------------------------------------------
def get_current_user():
    if "user_id" not in session:
        return None
    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE user_id = ?", (session["user_id"],)
    ).fetchone()
    conn.close()
    return user


# ===========================================================================
# HOME
# ===========================================================================
@app.route("/")
def index():
    user = get_current_user()
    return render_template("index.html", user=user)


# ===========================================================================
# REGISTER
# ===========================================================================
@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        full_name          = request.form.get("full_name", "").strip()
        email              = request.form.get("email", "").strip().lower()
        username           = request.form.get("username", "").strip().lower()
        password           = request.form.get("password", "")
        confirm_password   = request.form.get("confirm_password", "")
        college_department = request.form.get("college_department", "").strip()

        # --- Backend validation ---
        errors = []
        if not all([full_name, email, username, password, confirm_password, college_department]):
            errors.append("All fields are required.")
        if "@" not in email or "." not in email:
            errors.append("Please enter a valid email address.")
        if len(username) < 3:
            errors.append("Username must be at least 3 characters.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != confirm_password:
            errors.append("Passwords do not match.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("register.html",
                                   full_name=full_name, email=email,
                                   username=username,
                                   college_department=college_department)

        conn = get_db_connection()
        try:
            # Uniqueness checks
            existing_email = conn.execute(
                "SELECT user_id FROM users WHERE email = ?", (email,)
            ).fetchone()
            if existing_email:
                flash("This email is already registered.", "danger")
                conn.close()
                return render_template("register.html",
                                       full_name=full_name, email=email,
                                       username=username,
                                       college_department=college_department)

            existing_username = conn.execute(
                "SELECT user_id FROM users WHERE username = ?", (username,)
            ).fetchone()
            if existing_username:
                flash("This username is already taken.", "danger")
                conn.close()
                return render_template("register.html",
                                       full_name=full_name, email=email,
                                       username=username,
                                       college_department=college_department)

            hashed_pw = generate_password_hash(password)
            conn.execute(
                """INSERT INTO users (full_name, email, username, password, college_department)
                   VALUES (?, ?, ?, ?, ?)""",
                (full_name, email, username, hashed_pw, college_department)
            )
            conn.commit()
            flash("Registration successful! Please login to continue.", "success")
            return redirect(url_for("login"))

        except Exception as e:
            flash("An error occurred during registration. Please try again.", "danger")
            return render_template("register.html")
        finally:
            conn.close()

    return render_template("register.html")


# ===========================================================================
# LOGIN
# ===========================================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip().lower()
        password   = request.form.get("password", "")

        if not identifier or not password:
            flash("Please fill in all fields.", "danger")
            return render_template("login.html")

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?",
            (identifier, identifier)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"]   = user["user_id"]
            session["username"]  = user["username"]
            session["full_name"] = user["full_name"]
            flash(f"Welcome back, {user['full_name'].split()[0]}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username/email or password.", "danger")
            return render_template("login.html")

    return render_template("login.html")


# ===========================================================================
# LOGOUT
# ===========================================================================
@app.route("/logout")
@login_required
def logout():
    name = session.get("full_name", "").split()[0]
    session.clear()
    flash(f"You have been logged out successfully. Stay safe, {name}!", "info")
    return redirect(url_for("index"))


# ===========================================================================
# DASHBOARD
# ===========================================================================
@app.route("/dashboard")
@login_required
def dashboard():
    user = get_current_user()
    uid  = session["user_id"]
    conn = get_db_connection()

    # Quiz stats
    quiz_rows = conn.execute(
        "SELECT percentage, attempted_at FROM quiz_results WHERE user_id = ? ORDER BY attempted_at DESC",
        (uid,)
    ).fetchall()
    quiz_attempts  = len(quiz_rows)
    best_score     = round(max((r["percentage"] for r in quiz_rows), default=0), 1)
    latest_score   = round(quiz_rows[0]["percentage"], 1) if quiz_rows else 0

    # Decision stats
    decision_rows = conn.execute(
        "SELECT score_percentage FROM decision_results WHERE user_id = ? ORDER BY completed_at DESC",
        (uid,)
    ).fetchall()
    decision_attempts = len(decision_rows)
    best_decision     = round(max((r["score_percentage"] for r in decision_rows), default=0), 1)

    # Pledge
    pledge_row = conn.execute(
        "SELECT pledge_status FROM pledge WHERE user_id = ?", (uid,)
    ).fetchone()
    pledge_status = pledge_row["pledge_status"].capitalize() if pledge_row else "Not taken"

    # Awareness progress – simple heuristic
    visited_flags = []
    visited_flags.append(quiz_attempts > 0)
    visited_flags.append(decision_attempts > 0)
    visited_flags.append(pledge_row is not None)
    awareness_pct = round((sum(visited_flags) / 3) * 100)

    conn.close()
    return render_template("dashboard.html",
                           user=user,
                           quiz_attempts=quiz_attempts,
                           best_score=best_score,
                           latest_score=latest_score,
                           decision_attempts=decision_attempts,
                           best_decision=best_decision,
                           pledge_status=pledge_status,
                           awareness_pct=awareness_pct)


# ===========================================================================
# DRUG AWARENESS
# ===========================================================================
@app.route("/awareness")
def awareness():
    user = get_current_user()
    return render_template("awareness.html", user=user)


# ===========================================================================
# EFFECTS & RISKS
# ===========================================================================
@app.route("/effects")
def effects():
    user = get_current_user()
    return render_template("effects.html", user=user)


# ===========================================================================
# DECISION CHALLENGE
# ===========================================================================
SCENARIOS = [
    {
        "id": 1,
        "category": "Peer Pressure",
        "situation": "You are hanging out with a group of friends after college. One of them offers you a cigarette and says, \"Come on, just try it once. It's not a big deal.\" What would you do?",
        "options": [
            {"label": "A", "text": "Accept it to avoid feeling left out."},
            {"label": "B", "text": "Politely but firmly say no and explain you are not interested."},
            {"label": "C", "text": "Take it but pretend to smoke without actually inhaling."},
            {"label": "D", "text": "Stay quiet and hope they stop asking."},
        ],
        "correct": "B",
        "explanation": "Saying no clearly and confidently is the healthiest response. You do not owe anyone an explanation, but being firm prevents further pressure. Real friends will respect your decision.",
        "tip": "Practice saying: \"No thanks, I'm not into that.\" – short, calm, and final."
    },
    {
        "id": 2,
        "category": "Party Pressure",
        "situation": "At a college farewell party, someone hands you a drink and whispers, \"It has something extra in it – makes the night amazing. Everyone's having it.\" What would you do?",
        "options": [
            {"label": "A", "text": "Drink it because everyone else seems to be enjoying it."},
            {"label": "B", "text": "Take it but don't drink, and quietly dispose of it later."},
            {"label": "C", "text": "Refuse clearly, put it down, and move away from that group."},
            {"label": "D", "text": "Ask what's in it and then decide based on the answer."},
        ],
        "correct": "C",
        "explanation": "Never accept drinks with unknown substances. Refusing and moving away protects your safety. \"Something extra\" could be harmful or illegal. Your safety always comes first.",
        "tip": "Trust your instincts. If something feels wrong, it probably is."
    },
    {
        "id": 3,
        "category": "Stress & Unhealthy Coping",
        "situation": "Exam season is stressful and a classmate tells you, \"I use this to stay awake all night and focus. Want some? It really works for studying.\" What would you do?",
        "options": [
            {"label": "A", "text": "Accept it because you are desperate to pass your exams."},
            {"label": "B", "text": "Ask for more details about what it is before deciding."},
            {"label": "C", "text": "Decline, and instead plan a proper study schedule with rest breaks."},
            {"label": "D", "text": "Try a small amount just once to see if it helps."},
        ],
        "correct": "C",
        "explanation": "Using unverified substances to cope with academic stress is dangerous and can lead to dependence. Healthy study habits, proper sleep, and stress management techniques are far more effective and safe.",
        "tip": "Good sleep actually improves memory and exam performance more than all-nighters."
    },
    {
        "id": 4,
        "category": "Risky Group Behavior",
        "situation": "A group of seniors invites you to join them in a hidden corner of campus. You realize they are inhaling something from a plastic bag. They say, \"Relax, it's just for fun. Sit with us.\" What would you do?",
        "options": [
            {"label": "A", "text": "Sit with them to seem cool and fit in with the seniors."},
            {"label": "B", "text": "Watch from a distance without participating."},
            {"label": "C", "text": "Politely excuse yourself, leave immediately, and avoid that area."},
            {"label": "D", "text": "Join them just once so they don't bother you again."},
        ],
        "correct": "C",
        "explanation": "Inhalants are extremely dangerous and can cause serious harm even from a single use. Leaving the situation immediately is the right call. You are not obligated to explain yourself.",
        "tip": "Leaving a risky situation is not weakness – it is smart decision-making."
    },
    {
        "id": 5,
        "category": "Supporting a Friend",
        "situation": "You notice your close friend has been acting differently – missing classes, seeming distracted, and you found an unfamiliar packet in their bag by accident. You are worried. What would you do?",
        "options": [
            {"label": "A", "text": "Ignore it and pretend you didn't notice anything."},
            {"label": "B", "text": "Confront them angrily in front of others."},
            {"label": "C", "text": "Talk to them privately and calmly, expressing your concern and encouraging them to seek support."},
            {"label": "D", "text": "Immediately tell everyone to pressure them into stopping."},
        ],
        "correct": "C",
        "explanation": "A caring, private conversation is the best first step. Express concern without judgment. Encourage professional support or a trusted adult. Anger or public confrontation can push a person further away.",
        "tip": "Say: \"I've noticed you seem different lately and I'm worried about you. I'm here for you.\""
    },
]


@app.route("/decision", methods=["GET", "POST"])
@login_required
def decision():
    user = get_current_user()
    if request.method == "POST":
        answers = {}
        for s in SCENARIOS:
            ans = request.form.get(f"scenario_{s['id']}")
            answers[s["id"]] = ans

        healthy   = sum(1 for s in SCENARIOS if answers.get(s["id"]) == s["correct"])
        total     = len(SCENARIOS)
        score_pct = round((healthy / total) * 100, 1)

        # Build result details
        results = []
        for s in SCENARIOS:
            chosen = answers.get(s["id"])
            is_healthy = (chosen == s["correct"])
            chosen_text = next(
                (o["text"] for o in s["options"] if o["label"] == chosen), "Not answered"
            )
            results.append({
                "id":           s["id"],
                "category":     s["category"],
                "situation":    s["situation"],
                "chosen":       chosen,
                "chosen_text":  chosen_text,
                "is_healthy":   is_healthy,
                "correct":      s["correct"],
                "explanation":  s["explanation"],
                "tip":          s["tip"],
            })

        # Save to DB
        uid = session["user_id"]
        conn = get_db_connection()
        conn.execute(
            """INSERT INTO decision_results (user_id, total_scenarios, healthy_choices, score_percentage)
               VALUES (?, ?, ?, ?)""",
            (uid, total, healthy, score_pct)
        )
        conn.commit()
        conn.close()

        return render_template("decision.html", user=user,
                               scenarios=SCENARIOS,
                               submitted=True,
                               results=results,
                               healthy=healthy,
                               total=total,
                               score_pct=score_pct)

    return render_template("decision.html", user=user,
                           scenarios=SCENARIOS,
                           submitted=False)


# ===========================================================================
# QUIZ
# ===========================================================================
QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "Which of the following is an important way to prevent substance abuse?",
        "options": ["A. Following peer pressure",
                    "B. Ignoring warning signs",
                    "C. Making informed and healthy choices",
                    "D. Hiding problems from others"],
        "answer": "C"
    },
    {
        "id": 2,
        "question": "Why are college students particularly vulnerable to peer pressure around substances?",
        "options": ["A. They are too old to be influenced",
                    "B. Curiosity, stress, desire to fit in, and lack of awareness",
                    "C. They always make fully informed decisions",
                    "D. College campuses have no substance-related issues"],
        "answer": "B"
    },
    {
        "id": 3,
        "question": "What is the healthiest response when someone offers you a harmful substance?",
        "options": ["A. Try it once to see how it feels",
                    "B. Accept it to avoid being judged",
                    "C. Say no firmly and leave if needed",
                    "D. Ask someone else to try it first"],
        "answer": "C"
    },
    {
        "id": 4,
        "question": "Which of these is a healthy way to manage academic stress?",
        "options": ["A. Using substances to stay awake all night",
                    "B. Ignoring the stress completely",
                    "C. Taking regular breaks, exercising, and talking to someone",
                    "D. Skipping classes to avoid stress"],
        "answer": "C"
    },
    {
        "id": 5,
        "question": "Substance misuse can affect a student's academic performance by:",
        "options": ["A. Improving concentration and focus",
                    "B. Reducing motivation, attendance, and grades",
                    "C. Making studying easier",
                    "D. Having no effect on academics"],
        "answer": "B"
    },
    {
        "id": 6,
        "question": "If you are concerned that a friend may be struggling with substance use, what should you do?",
        "options": ["A. Ignore the situation completely",
                    "B. Confront them aggressively in public",
                    "C. Talk to them privately and calmly, and encourage them to seek support",
                    "D. Tell their secrets to everyone"],
        "answer": "C"
    },
    {
        "id": 7,
        "question": "Which of the following is NOT a healthy alternative to cope with stress?",
        "options": ["A. Exercise and sports",
                    "B. Music and creative activities",
                    "C. Using harmful substances",
                    "D. Meditation and mindfulness"],
        "answer": "C"
    },
    {
        "id": 8,
        "question": "What does addiction mean?",
        "options": ["A. A free choice that can be stopped anytime without difficulty",
                    "B. A compulsive dependence on a substance despite harmful consequences",
                    "C. A healthy habit",
                    "D. Something that only affects older adults"],
        "answer": "B"
    },
    {
        "id": 9,
        "question": "Why is it important to seek professional support for substance-related problems?",
        "options": ["A. It is not important at all",
                    "B. Professionals are trained to provide safe, effective help and guidance",
                    "C. Professionals will judge you negatively",
                    "D. Only family members can help"],
        "answer": "B"
    },
    {
        "id": 10,
        "question": "Which statement best describes a drug-free lifestyle?",
        "options": ["A. Avoiding all social situations",
                    "B. Making responsible choices, protecting your health, and encouraging others to do the same",
                    "C. Only avoiding illegal substances but using all others freely",
                    "D. Doing whatever peers suggest"],
        "answer": "B"
    },
]


@app.route("/quiz")
@login_required
def quiz():
    user = get_current_user()
    return render_template("quiz.html", user=user, questions=QUIZ_QUESTIONS)


@app.route("/quiz/submit", methods=["POST"])
@login_required
def quiz_submit():
    answers = {}
    for q in QUIZ_QUESTIONS:
        ans = request.form.get(f"q{q['id']}")
        answers[q["id"]] = ans

    correct = sum(1 for q in QUIZ_QUESTIONS if answers.get(q["id"]) == q["answer"])
    wrong   = len(QUIZ_QUESTIONS) - correct
    pct     = round((correct / len(QUIZ_QUESTIONS)) * 100, 1)

    uid = session["user_id"]
    conn = get_db_connection()
    conn.execute(
        """INSERT INTO quiz_results (user_id, total_questions, correct_answers, wrong_answers, score, percentage)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (uid, len(QUIZ_QUESTIONS), correct, wrong, correct, pct)
    )
    conn.commit()
    conn.close()

    # Build per-question feedback
    feedback = []
    for q in QUIZ_QUESTIONS:
        chosen = answers.get(q["id"])
        feedback.append({
            "id":       q["id"],
            "question": q["question"],
            "options":  q["options"],
            "chosen":   chosen,
            "correct":  q["answer"],
            "is_right": chosen == q["answer"],
        })

    flash("Quiz submitted successfully!", "success")
    return render_template("result.html",
                           user=get_current_user(),
                           total=len(QUIZ_QUESTIONS),
                           correct=correct,
                           wrong=wrong,
                           score=correct,
                           percentage=pct,
                           feedback=feedback)


@app.route("/quiz/result")
@login_required
def quiz_result():
    return redirect(url_for("quiz_history"))


@app.route("/quiz/history")
@login_required
def quiz_history():
    user = get_current_user()
    uid  = session["user_id"]
    conn = get_db_connection()
    rows = conn.execute(
        """SELECT result_id, total_questions, correct_answers, wrong_answers,
                  score, percentage, attempted_at
           FROM quiz_results
           WHERE user_id = ?
           ORDER BY attempted_at DESC""",
        (uid,)
    ).fetchall()
    best = round(max((r["percentage"] for r in rows), default=0), 1)
    conn.close()
    return render_template("quiz_history.html", user=user, rows=rows, best=best)


# ===========================================================================
# HEALTHY CHOICES
# ===========================================================================
@app.route("/healthy")
def healthy():
    user = get_current_user()
    return render_template("healthy.html", user=user)


# ===========================================================================
# ANTI-RAGGING
# ===========================================================================
@app.route("/anti-ragging")
def anti_ragging():
    user = get_current_user()
    return render_template("anti_ragging.html", user=user)


# ===========================================================================
# HELP & SUPPORT
# ===========================================================================
@app.route("/help")
def help_support():
    user = get_current_user()
    return render_template("help.html", user=user)


# ===========================================================================
# PLEDGE
# ===========================================================================
@app.route("/pledge", methods=["GET", "POST"])
@login_required
def pledge():
    user = get_current_user()
    uid  = session["user_id"]
    conn = get_db_connection()
    existing = conn.execute(
        "SELECT * FROM pledge WHERE user_id = ?", (uid,)
    ).fetchone()

    if request.method == "POST":
        if existing:
            flash("You have already taken the pledge.", "info")
        else:
            agreed = request.form.get("pledge_agree")
            if not agreed:
                flash("Please check the checkbox to take the pledge.", "warning")
                conn.close()
                return render_template("pledge.html", user=user, existing=None)
            conn.execute(
                "INSERT INTO pledge (user_id, pledge_status) VALUES (?, 'completed')",
                (uid,)
            )
            conn.commit()
            flash("Thank you for taking the Drug-Free Campus pledge!", "success")
            conn.close()
            return redirect(url_for("pledge"))

    conn.close()
    return render_template("pledge.html", user=user, existing=existing)


# ===========================================================================
# RUN
# ===========================================================================
if __name__ == "__main__":
    app.run(debug=True)
