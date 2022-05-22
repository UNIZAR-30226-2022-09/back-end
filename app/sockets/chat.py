from optparse import check_choice
from random import sample

from sqlalchemy import exc, true
from app import app, db, socketio
from app.models import UserSid, chatRoom
from flask import Blueprint, request
from flask_socketio import emit

chatsBp = Blueprint('chats',__name__)

@socketio.on('message')
def message(message):
    print(request.sid)
    emit('message', message)


# Funcion para almacenar por cada Usuario un SocketID único en esa sesion
# que cambiará a traves de las diferentes sesiones que pueda tener.

@socketio.on('username')
def receive_username(username):

    requestedUser = UserSid.query.filter_by(User=username).first()
    UsersockID = UserSid(Sid=request.sid,User=username)

    if requestedUser is None:
        db.session.add(UsersockID)
        db.session.commit()
    else:  
        db.session.delete(requestedUser)
        db.session.commit()
        
        db.session.add(UsersockID)
        db.session.commit()

@app.route("/new_chat",methods=['POST'])
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
        return "Room Added"
    else:
        return "Room Already registered"

@app.route("/private/<string:userDest>",methods=['GET'])
def index(userDest):
    print(userDest)
    userOrigin = request.headers['userOrigin']
    print(userOrigin)
    
    roomId = check_private(userOrigin,userDest)    
    
    return str(roomId)

# Comprobamos que no exista una room con ambos usuarios dentro

def check_room(userOr,userDest):
    room = chatRoom.query.filter_by(user1 = userOr , user2=userDest).first()
    print(room)
    if room is None:
        room = chatRoom.query.filter_by(user2 = userOr , user1=userDest).first()
        print(room.roomid)
        if room is None:
            return True
        else: 
            return False
    else:
        return False
    
def check_private(userOr,userDest):
    room = chatRoom.query.filter_by(user1 = userOr , user2=userDest).first()
    if room is None:
        room = chatRoom.query.filter_by(user2 = userOr , user1=userDest).first()
        return room.roomid
    else:
        return room.roomid