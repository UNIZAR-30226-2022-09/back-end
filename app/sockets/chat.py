from random import sample
from datetime import datetime
from venv import create
from app import app, db
from app.models import Chat, UserSid, chatRoom
from flask import Blueprint, jsonify, session, request
from flask_cors import CORS
from app.user.main import token_required
from flask_socketio import SocketIO, send, join_room,leave_room, emit

CORS(app,cors_allowed_origins="*")
socketio = SocketIO(app, cors_allowed_origins="*")


chatsBp = Blueprint('chats',__name__)

# Funcion socket por cada mensaje que se mande

@socketio.on('message')
def chat(message):
    
    print(message)
    print(request.sid)
    
    created_at = datetime.now()
    nick = message['user']
    mensaje = message['message']
    room = message['sala']
    
    chat_message = Chat(nick=nick, created_at = created_at, message=mensaje, room=room)
    db.session.add(chat_message)
    db.session.commit()

    print(room)
    emit('message',(mensaje,nick), broadcast=True, to=room)

@socketio.on('disconnect')
def disconnect():
    print("User left to Socket")

@socketio.on('connect')
def disconnect():
    print("User Added to Socket")

# Funcion para almacenar por cada Usuario un SocketID único en esa sesion
# que cambiará a traves de las diferentes sesiones que pueda tener

@socketio.on('join')
def on_join(data):
    join_room(data['room'])
    emit('join' , 'A user has entered the room.', to=data['room'])
    print(type(data['room']))
    addRoomSession(data['room'])

def addRoomSession(room):
    if 'rooms' not in session:
        session['rooms'] = []

    rooms = session['rooms']
    rooms.append(room)
    session['rooms'] = rooms
    print(session['rooms'])

@socketio.on('leave')
def on_leave(data):
    leave_room(data['room'])
    emit('leave' , 'A user has left the room.', to=data['room'])    
    print(type(data['room']))
    removeRoomSession(data['room'])

def removeRoomSession(room):

    rooms = session['rooms']

    rooms.remove(room)
    session['rooms'] = rooms
    print('salas activas: {}'.format(session['rooms']))

# Funcion para cargar todos los chat que un usuario tiene abierto

@app.route("/chat", methods=['GET'])
@token_required
def load_chat(current_user):
    current_user = request.headers['current_user']
    list_users = []

    users = chatRoom.query.filter_by(user1 = current_user).all()                # Cargamos las salas donde el usuario figura como 1
    for user in users:
        if user.user1 == current_user:
            list_users.append(user.user2)
        else:
            list_users.append(user.user1)

    users = chatRoom.query.filter_by(user2 = current_user).all()                # Cargamos las salas donde el usuario figura como 2
    for user in users:
        if user.user1 == current_user:
            list_users.append(user.user2)
        else:
            list_users.append(user.user1)
    
    print(list_users)    
    return jsonify(list_users)

@app.route("/new_chat",methods=['GET'])
def new_chat():
    
    userOrigin = request.headers['userOrigin']              # Cambiar al metodo de recibir el usuario origen.
    userDest = request.headers['userDest']                  # Cambiar la metodo de recibir el usuario destino.
    print(userOrigin)
    print(userDest)
    randomNumber = sample(range(10,99999),1)
    print(randomNumber[0])

    if check_room(userOrigin,userDest):
        NewRoom = chatRoom(roomid = randomNumber[0],user1=userOrigin, user2=userDest)
        db.session.add(NewRoom)
        db.session.commit()
        return str(randomNumber[0])
    else:
        roomId = getRoom(userOrigin,userDest)
        return str(roomId)

# Cargamos las conversaciones de una sala

@app.route("/private/<string:roomId>",methods=['GET'])
def index(roomId):
     
    print('Se ha unido a la sala {}'.format(roomId))
    
    messages = Chat.query.filter_by(room = roomId).order_by(Chat.created_at.desc()).all()
    messagelist = []
    for i in messages:
        message = {
            'nick' : i.nick,
            'message' : i.message,
            'created_at' : i.created_at
        }
        messagelist.append(message)
 
    return jsonify(messagelist)

# Comprobamos que no exista una room con ambos usuarios dentro

def check_room(userOrigin,userDest):
    room = chatRoom.query.filter_by(user1 = userOrigin , user2=userDest).first()
    if room is None:
        room = chatRoom.query.filter_by(user2 = userOrigin , user1=userDest).first()
        if room is None:
            return True
        else: 
            return False
    else:
        return False

# Devuelve el sid del usuario que 

def checkReceiver(sid):
    receiver = UserSid.query.filter_by(Sid=sid).first()
    return receiver.User

def getRoom(userOrigin, userDest):
    chat = chatRoom.query.filter_by(user1 = userOrigin , user2=userDest).first()
    if chat is None:
        chat = chatRoom.query.filter_by(user2 = userOrigin , user1=userDest).first()
        return chat.roomid
    else:
        return chat.roomid