from flask import Flask, render_template_string, request, redirect, session
from flask_sqlalchemy import SQLAlchemy # pyright: ignore[reportMissingImports]

app = Flask(__name__)
app.secret_key = "library_secret"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///library.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ------------------ MODELS ------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    role = db.Column(db.String(10))

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    author = db.Column(db.String(100))
    image = db.Column(db.String(300))
    available = db.Column(db.Boolean, default=True)

# ------------------ INIT DB ------------------
def setup_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username="admin").first():
            db.session.add(User(username="admin", password="admin123", role="admin"))
            db.session.commit()

# ------------------ AUTH ------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(
            username=request.form["username"],
            password=request.form["password"],
            role=request.form["role"]
        ).first()
        if user:
            session["user"] = user.username
            session["role"] = user.role
            return redirect("/dashboard")
    return render_template_string(LOGIN_HTML)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        db.session.add(User(
            username=request.form["username"],
            password=request.form["password"],
            role="student"
        ))
        db.session.commit()
        return redirect("/")
    return render_template_string(REGISTER_HTML)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ------------------ DASHBOARD ------------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    books = Book.query.all()
    return render_template_string(DASHBOARD_HTML, books=books, role=session["role"])

# ------------------ ADMIN CRUD ------------------
@app.route("/add", methods=["POST"])
def add_book():
    if session.get("role") == "admin":
        db.session.add(Book(
            title=request.form["title"],
            author=request.form["author"],
            image=request.form["image"]
        ))
        db.session.commit()
    return redirect("/dashboard")

@app.route("/edit/<int:id>", methods=["POST"])
def edit_book(id):
    if session.get("role") == "admin":
        book = Book.query.get(id)
        book.title = request.form["title"]
        book.author = request.form["author"]
        book.image = request.form["image"]
        db.session.commit()
    return redirect("/dashboard")

@app.route("/delete/<int:id>")
def delete_book(id):
    if session.get("role") == "admin":
        Book.query.filter_by(id=id).delete()
        db.session.commit()
    return redirect("/dashboard")

# ------------------ STUDENT ACTIONS ------------------
@app.route("/issue/<int:id>")
def issue(id):
    if session.get("role") == "student":
        book = Book.query.get(id)
        book.available = False
        db.session.commit()
    return redirect("/dashboard")

@app.route("/return/<int:id>")
def return_book(id):
    if session.get("role") == "student":
        book = Book.query.get(id)
        book.available = True
        db.session.commit()
    return redirect("/dashboard")

# ------------------ HTML + CSS ------------------
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Library Login</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body{
background:linear-gradient(120deg,#667eea,#764ba2);
}
.card{
border-radius:15px;
}
</style>
</head>
<body class="d-flex justify-content-center align-items-center vh-100">
<div class="card p-4 shadow" style="width:360px">
<h3 class="text-center mb-3">📚 Library Login</h3>
<form method="post">
<input class="form-control mb-2" name="username" placeholder="Username" required>
<input class="form-control mb-2" type="password" name="password" placeholder="Password" required>
<select class="form-control mb-3" name="role">
<option value="student">Student</option>
<option value="admin">Admin</option>
</select>
<button class="btn btn-primary w-100">Login</button>
</form>
<p class="text-center mt-2">
<a href="/register">New Student? Register</a>
</p>
</div>
</body>
</html>
"""

REGISTER_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Register</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light d-flex justify-content-center align-items-center vh-100">
<div class="card p-4 shadow" style="width:360px">
<h4 class="text-center">Student Registration</h4>
<form method="post">
<input class="form-control mb-2" name="username" placeholder="Username" required>
<input class="form-control mb-3" type="password" name="password" placeholder="Password" required>
<button class="btn btn-success w-100">Register</button>
</form>
</div>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Dashboard</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
.card:hover{
transform:scale(1.03);
transition:.3s;
}
img{
height:220px;
object-fit:cover;
}
</style>
</head>
<body>

<nav class="navbar navbar-dark bg-dark px-3">
<span class="navbar-brand">📖 Library Management</span>
<a href="/logout" class="btn btn-danger">Logout</a>
</nav>

<div class="container mt-4">

{% if role=="admin" %}
<div class="card p-3 mb-4 shadow">
<h5>Add New Book</h5>
<form method="post" action="/add" class="row g-2">
<div class="col-md-4"><input class="form-control" name="title" placeholder="Title" required></div>
<div class="col-md-4"><input class="form-control" name="author" placeholder="Author" required></div>
<div class="col-md-4"><input class="form-control" name="image" placeholder="Image URL"></div>
<button class="btn btn-primary">Add Book</button>
</form>
</div>
{% endif %}

<div class="row g-4">
{% for book in books %}
<div class="col-md-4 col-sm-6">
<div class="card shadow h-100">
<img src="{{book.image or 'https://via.placeholder.com/300'}}" class="card-img-top">
<div class="card-body">
<h5>{{book.title}}</h5>
<p class="text-muted">{{book.author}}</p>

{% if role=="admin" %}
<form method="post" action="/edit/{{book.id}}">
<input class="form-control mb-1" name="title" value="{{book.title}}">
<input class="form-control mb-1" name="author" value="{{book.author}}">
<input class="form-control mb-2" name="image" value="{{book.image}}">
<button class="btn btn-warning btn-sm">Update</button>
<a href="/delete/{{book.id}}" class="btn btn-danger btn-sm">Delete</a>
</form>
{% else %}
{% if book.available %}
<a href="/issue/{{book.id}}" class="btn btn-success w-100">Issue</a>
{% else %}
<a href="/return/{{book.id}}" class="btn btn-secondary w-100">Return</a>
{% endif %}
{% endif %}

</div>
</div>
</div>
{% endfor %}
</div>
</div>
</body>
</html>
"""

# ------------------ RUN ------------------
if __name__ == "__main__":
    setup_db()
    app.run(debug=True)
