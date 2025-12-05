# Clue & Cue
# app.py
# ---------------- IMPORTS ---------------- #
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room, emit
from game.engine import Room
import os

# ---------------- FLASK CONFIG ---------------- #
app = Flask(__name__)
# Use environment variable on server, or 'dev' for local testing
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev_secret_key")
socketio = SocketIO(app)

# Global dictionary to store active Room objects
# Key: Room Code (str), Value: Room (Object)
ROOMS = {}


# ---------------- ROUTES ---------------- #

@app.route("/")
def index():
    """Renders the Home/Lobby page."""
    return render_template("index.html")


@app.route("/rules")
def rules():
    """Renders the Rules page."""
    return render_template("rules.html")


@app.route("/game/<roomcode>")
def game_ui(roomcode):
    """
    Renders the main Game Interface.
    Checks if the room exists; if not, redirects back to Home.
    """
    if roomcode not in ROOMS:
        return redirect(url_for('index'))
    return render_template("game.html", roomcode=roomcode)


# ---------------- SOCKET.IO EVENTS ---------------- #

@socketio.on("create_room")
def handle_create(data):
    """
    Creates a new game room with a random 4-letter code.
    Adds the creator as the first player.
    """
    username = data.get("username")
    import random, string
    roomcode = ''.join(random.choices(string.ascii_uppercase, k=4))

    new_room = Room(roomcode, username)
    ROOMS[roomcode] = new_room

    emit("room_created", {"roomcode": roomcode})


@socketio.on("join_game")
def handle_join(data):
    """
    Handles a player joining an existing room.
    Associates the socket session ID (sid) with the player for private messaging.
    """
    roomcode = data.get("roomcode")
    username = data.get("username")

    # --- FIX FOR PHANTOM PLAYERS ---
    # Reject connections that don't have a valid username
    if not username or username == 'null':
        emit("error", {"msg": "Username required to join."})
        return
    # -----------------------------

    if roomcode not in ROOMS:
        emit("error", {"msg": "Room not found"})
        return

    room = ROOMS[roomcode]
    player = room.add_player(username)
    player.sid = request.sid  # Save session ID for private messages

    join_room(roomcode)
    # Broadcast new state to everyone in the room so they see the new player
    emit("state_update", room.get_public_state(), to=roomcode)


@socketio.on("start_game")
def handle_start(data):
    """
    Starts the game (moves from LOBBY to SELECTION phase).
    Only the room creator (host) is allowed to trigger this.
    """
    roomcode = data.get("roomcode")
    username = data.get("username")

    if roomcode in ROOMS:
        room = ROOMS[roomcode]

        if room.creator != username:
            emit("error", {"msg": "Only the host can start the game!"})
            return

        success, msg = room.start_selection_phase()
        if success:
            # 1. Update public state (Phase change)
            emit("state_update", room.get_public_state(), to=roomcode)
            # 2. Privately deal 8 cards to each player
            for p in room.players:
                if p.sid:
                    socketio.emit("deal_hand", p.initial_cards, room=p.sid)
        else:
            emit("error", {"msg": msg})


@socketio.on("submit_cards")
def handle_submit(data):
    """
    Receives the 5 chosen cards from a player.
    """
    roomcode = data.get("roomcode")
    username = data.get("username")
    indices = data.get("indices")

    if roomcode in ROOMS:
        room = ROOMS[roomcode]
        room.submit_selection(username, indices)
        emit("state_update", room.get_public_state(), to=roomcode)


@socketio.on("select_giver")
def handle_select_giver(data):
    """
    Captain selects which teammate will give the clues.
    """
    roomcode = data.get("roomcode")
    target_user = data.get("target_user")
    if roomcode in ROOMS:
        ROOMS[roomcode].set_clue_giver(target_user)
        emit("state_update", ROOMS[roomcode].get_public_state(), to=roomcode)


@socketio.on("action_guess")
def handle_guess(data):
    """
    The Clue Giver confirms their team guessed correctly.
    """
    roomcode = data.get("roomcode")
    if roomcode in ROOMS:
        ROOMS[roomcode].guess_correct()
        emit("state_update", ROOMS[roomcode].get_public_state(), to=roomcode)


@socketio.on("action_skip")
def handle_skip(data):
    """
    The Clue Giver skips the current card (only allowed in R2/R3).
    """
    roomcode = data.get("roomcode")
    if roomcode in ROOMS:
        ROOMS[roomcode].skip_card()
        emit("state_update", ROOMS[roomcode].get_public_state(), to=roomcode)


@socketio.on("end_turn")
def handle_end_turn(data):
    """
    Manually ends the turn (or triggered by timer).
    """
    roomcode = data.get("roomcode")
    if roomcode in ROOMS:
        ROOMS[roomcode].end_turn()
        emit("state_update", ROOMS[roomcode].get_public_state(), to=roomcode)


@socketio.on("disconnect")
def handle_disconnect():
    """
    Handles player disconnection.
    """
    pass


if __name__ == "__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)