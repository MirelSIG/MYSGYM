from flask import Blueprint, render_template

frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route("/")
def home():
    return render_template("home.html")

@frontend_bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@frontend_bp.route("/entity/<name>")
def entity(name):
    return render_template("entity.html", entity=name)

@frontend_bp.route("/login")
def login():
    return render_template("login.html")
