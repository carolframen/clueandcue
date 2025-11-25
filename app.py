# Clue & Cue
# ---------------------------- IMPORTS ------------------------------- #
from flask import Flask, render_template
from flask_socketio import SocketIO
import os


# ---------------------------- CONSTANTS ------------------------------- #



# ---------------------------- SET UP ------------------------------- #
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "dev")
socketio = SocketIO(app)


# ---------------------------- PAGES ------------------------------- #
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/rules")
def rules():
    return render_template("rules.html")

@app.route("/add_username")
def add_username():
    return render_template("add_username.html")














# ---------------------------- RUN ------------------------------- #
if __name__ == "__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)