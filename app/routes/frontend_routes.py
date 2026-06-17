from flask import Blueprint, render_template

frontend = Blueprint('frontend', __name__)

@frontend.route("/")
def home():
    return render_template("home.html")

@frontend.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@frontend.route("/entity/<name>")
def entity(name):
    return render_template("entity.html", entity=name)

@frontend.route("/login")
def login():
    return render_template("login.html")
