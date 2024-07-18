from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'your_secret_key'

db = SQLAlchemy(app)

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password

@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        session["secret"] = False
        first = request.form.get("first_name")
        last = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        exists = Account.query.filter_by(email=email).first()
        
        result = password == confirm_password

        if exists:
            return render_template("index.html", message="Email already in use")

        if not (first and last and email and password and confirm_password):
            return redirect(url_for("index"))

        if result:
            # Create a new account instance and add it to the database
            new_user = Account(first, last, email, password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("thank_you"))
        else:
            return render_template("index.html", message="Password does not match")

    return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def login():

    session["secret"] = False

    if request.method == "POST":
        name = request.form.get("first_name")
        password = request.form.get("password")

        user = Account.query.filter_by(first_name=name, password=password).first()

        if name == "secret" and password == "secret":
            session["secret"] = True
            return redirect(url_for("secret"))
        elif user:
            return redirect(url_for("sign"))
        else:
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/thankyou", methods=["POST", "GET"])
def thank_you():
    if request.method == "POST":
        return redirect(url_for("login"))

    return render_template("thankyou.html")

@app.route("/sign", methods=["POST", "GET"])
def sign():
    return render_template("sign.html")

@app.route("/secret", methods=["GET", "POST"])
def secret():
    if not session.get("secret"):
        return redirect(url_for("login"))  # Redirect to login if session variable is not set
    
    if request.method == "POST":
        session["secret"] = False
        return redirect(url_for("login"))

    return render_template("secretPage.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
