from app import db
from datetime import datetime
from sqlalchemy import  Integer
from flask import Blueprint

modelsBp = Blueprint('models',__name__)

# USUARIO

class Usuario(db.Model):
    __tablename__ = "usuario"

    nick = db.Column(db.String(20), primary_key=True)                                               # Nick usuario
    Nombre_de_usuario = db.Column(db.String(50))                                                    # Nombre Usuario
    password = db.Column(db.String(50))                                                             # Contraseña
    e_mail = db.Column(db.String(50), unique=True, nullable=False)                                  # E-mail
    descripcion  = db.Column(db.String(1000))                                                       # Descripcion del Usuario
    link  = db.Column(db.String(200))                                                               # Link interés Usuario
    foto_de_perfil = db.Column(db.String(400))                                                      # Foto Perfil del Usuario

# SIGUE

class Sigue(db.Model):
    __tablename__="sigue"

    Usuario_Nicka = db.Column(db.String(20), db.ForeignKey('usuario.nick'),primary_key=True)        # Le sigue el usuario b
    Usuario_Nickb = db.Column(db.String(20), db.ForeignKey('usuario.nick'),primary_key=True)        # Sigue al usuario a

# CHAT

class Chat(db.Model):
    __tablename__="chat"

    id=db.Column(db.Integer, primary_key=True)                                                      
    nick=db.Column(db.String(20), db.ForeignKey('usuario.nick'))                                    # Usuario emisor del mensaje
    created_at=db.Column(db.DateTime, default=datetime.utcnow)                                      # Momento creación mensaje
    updated_at=db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)            # Momento de actualización mensaje
    message=db.Column(db.String(500))                                                               # Contenido del mensaje
    room=db.Column(db.String(10))                                                                   # Chat al que pertenece


class Publicacion(db.Model):
    __tablename__="publicacion"

    id  = db.Column(Integer,primary_key=True)                                                       
    descripcion  = db.Column(db.String(1000))                                                       # Descripcion de la Publicacion
    timestamp = db.Column(db.TIMESTAMP, nullable=False,                                             # Momento de publicación
                  server_default=db.func.now(),                                                     
                  onupdate=db.func.now())
    Usuario_Nicka = db.Column(db.String(20), db.ForeignKey('usuario.nick'))                         # Usuario Publicador

class Propia(db.Model):
    __tablename__="publicacion_popia"

    pdf = db.Column(db.String(400))                                                                 # Pdf a subir
    portada = db.Column(db.String(400))                                                             # Portada del PDF
    id = db.Column(db.String(20), db.ForeignKey('publicacion.id'),primary_key=True)                 # Id Publicacion
    Usuario_Nicka = db.Column(db.String(20), db.ForeignKey('usuario.nick'))                         # Usuario Publicador


class Recomendacion(db.Model):
    __tablename__="publicacion_recomendada"

    link  = db.Column(db.String(200),nullable=False)                                                # Link a la Recomendacion
    titulo = db.Column(db.String(200),nullable=False)                                               # Titulo Recomendacion
    autor  = db.Column(db.String(200),nullable=False)                                               # Autor de la obra Recomendada
    id = db.Column(db.String(20), db.ForeignKey('publicacion.id'),primary_key=True)                 # Id Recomendacion
    Usuario_Nicka = db.Column(db.String(20), db.ForeignKey('usuario.nick'))                         # Usuario que ha hecho la recomendacion

class Tematica(db.Model):
    __tablename__="tematica"

    tema  = db.Column(db.String(50), primary_key=True )                                             # Tema de la tematica


class Notificaciones(db.Model):
    __tablename__="notificaciones"

    id  = db.Column(Integer,primary_key=True)                                                # Id Notificacion
    tipo = db.Column(Integer,nullable=False)                                                                       
    idPubli = db.Column(Integer)
    nickEmisor = db.Column(db.String(20),db.ForeignKey('usuario.nick'),nullable=False)           # Nick Receptor
    timestamp = db.Column(db.TIMESTAMP, nullable=False,                                             # Momento de publicación
                  server_default=db.func.now(),                                                     
                  onupdate=db.func.now())                                                                   # Fecha Notificacion
    nickReceptor = db.Column(db.String(20), db.ForeignKey('usuario.nick'),nullable=False)        # Nick Emisor
    comentario =  db.Column(db.String(200))                                                        # Comentario


class Prefiere(db.Model):
    __tablename__="prefiere_tema"

    Usuario_Nicka = db.Column(db.String(20), db.ForeignKey('usuario.nick'),primary_key=True)        # Usuario que prefiere distintas tematicas
    tema = db.Column(db.String(50), db.ForeignKey('tematica.tema'),primary_key=True)


class Trata_pub_del_tema(db.Model):
    __tablename__="tematica_publicacion"

    id = db.Column(db.Integer, db.ForeignKey('publicacion.id'),primary_key=True)
    tema = db.Column(db.String(50), db.ForeignKey('tematica.tema'),primary_key=True)

class Gusta(db.Model):
    __tablename__="gusta"
    
    id = db.Column(db.Integer, db.ForeignKey('publicacion.id'),primary_key=True)
    Usuario_Nicka = db.Column(db.String(20), db.ForeignKey('usuario.nick'),primary_key=True)            # Quien le da Me gusta


class Comenta(db.Model):
    __tablename__="comentarios"

    id  = db.Column(Integer,primary_key=True)
    idPubli = db.Column(db.Integer, db.ForeignKey('publicacion.id'))

    Usuario_Nicka = db.Column(db.String(20), db.ForeignKey('usuario.nick'))                             # Quien comenta
    comentario  = db.Column(db.String(1000))                                                            # Contenido comentario


class Guarda(db.Model):
    __tablename__="pub_guardadas"

    id = db.Column(db.Integer, db.ForeignKey('publicacion.id'),primary_key=True)
    Usuario_Nicka = db.Column(db.String(20), db.ForeignKey('usuario.nick'),primary_key=True)            # Quien se lo guarda
    tipo =db.Column(db.Integer,nullable=False)                                                          # 1. Articulos | 2. Recomendacion

class Trata(db.Model):
    __tablename__="trata"
    
    id_publi = db.Column(db.Integer, db.ForeignKey('publicacion.id'),primary_key=True)
    id_notif = db.Column(db.String(20), db.ForeignKey('notificaciones.id'),primary_key=True)


class UserSid(db.Model):
    __tablename__="UserSid"

    Sid = db.Column(db.String(50))                                            # Socket Id del Usuario en ese momento
    User = db.Column(db.String(20), db.ForeignKey('usuario.nick'), primary_key=True)             # Usuario que contiene ese SocketId

class chatRoom(db.Model):
    __tablename__="chatRoom"

    roomid = db.Column(db.Integer)   
    user1 = db.Column(db.String(20), db.ForeignKey('usuario.nick'), primary_key=True)
    user2 = db.Column(db.String(20), db.ForeignKey('usuario.nick'), primary_key=True)