from flask import Flask, request, redirect, render_template_string
from flask_sqlalchemy import SQLAlchemy  # pyright: ignore[reportMissingImports]
import os

app = Flask(__name__)

# DB config
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "registrations.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

#MODEL
class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    gender = db.Column(db.String(10))

with app.app_context():
    db.create_all()

#ADD USER (STARTING PAGE)
@app.route("/", methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        user = Registration(
            name=request.form["name"],
            email=request.form["email"],
            phone=request.form["phone"],
            gender=request.form["gender"]
        )
        db.session.add(user)
        db.session.commit()
        return redirect("/list")

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Add</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

<!--ADD PAGE BACKGROUND STYLE -->
<style>
body {
    background-image: url('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQkFfVYsRRSELuO-pPAtBvminDSd1AJjQldgA&s');
    background-size: scroll;
    background-position: center;
    background-attachment: fixed;
}

.overlay {
    background: rgba(255,255,255,0.93);
    padding: 30px;
    border-radius: 15px;
}
</style>
</head>

<body>

<nav class="navbar navbar-dark bg-primary px-3">
  <span class="navbar-brand">Registration System</span>
  <div>
    <a class="btn btn-light btn-sm" href="/">Add</a>
    <a class="btn btn-light btn-sm" href="/list">Users</a>
  </div>
</nav>

<div class="container mt-4">
  <div class="overlay card p-4 col-md-6 mx-auto">
    <h4>Add Registration</h4>
    <form method="post">
      <input class="form-control mb-2" name="name" placeholder="Full Name" required>
      <input class="form-control mb-2" type="email" name="email" placeholder="Email" required>
      <input class="form-control mb-2" name="phone" placeholder="Phone" required>
      <select class="form-control mb-2" name="gender">
        <option>Male</option>
        <option>Female</option>
      </select>
      <button class="btn btn-primary w-100">Save</button>
    </form>
  </div>
</div>

</body>
</html>
""")

#LIST USERS
@app.route("/list")
def list_users():
    users = Registration.query.all()

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Users</title>

<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

<style>
body {
    background-image: url('https://imgs.search.brave.com/aSz79jIWCllZhMpstYKmfdihtasFPDVaHbvtRLrS2vA/rs:fit:500:0:1:0/g:ce/aHR0cHM6Ly9pLnBp/bmltZy5jb20vb3Jp/Z2luYWxzL2JhLzBj/L2UwL2JhMGNlMDBk/YTBlODJjNzc3ZjUz/YzQ5NDhiYmYxYWRj/LmpwZw');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

.overlay {
    background: rgba(255,255,255,0.92);
    padding: 30px;
    border-radius: 15px;
}

.avatar {
    width: 40px;
    border-radius: 50%;
}
</style>
</head>

<body>

<nav class="navbar navbar-dark bg-primary px-3">
  <span class="navbar-brand">Registration System</span>
  <div>
    <a class="btn btn-light btn-sm" href="/">Add</a>
    <a class="btn btn-light btn-sm" href="/list">Users</a>
  </div>
</nav>

<div class="container mt-4">
  <div class="overlay">
    <h4>Registered Users</h4>

    <table class="table table-striped table-hover">
      <thead class="table-primary">
        <tr>
          <th>Image</th>
          <th>Name</th>
          <th>Email</th>
          <th>Phone</th>
          <th>Gender</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {% for u in users %}
        <tr>
          <td><img class="avatar" src="https://i.pravatar.cc/50?img={{ u.id }}"></td>
          <td>{{ u.name }}</td>
          <td>{{ u.email }}</td>
          <td>{{ u.phone }}</td>
          <td>{{ u.gender }}</td>
          <td>
              <a class="btn btn-warning btn-sm" href="/edit/{{ u.id }}">Edit</a>
              <a class="btn btn-danger btn-sm" href="/delete/{{ u.id }}">Delete</a>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>

</body>
</html>
""", users=users)

#EDIT USER
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_user(id):
    user = Registration.query.get_or_404(id)

    if request.method == "POST":
        user.name = request.form["name"]
        user.email = request.form["email"]
        user.phone = request.form["phone"]
        user.gender = request.form["gender"]
        db.session.commit()
        return redirect("/list")

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Edit</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>

<body>

<nav class="navbar navbar-dark bg-primary px-3">
  <span class="navbar-brand">Registration System</span>
  <div>
    <a class="btn btn-light btn-sm" href="/">Add</a>
    <a class="btn btn-light btn-sm" href="/list">Users</a>
  </div>
</nav>

<div class="container mt-4">
  <div class="card p-4 col-md-6 mx-auto">
    <h4>Edit Registration</h4>
    <form method="post">
      <input class="form-control mb-2" name="name" value="{{ user.name }}" required>
      <input class="form-control mb-2" type="email" name="email" value="{{ user.email }}" required>
      <input class="form-control mb-2" name="phone" value="{{ user.phone }}" required>
      <select class="form-control mb-2" name="gender">
        <option {% if user.gender=="Male" %}selected{% endif %}>Male</option>
        <option {% if user.gender=="Female" %}selected{% endif %}>Female</option>
      </select>
      <button class="btn btn-success w-100">Update</button>
    </form>
  </div>
</div>

</body>
</html>
""", user=user)

#DELETE
@app.route("/delete/<int:id>")
def delete_user(id):
    user = Registration.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect("/list")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

