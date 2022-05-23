from flask import Blueprint , request , jsonify, redirect, url_for
import jwt
from sqlalchemy import  select, and_
import datetime
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from app import db, app
from app.models import Usuario , Sigue , Publicacion, Prefiere
from flask_cors import CORS

CORS(app)
ABSOLUTE_PATH_TO_YOUR_FOLDER ='../static/fotosPerfil'

usersBp = Blueprint('users',__name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = request.headers['token']
        
        if not token:
            return jsonify({'error': 'Token no existe'}), 403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = Usuario.query.filter_by(nick=data['nick']).first()
            current_user = data['nick']
        except:
            return jsonify({'error': 'Token no valido'}), 403

        return f(current_user,*args, **kwargs)
    return decorated



@app.route('/register', methods=['POST'])
def add_data():
    data= request.get_json()

    user = Usuario.query.filter_by(e_mail=data['e_mail']).first()
    nick = Usuario.query.filter_by(nick=data['nick']).first()
    if user: # si esto devuelve algo entonces el email existe
        return jsonify({'error': 'Existe correo'}) #json diciendo error existe email
    if nick:
        return jsonify({'error': 'Existe nick'})
    
    register = Usuario(nick=data['nick'],password=generate_password_hash(data['password']), e_mail=data['e_mail'],foto_de_perfil="platon.jpg")
    db.session.add(register)
    db.session.commit()

    token = jwt.encode({'nick' : data['nick'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
    return jsonify({'token' : token.decode('UTF-8')})



@app.route('/login', methods=['POST'])
def login():

    data= request.get_json()

    if '@' in data['nickOcorreo']:
        user = Usuario.query.filter_by(e_mail=data['nickOcorreo']).first()
        
    else:
        user = Usuario.query.filter_by(nick=data['nickOcorreo']).first()

    if not user:
        return jsonify({'error': 'No existe ese usuario'})#error mal user
    if not check_password_hash(user.password, data['password']):
        return jsonify({'error': 'Mala contraseña'}) #error mala contraseña


    token = jwt.encode({'nick' : user.nick, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=9999999)}, app.config['SECRET_KEY'])
    return jsonify({'token' : token.decode('UTF-8'), 'nick' : user.nick})

@app.route('/mostrarPerfil', methods=['GET'])
@token_required
def mostrarPerfil(current_user):
    nick = request.headers['nick']
    print ("este es el nick enseñame: ",nick, "current: ",current_user)
    s = select([Usuario.Nombre_de_usuario,  Usuario.descripcion,Usuario.link, Usuario.foto_de_perfil]).where((Usuario.nick == nick))
    result = db.session.execute(s)

    siguiendo = db.session.query(Sigue).filter(and_(Sigue.Usuario_Nicka == nick , Sigue.Usuario_Nickb == current_user)).count()
    print (siguiendo)
    seguidos= db.session.query(Sigue).filter(Sigue.Usuario_Nickb == nick ).count()
    seguidores= db.session.query(Sigue).filter(Sigue.Usuario_Nicka == nick ).count()
    nposts= db.session.query(Publicacion).filter(Publicacion.Usuario_Nicka == nick ).count()

    tema = select([Prefiere.tema]).where((Prefiere.Usuario_Nicka == nick))
    temas = db.session.execute(tema)
    vector = []
    for row in temas:
        vector += row
    for row in result:
        fila = {
            "nick": nick,
            "nombre_de_usuario":row[0],
            "descripcion":row[1],
            "link":row[2],
            "foto_de_perfil": 'http://51.255.50.207:5000/display/' + row[3],
            "nsiguiendo": seguidos,
            "nseguidores": seguidores,
            "nposts": nposts,
            "siguiendo" : bool(siguiendo),
            "tematicas": vector
        }
    return fila

@app.route('/display/<filename>')
def fotoget(filename):
    return redirect(url_for('static', filename='fotosPerfil/' + filename),code = 301)


@app.route('/editarPerfil', methods=['POST'])
@token_required
def editarPerfilpost(current_user):

    data= request.get_json()
    user = Usuario.query.filter_by(nick=current_user).first()
    user.Nombre_de_usuario = data['nombre_de_usuario']
    print(data['nombre_de_usuario'])
    print(data['descripcion'])
    print(data['link'])
    print(data['tematicas'])
    user.descripcion = data['descripcion']
    user.link = data['link']
    tematicas = data['tematicas']
    todo = Prefiere.query.filter_by( Usuario_Nicka=current_user).first()
    while todo is not None:
        db.session.delete(todo)
        todo = Prefiere.query.filter_by( Usuario_Nicka=current_user).first()
    db.session.commit()
    for temas in tematicas:
        #tema = Prefiere.query.filter_by(tema=temas).first()
        #if not tema:
        tema = Prefiere(Usuario_Nicka=current_user, tema = temas)
        db.session.add(tema)
    
    db.session.commit()

    token = jwt.encode({'nick' : current_user, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
    return jsonify({'token' : token.decode('UTF-8')})


@app.route('/actualizarImagen', methods=['POST'])
@token_required
def actualizarImagen(current_user):
    user = Usuario.query.filter_by(nick=current_user).first()

    if request.files['nueva_foto'] is not None: 
            file = request.files['nueva_foto']

            filename = secure_filename(str(current_user)) + ".jpg"

            file.save(os.path.join(ABSOLUTE_PATH_TO_YOUR_FOLDER, filename))
            user.foto_de_perfil = filename 
            db.session.commit()

    token = jwt.encode({'nick' : current_user, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
    return jsonify({'token' : token.decode('UTF-8')})
