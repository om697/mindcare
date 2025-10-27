from flask import Flask, render_template, request, redirect, url_for, session
import json, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "mindcare_secret"

# Create users file if not exists
if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump({}, f)

# ---------- ROUTES ---------- #

@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("home"))  # Direct to options/dashboard
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        with open("users.json", "r") as f:
            users = json.load(f)

        if username in users and users[username]["password"] == password:
            session["user"] = username
            return redirect(url_for("home"))  # Directly to dashboard
        return "Invalid credentials!"
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        with open("users.json", "r") as f:
            users = json.load(f)

        if username in users:
            return "Username already exists!"
        users[username] = {"password": password, "moods": [], "assessments": []}
        with open("users.json", "w") as f:
            json.dump(users, f, indent=4)
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/home")
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("home.html", username=session["user"])

# ---------- Self Assessment ----------
@app.route("/self_assessment", methods=["GET", "POST"])
def self_assessment():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]
    with open("users.json", "r") as f:
        users = json.load(f)
    user_data = users.get(username, {"assessments": [], "moods": []})

    if request.method == "POST":
        # Gather form data
        sleep = int(request.form.get("sleep_hours", 0))
        work = int(request.form.get("work_hours", 0))
        questions = ["q1","q2","q3","q4","q5"]
        score = sum(int(request.form.get(q,0)) for q in questions)

        # Unique scoring modifiers
        if sleep < 6: score += 2
        if work > 10: score += 2

        # Generate suggestion
        if score <= 4:
            suggestion = "You seem mentally healthy. Keep up your habits!"
        elif score <= 8:
            suggestion = "You might be a bit stressed. Try meditation and rest."
        else:
            suggestion = "You seem quite stressed. Take a break or talk to a counselor."

        # Save assessment
        user_data.setdefault("assessments", []).append({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "score": score,
            "sleep": sleep,
            "work": work,
            "suggestion": suggestion
        })
        users[username] = user_data
        with open("users.json", "w") as f:
            json.dump(users, f, indent=4)

        return render_template("result.html", score=score, suggestion=suggestion)

    return render_template("self_assessment.html")
# ---------- Mood Tracking ----------
@app.route("/mood_tracking", methods=["GET", "POST"])
def mood_tracking():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]
    with open("users.json", "r") as f:
        users = json.load(f)
    user_data = users.get(username, {"moods": [], "assessments": []})

    if request.method == "POST":
        mood = request.form.get("mood", "")
        today = datetime.now().strftime("%Y-%m-%d %H:%M")
        user_data.setdefault("moods", []).append({"date": today, "mood": mood})
        users[username] = user_data
        with open("users.json", "w") as f:
            json.dump(users, f, indent=4)

    return render_template("mood_tracking.html", moods=user_data.get("moods", []))

# ---------- Booking ----------
@app.route("/booking", methods=["GET", "POST"])
def booking():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        date = request.form.get("date")
        time = request.form.get("time")
        message = request.form.get("message")
        return f"Booking confirmed for {date} at {time}. Message: {message}"

    return render_template("booking.html")

# ---------- Tips ----------
@app.route("/tips")
def tips():
    if "user" not in session:
        return redirect(url_for("login"))

    tips_data = [
        {
            "title": "🌞 Morning Mindset",
            "description": "Start each day by setting one small positive intention. Even 5 minutes of calm focus can shape your whole day.",
            "image": "https://cdn.pixabay.com/photo/2020/03/14/13/28/sunrise-4939763_1280.jpg"
        },
        {
            "title": "🧘 Mindful Breathing",
            "description": "Inhale for 4 seconds, hold for 4, exhale for 6. Repeat 5 times to lower anxiety and reset your focus.",
            "image": "https://cdn.pixabay.com/photo/2016/11/21/15/53/yoga-1842292_1280.jpg"
        },
        {
            "title": "🌿 Connect with Nature",
            "description": "Spend at least 10 minutes outdoors — sunlight and greenery can instantly lift your mood.",
            "image": "https://cdn.pixabay.com/photo/2016/11/29/03/52/forest-1868037_1280.jpg"
        },
        {
            "title": "📓 Gratitude Journaling",
            "description": "Write down 3 things you’re grateful for every evening — it helps your brain focus on positivity.",
            "image": "https://cdn.pixabay.com/photo/2016/11/29/03/16/blur-1867348_1280.jpg"
        },
        {
            "title": "🎶 Music & Relaxation",
            "description": "Play your favorite relaxing playlist and let your mind wander — music heals stress faster than silence.",
            "image": "https://cdn.pixabay.com/photo/2017/02/13/19/46/music-2069829_1280.jpg"
        },
        {
            "title": "💬 Connect with Others",
            "description": "Talk to someone you trust about your feelings. Emotional sharing builds resilience.",
            "image": "https://cdn.pixabay.com/photo/2016/03/27/21/16/friends-1284476_1280.jpg"
        }
    ]
    return render_template("tips.html", tips=tips_data)

# ---------- Logout ----------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))
# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
