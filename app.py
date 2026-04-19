from flask import Flask, render_template, request, redirect, session
import sqlite3
import string
import random

app = Flask(__name__)
app.secret_key = "spectralearn"

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT,
            password TEXT,
            role TEXT,
            theme TEXT,
            font_size TEXT,
            font_family TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= HOME =================
@app.route("/")
def home():
    return render_template("home.html")

# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username").strip()
        email = request.form.get("email").strip()
        password = request.form.get("password").strip()
        role = request.form.get("role").strip().lower()

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
            (username, email, password, role)
        )

        conn.commit()

        conn.close()

        return redirect("/login")

    return render_template("register.html")

# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        print("LOGIN INPUT:", username, password)

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # 🔍 SHOW ALL USERS
        cursor.execute("SELECT username, password, role FROM users")
        print("ALL USERS:", cursor.fetchall())

        # 🔍 CHECK MATCH
        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()
        print("MATCH RESULT:", user)

        conn.close()

        if user:
            session["user"] = user[1]
            session["role"] = user[4]

            # ✅ SETTINGS APPLY HERE
            session["theme"] = user[5] if user[5] else ""
            session["font_size"] = user[6] if user[6] else ""
            session["font_family"] = user[7] if user[7] else ""

            print("SESSION SET:", session["theme"], session["font_size"], session["font_family"])

            return redirect("/dashboard")

        else:
            return "Invalid credentials"

    return render_template("login.html")

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    letter_progress = session.get("letter_progress", 0)
    number_progress = session.get("number_progress", 0)

    letter_percent = int((letter_progress / 26) * 100) if letter_progress else 0
    number_percent = int((number_progress / 20) * 100) if number_progress else 0

    word_progress = session.get("word_progress", 0)
    word_percent = int((word_progress / 26) * 100) if word_progress else 0

    return render_template(
        "dashboard.html",
        user=session["user"],
        role=session["role"],
        letter_percent=letter_percent,
        number_percent=number_percent,
        word_percent=word_percent
    )

# ================= ALPHABET =================
LETTERS = list(string.ascii_uppercase)

@app.route("/learning")
def learning():
    if "user" not in session:
        return redirect("/login")

    alphabet_data = [
        ("A","a","apple.jpg"), ("B","b","ball.jpg"), ("C","c","cat.jpg"),
        ("D","d","dog.jpg"), ("E","e","elephant.jpg"), ("F","f","fish.jpg"),
        ("G","g","grapes.jpg"), ("H","h","hat.jpg"), ("I","i","icecream.jpg"),
        ("J","j","juice.jpg"), ("K","k","kite.jpg"), ("L","l","lion.jpg"),
        ("M","m","monkey.jpg"), ("N","n","nest.jpg"), ("O","o","orange.jpg"),
        ("P","p","parrot.jpg"), ("Q","q","queen.jpg"), ("R","r","rabbit.jpg"),
        ("S","s","sun.jpg"), ("T","t","tiger.jpg"), ("U","u","umbrella.jpg"),
        ("V","v","van.jpg"), ("W","w","watch.jpg"), ("X","x","xylophone.jpg"),
        ("Y","y","yacht.jpg"), ("Z","z","zebra.jpg"),
    ]

    page = int(request.args.get("page", 0))

    start = page * 3
    end = start + 3

    current_letters = alphabet_data[start:end]

    # progress
    session["letter_progress"] = min(end, len(alphabet_data))

    next_page = page + 1 if end < len(alphabet_data) else None

    return render_template(
        "learning.html",
        letters=current_letters,
        next_page=next_page
    )

@app.route("/word_builder")
def word_builder():

    if "user" not in session:
        return redirect("/login")

    # ✅ ONLY THIS LIST (A–Z)
    words = [
        ("A","Apple","apple.jpg"), ("B","Ball","ball.jpg"),
        ("C","Cat","cat.jpg"), ("D","Dog","dog.jpg"),
        ("E","Elephant","elephant.jpg"), ("F","Fish","fish.jpg"),
        ("G","Grapes","grapes.jpg"), ("H","Hat","hat.jpg"),
        ("I","Ice Cream","icecream.jpg"), ("J","Juice","juice.jpg"),
        ("K","Kite","kite.jpg"), ("L","Lion","lion.jpg"),
        ("M","Monkey","monkey.jpg"), ("N","Nest","nest.jpg"),
        ("O","Orange","orange.jpg"), ("P","Parrot","parrot.jpg"),
        ("Q","Queen","queen.jpg"), ("R","Rabbit","rabbit.jpg"),
        ("S","Sun","sun.jpg"), ("T","Tiger","tiger.jpg"),
        ("U","Umbrella","umbrella.jpg"), ("V","Van","van.jpg"),
        ("W","Watch","watch.jpg"), ("X","Xylophone","xylophone.jpg"),
        ("Y","Yacht","yacht.jpg"), ("Z","Zebra","zebra.jpg"),
    ]

    # 🔥 DEBUG (IMPORTANT)
    print("WORDS COUNT:", len(words))

    page = int(request.args.get("page", 0))

    start = page * 3
    end = start + 3

    current_words = words[start:end]

    next_page = page + 1 if end < len(words) else None

    return render_template(
        "word_builder.html",
        words=current_words,
        next_page=next_page
    )

# ================= WORD ACTIVITY =================
@app.route("/word_activity")
def word_activity():

    if "user" not in session:
        return redirect("/login")

    # ✅ reset session first time
    if "q_count" not in session:
        session["q_count"] = 0
        session["score"] = 0
        session["used_questions"] = []

    words = [
        ("A","Apple","apple.jpg"), ("B","Ball","ball.jpg"),
        ("C","Cat","cat.jpg"), ("D","Dog","dog.jpg"),
        ("E","Elephant","elephant.jpg"), ("F","Fish","fish.jpg"),
    ]

    # ✅ avoid repeating questions
    remaining = [w for w in words if w[1] not in session["used_questions"]]

    if not remaining:
        session["used_questions"] = []
        remaining = words.copy()

    question = random.choice(remaining)
    session["used_questions"].append(question[1])

    # ✅ ensure correct answer is included
    remaining_words = [w for w in words if w != question]
    wrong_options = random.sample(remaining_words, 2)
    options = wrong_options + [question]
    random.shuffle(options)
    

    return render_template(
        "word_activity.html",
        correct_word=question[1],
        correct_image=question[2],
        options=options,
        score=session["score"]
    )


@app.route("/check_word_answer", methods=["POST"])
def check_word_answer():

    selected = request.form.get("selected")
    correct = request.form.get("correct_word")

    if selected == correct:
        session["score"] += 1

    session["q_count"] += 1

    # ✅ after 5 questions → result
    if session["q_count"] >= 5:
        score = session["score"]

        session.pop("q_count", None)
        session.pop("score", None)
        session.pop("used_questions", None)

        return render_template("word_result.html", score=score)

    return redirect("/word_activity")
# ================= NUMBERS =================
@app.route("/numbers")
def numbers():
    if "user" not in session:
        return redirect("/login")

    number_data = [
        (1,"One"), (2,"Two"), (3,"Three"), (4,"Four"), (5,"Five"),
        (6,"Six"), (7,"Seven"), (8,"Eight"), (9,"Nine"), (10,"Ten"),
        (11,"Eleven"), (12,"Twelve"), (13,"Thirteen"), (14,"Fourteen"), (15,"Fifteen"),
        (16,"Sixteen"), (17,"Seventeen"), (18,"Eighteen"), (19,"Nineteen"), (20,"Twenty"),
    ]

    page = int(request.args.get("page", 0))

    start = page * 10
    end = start + 10

    current_numbers = number_data[start:end]

    session["number_progress"] = min(end, len(number_data))

    next_page = page + 1 if end < len(number_data) else None

    return render_template(
        "numbers.html",
        numbers=current_numbers,
        next_page=next_page
    )

# ================= EMOTIONS MODULE =================
@app.route("/emotions")
def emotions():

    if "user" not in session:
        return redirect("/login")

    emotions_list = [
        ("Happy", "happy.png"),
        ("Sad", "sad.png"),
        ("Angry", "angry.png"),
        ("Surprised", "surprised.png"),
        ("Scared", "scared.png"),
        ("Excited", "excited.png"),
        ("shy", "shy.png"),
        ("Bored" , "bored.png")
        
    ]

    return render_template("emotions.html", emotions=emotions_list)



# ================= TEACHER DASHBOARD =================
@app.route("/teacher_dashboard")
def teacher_dashboard():
    if "user" not in session or session.get("role") != "teacher":
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT username, email FROM users WHERE role='student'")
    students = cursor.fetchall()

    conn.close()

    return render_template("teacher_dashboard.html", students=students)

# ================= EDIT STUDENT =================
@app.route("/edit_student/<username>")
def edit_student(username):

    if "user" not in session or session.get("role") != "teacher":
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    student = cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (username,)
    ).fetchone()

    conn.close()

    return render_template(
        "edit_student.html",
        username=student[1],
        email=student[2]
    )# ================= UPDATE STUDENT SETTINGS =================
@app.route("/update_student_settings/<username>", methods=["POST"])
def update_student_settings(username):

    if "user" not in session or session.get("role") != "teacher":
        return redirect("/login")

    theme = request.form.get("theme")
    font_size = request.form.get("font_size")
    font_family = request.form.get("font_family")

    # 🔥 ADD DEBUG HERE
    print("UPDATING:", username, theme, font_size, font_family)

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET theme=?, font_size=?, font_family=?
        WHERE username=?
    """, (theme, font_size, font_family, username))

    conn.commit()
    conn.close()

    return redirect("/teacher_dashboard")

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
DELETE FROM users
WHERE rowid NOT IN (
    SELECT MIN(rowid)
    FROM users
    GROUP BY username
)
""")

conn.commit()
conn.close()
# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
