from app import app, socketio
from flask import Blueprint, request
from flask_socketio import emit

chatsBp = Blueprint('chats',__name__)

session_userlist = []

@socketio.on('message')
@app.route("/chat")
def message(message):
    print(request.sid)
    emit('message', message)

@socketio.on('username')
def receive_username(username):
    session_userlist.append({username:request.sid})
    for user in session_userlist:
        print(user)
    
