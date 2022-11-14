import random

from flask import Flask, render_template
from flask_socketio import SocketIO, emit, leave_room
from flask_socketio import join_room
import eventlet

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(
    app,
    cors_allowed_origins=["http://127.0.0.1:5000"],
    async_mode="eventlet",
    engineio_logger=True
)


@socketio.on("join")
def on_join(data):
    room = data["level"]
    join_room(room)
    warnings = ["W0", "W2", "W4", "W6"]
    errors = ["E1", "E3", "E5", "E7"]
    emit("new_logs", warnings if room == "warning" else errors, to=room)


@socketio.on("leave")
def on_leave(data):
    room = data["level"]
    leave_room(room)


@app.route("/", methods=["GET", "POST"])
def show_logs():
    return render_template("logs.html")


def threaded_function():
    while True:
        num = random.randint(0, 100)
        if num % 2 == 0:
            socketio.emit("new_logs", ["W" + str(num)], to="warning")
        else:
            socketio.emit("new_logs", ["E" + str(num)], to="error")
        eventlet.sleep(1)


socketio.start_background_task(threaded_function)
if __name__ == "__main__":
    eventlet.monkey_patch()
    socketio.run(app, debug=False)
