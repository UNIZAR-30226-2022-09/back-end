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
    user_id=db.Column(db.Integer, db.ForeignKey('usuario.nick'))                                    # Usuario emisor del mensaje
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
    Usuario_Nicka = db.Column(db.String(20), db.ForeignKey('usuario.nick'))                         # Usuario Recomendador

class Tematica(db.Model):
    __tablename__="tematica"

    tema  = db.Column(db.String(50), primary_key=True )                                             # Tema de la tematica


class Notificaciones(db.Model):
    __tablename__="notificaciones"

    id  = db.Column(db.Integer, primary_key=True )                                                  # Id Notificacion
    fecha  = db.Column(db.Date)                                                                     # Fecha Notificacion
    Usuario_Nicka = db.Column(db.String(20), db.ForeignKey('usuario.nick'),primary_key=True)        # ?????


class Prefiere(db.Model):
    __tablename__="prefiere_tema"

    Usuario_Nicka = db.Column(db.String(20), db.ForeignKey('usuario.nick'),primary_key=True)        # 
    tema = db.Column(db.String(50), db.ForeignKey('tematica.tema'),primary_key=True)


class Trata_pub_del_tema(db.Model):
    __tablename__="tematica_publicacion"

    id = db.Column(db.Integer, db.ForeignKey('publicacion.id'),primary_key=True)
    tema = db.Column(db.String(50), db.ForeignKey('tematica.tema'),primary_key=True)

class Gusta(db.Model):
    __tablename__="gusta"
    
    id = db.Column(db.Integer, db.ForeignKey('publicacion.id'),primary_key=True)
    Usuario_Nicka = db.Column(db.String(20), db.ForeignKey('usuario.nick'),primary_key=True)


class Comenta(db.Model):
    __tablename__="comentarios"

    id  = db.Column(Integer,primary_key=True)
    idPubli = db.Column(db.Integer, db.ForeignKey('publicacion.id'))

    Usuario_Nicka = db.Column(db.String(20), db.ForeignKey('usuario.nick'))
    comentario  = db.Column(db.String(1000))


class Guarda(db.Model):
    __tablename__="pub_guardadas"

    id = db.Column(db.Integer, db.ForeignKey('publicacion.id'),primary_key=True)
    Usuario_Nicka = db.Column(db.String(20), db.ForeignKey('usuario.nick'),primary_key=True) # de quien son los guardados
    tipo =db.Column(db.Integer,nullable=False)

class Trata(db.Model):
    __tablename__="trata"
    
    id_publi = db.Column(db.Integer, db.ForeignKey('publicacion.id'),primary_key=True)
    id_notif = db.Column(db.String(20), db.ForeignKey('notificaciones.id'),primary_key=True)


class Genera(db.Model):
    __tablename__="genera"

    id = db.Column(db.Integer, db.ForeignKey('publicacion.id'),primary_key=True)
    Usuario_Nicka = db.Column(db.String(20), db.ForeignKey('usuario.nick'),primary_key=True)
