from flask import Flask, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "library_secret_key"

# ================= DATABASE =================
def get_db():
    return sqlite3.connect("library.db", check_same_thread=False)

def init_db():
    con = get_db()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        author TEXT
    )
    """)

    con.commit()
    con.close()

init_db()

# ================= CSS =================
css = """
<style>
body{
    font-family: Arial;
    background: linear-gradient(120deg,#4facfe,#00f2fe);
    display:flex;
    justify-content:center;
    align-items:center;
    height:100vh;
}
.container{
    background:white;
    padding:30px;
    width:380px;
    border-radius:12px;
    text-align:center;
    box-shadow:0 10px 25px rgba(0,0,0,0.2);
}
input,select,button{
    width:100%;
    padding:10px;
    margin:8px 0;
}
button{
    background:#4facfe;
    border:none;
    color:white;
    font-size:16px;
    border-radius:6px;
}
a{display:block;margin-top:10px;text-decoration:none;color:#4facfe;}
ul{list-style:none;padding:0;}
li{background:#eee;padding:8px;margin:5px;border-radius:5px;}
</style>
"""

# ================= HOME =================
@app.route("/")
def home():
    return css + """
    <div class="container">
        <h2>Library Management System</h2>
        <a href="/register">Register</a>
        <a href="/login/student">Student Login</a>
        <a href="/login/admin">Admin Login</a>
    </div>
    """

# ================= REGISTER =================
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        password = request.form["password"].strip()
        role = request.form["role"].strip()

        try:
            con = get_db()
            con.execute(
                "INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)",
                (name,email,password,role)
            )
            con.commit()
            con.close()
            return redirect("/")
        except Exception as e:
            return css + f"<div class='container'><h3>User already exists</h3><a href='/register'>Back</a></div>"

    return css + """
    <div class="container">
        <h3>Register</h3>
        <form method="post">
            <input name="name" placeholder="Name" required>
            <input name="email" placeholder="Email" required>
            <input type="password" name="password" placeholder="Password" required>
            <select name="role">
                <option value="student">Student</option>
                <option value="admin">Admin</option>
            </select>
            <button>Register</button>
        </form>
        <a href="/">Back</a>
    </div>
    """

# ================= STUDENT LOGIN =================
@app.route("/login/student", methods=["GET","POST"])
def student_login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        con = get_db()
        cur = con.cursor()
        cur.execute(
            "SELECT * FROM users WHERE email=? AND password=? AND role='student'",
            (email,password)
        )
        user = cur.fetchone()
        con.close()

        if user:
            session["student"] = user[1]
            return redirect("/student")

        return css + "<div class='container'><h3>Invalid Student Login</h3><a href='/login/student'>Try Again</a></div>"

    return css + """
    <div class="container">
        <h3>Student Login</h3>
        <form method="post">
            <input name="email" placeholder="Email">
            <input type="password" name="password" placeholder="Password">
            <button>Login</button>
        </form>
        <a href="/">Back</a>
    </div>
    """

# ================= ADMIN LOGIN =================
@app.route("/login/admin", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        con = get_db()
        cur = con.cursor()
        cur.execute(
            "SELECT * FROM users WHERE email=? AND password=? AND role='admin'",
            (email,password)
        )
        admin = cur.fetchone()
        con.close()

        if admin:
            session["admin"] = admin[1]
            return redirect("/admin")

        return css + "<div class='container'><h3>Invalid Admin Login</h3><a href='/login/admin'>Try Again</a></div>"

    return css + """
    <div class="container">
        <h3>Admin Login</h3>
        <form method="post">
            <input name="email" placeholder="Email">
            <input type="password" name="password" placeholder="Password">
            <button>Login</button>
        </form>
        <a href="/">Back</a>
    </div>
    """

# ================= ADMIN DASHBOARD =================
@app.route("/admin", methods=["GET","POST"])
def admin():
    if "admin" not in session:
        return redirect("/")

    if request.method == "POST":
        title = request.form["title"].strip()
        author = request.form["author"].strip()
        con = get_db()
        con.execute(
            "INSERT INTO books (title,author) VALUES (?,?)",
            (title,author)
        )
        con.commit()
        con.close()

    books = get_db().execute("SELECT * FROM books").fetchall()

    return css + f"""
    <div class="container">
        <h3>Admin Dashboard</h3>
        <form method="post">
            <input name="title" placeholder="Book Title">
            <input name="author" placeholder="Author">
            <button>Add Book</button>
        </form>
        <ul>
            {''.join([f"<li>{b[1]} by {b[2]}</li>" for b in books])}
        </ul>
        <a href="/logout">Logout</a>
    </div>
    """

# ================= STUDENT DASHBOARD =================
@app.route("/student")
def student():
    if "student" not in session:
        return redirect("/")

    books = get_db().execute("SELECT * FROM books").fetchall()

    return css + f"""
    <div class="container">
        <h3>Student Dashboard</h3>
        <ul>
            {''.join([f"<li>{b[1]} by {b[2]}</li>" for b in books])}
        </ul>
        <a href="/logout">Logout</a>
    </div>
    """

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
