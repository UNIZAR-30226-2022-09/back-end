from lib2to3.pgen2 import token
from flask import Blueprint, request, jsonify
from flask_login import current_user
from app import app, db
import jwt
import json
from sqlalchemy import  select , func
import datetime
from app.models import Notificaciones, Usuario, Gusta, Comenta, Guarda, Propia, Sigue, Publicacion, Recomendacion
from app.post.main import Comentario
from app.user.main import token_required

actionsBp = Blueprint('actions',__name__)


class Notificacion:
  def __init__(self, id, nick,tipo, foto_de_perfil,timestamps):
    self.id  = id
    self.nick = nick
    self.foto_de_perfil = foto_de_perfil
    self.tipo = tipo
    self.timestamps = timestamps

class meGusta(Notificacion):

    def __init__(self, id_pub, nick,tipo, foto_de_perfil,timestamps, id):
        """Constructor de clase pdf"""

        # Invoca al constructor de clase Persona
        Notificacion.__init__(self,nick,tipo, foto_de_perfil,timestamps)

        # Nuevos atributos
        self.id_pub = id_pub

class comenta(Notificacion):

    def __init__(self, id, nick,tipo, foto_de_perfil,timestamps, comentario):
        """Constructor de clase pdf"""

        # Invoca al constructor de clase Persona
        Notificacion.__init__(self,id,nick,tipo, foto_de_perfil,timestamps)

        # Nuevos atributos
        # PONER UN ID PUB
        self.comentario = comentario

@app.route('/buscarUsuarios', methods=['GET'])
@token_required
def getUsuarios(current_user):
    nick = request.headers['nick']

    search = "%{}%".format(nick)
    resulta = Usuario.query.filter(Usuario.nick.like(search)).all()
    #resultb = Usuario.query.filter(Usuario.nick.like(search)).all()

    print(resulta)
    nicks = []
    finalDictionary = {}
    foto_de_perfil= []
    for a in resulta: 
         nicks.append(str(a.nick))
         foto_de_perfil.append(str(a.foto_de_perfil))
    i=0
    for x in  nicks:
        print(x)
        nombreCompletofoto = "http://51.255.50.207:5000/display/" + str(foto_de_perfil[i])
        finalDictionary[x] = { 'foto_de_perfil' : nombreCompletofoto } #funciona

        i = i+1
    print (i)
    print (finalDictionary)
    return  json.dumps(finalDictionary, indent = i)



@app.route('/darLike', methods=['POST'])
@token_required
def darLike(current_user):
    data= request.get_json()
    
    gusta = Gusta.query.filter_by(id=data['id'] ,Usuario_Nicka=current_user).first()

    if gusta: 
        db.session.delete(gusta)
    else:        
        like = Gusta(id=data['id'], Usuario_Nicka=current_user) 
        nickRecep = Publicacion.query.filter_by(id=data['id']).first()
        notificacion = Notificaciones(tipo=1,id=data['id'], nickEmisor=current_user, nickReceptor= nickRecep.Usuario_Nicka)
        db.session.add(like)
        db.session.add(notificacion)

    db.session.commit()

    token = jwt.encode({'nick' : current_user, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
    return jsonify({'token' : token.decode('UTF-8')})


@app.route('/comentar', methods=['POST'])
@token_required
def comentar(current_user):
    data= request.get_json()

    guardar = Comenta(idPubli=data['id'], Usuario_Nicka=current_user,comentario=data['comentario'])
    db.session.add(guardar)

    nickRecep = Publicacion.query.filter_by(id=data['id']).first()
    notificacion = Notificaciones(tipo=2,id=data['id'], nickEmisor=current_user, nickReceptor= nickRecep.Usuario_Nicka, comentario=data['comentario'])
    db.session.add(notificacion)
    
    db.session.commit()


    token = jwt.encode({'nick' : current_user, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
    return jsonify({'token' : token.decode('UTF-8')})

@app.route('/verComentarios', methods=['GET'])
@token_required
def verComentarios():
    coments = []
    comentarios=Comenta.query.filter_by(idPubli=request.headers['id']).order_by(Comenta.id.desc())
    for r in comentarios:
        x = select([ Usuario.foto_de_perfil]).where((Usuario.nick == r.Usuario_Nicka))
        resultb = db.session.execute(x)
        for a in resultb:
            coments.append(Comenta(r.idPubli,r.id,r.Usuario_Nicka,a.foto_de_perfil,r.comentario))
    finalDictionary = {}
    i=0
    for comen in coments:
        foto_de_perfil_Completo= 'http://51.255.50.207:5000/display/' + str(comen.foto_de_perfil)
        finalDictionary[comen.idComen] = { 'nick' : str(comen.nick) ,'foto_de_perfil' : str(foto_de_perfil_Completo), 'comentario':  str(comen.comentario)}
        i = i + 1

    return json.dumps(finalDictionary, indent = i)

@app.route('/guardar', methods=['POST'])
@token_required
def guardarPost(current_user):
    data= request.get_json()
    guardado = Guarda.query.filter_by(id=data['id'], Usuario_Nicka=current_user).first()
    if guardado: 
        print("true")
        db.session.delete(guardado)
        
    else:

        art = Propia.query.filter_by(id=data['id']).first()
        if art:
            guardar = Guarda(id=data['id'],  Usuario_Nicka=current_user, tipo=1) #Usuario_Nicka=r.Usuario_Nicka,
            db.session.add(guardar)
        else:
            guardar = Guarda(id=data['id'],  Usuario_Nicka=current_user, tipo=2) #Usuario_Nicka=r.Usuario_Nicka,
            db.session.add(guardar)
    db.session.commit()

    token = jwt.encode({'nick' : current_user, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
    return jsonify({'token' : token.decode('UTF-8')})


@app.route('/seguirUser', methods=['POST'])
@token_required
def seguirUser(current_user):
    data = request.get_json()
    print(data['nick'])
    siguiendo = Sigue.query.filter_by(Usuario_Nicka=data['nick'], Usuario_Nickb=current_user).first()   # Comprobamos si ya lo seguimos
    if siguiendo: 
        print("true")
        db.session.delete(siguiendo)    # Si ya lo sigue, significa que lo queria dejar de seguir.
        
    else:
        print("false")
        seguir = Sigue(Usuario_Nicka=data['nick'], Usuario_Nickb=current_user) # Si no lo sigue significa que lo quiere seguir
        db.session.add(seguir)
        notificacion = Notificaciones(tipo=3, nickEmisor=current_user, nickReceptor= data['nick'])
        db.session.add(notificacion)

    db.session.commit()

    token = jwt.encode({'nick' : current_user, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
    return jsonify({'token' : token.decode('UTF-8')})


def cargarDatosPDFstr(pdfname,portadaname,id):
    pdf = select([Propia.pdf,Propia.portada]).where((Propia.id == id))
    resulta = db.session.execute(pdf)

    for a in resulta:
        pdfname=str(a.pdf)
        portadaname=str(a.portada)
    return pdfname,portadaname

def cargarDatosRecomendacionesstr(links,titulos,autores,id):
    recom = select([Recomendacion.link,Recomendacion.titulo,Recomendacion.autor]).where((Recomendacion.id == id))
    resulta = db.session.execute(recom)

    for a in resulta:
        links=str(a.link)
        titulos=str(a.titulo)
        autores=str(a.autor)
    return links,titulos,autores



@app.route('/notificaciones', methods=['GET'])  # Tiene que haber token
def verNotificaciones():
    current_user = "Alvaro"
    offsetreal = 0
    limite=request.headers['limit']
    offsetreal = int(request.headers['offset'])*int(limite)
    notiVec = []
    notis=Notificaciones.query.filter_by(nickReceptor=current_user).order_by(Notificaciones.id.desc())
    for r in notis:
        x = select([ Usuario.foto_de_perfil]).where((Usuario.nick == r.nickEmisor))
        resultb = db.session.execute(x)
        for a in resultb:
            if r.tipo ==1:
                notiVec.append(meGusta(r.nickEmisor,r.tipo,a.foto_de_perfil,r.timestamp))
            elif r.tipo ==2:
                notiVec.append(comenta(r.nickEmisor,r.tipo,a.foto_de_perfil,r.timestamp,r.comentario))
            else:
                notiVec.append(Notificacion(r.nickEmisor,r.tipo,a.foto_de_perfil,r.timestamp))



    notiVec2=[]
    for i in range (int(offsetreal), int(offsetreal) + int(limite)):
        #print("x es = ", x , "i es: ", i ," offset: ", offsetreal, "limite: ", limite, "publis[i]: ", Publis[i])
        if i< len(notiVec): 
            print("i es: ", i ,"len publis: ", len(notiVec))
            notiVec2.append(notiVec[i])

    if len(notiVec2) == 0:
        return jsonify({'fin': 'La lista se ha acabado no hay mas notis'})

    finalDictionary = {}
    i=0
    for noti in notiVec2:
        foto_de_perfil_Completo= 'http://51.255.50.207:5000/display/' + str(noti.foto_de_perfil)
        if noti.tipo==1:
            finalDictionary[noti.id] = { 'nick' : str(noti.nick) ,'foto_de_perfil' : str(foto_de_perfil_Completo), 'id' : noti.id}
        elif noti.tipo==2:
            finalDictionary[noti.id] = { 'nick' : str(noti.nick) ,'foto_de_perfil' : str(foto_de_perfil_Completo), 'comentario': str(noti.comentario)}
        else:
            finalDictionary[noti.id] = { 'nick' : str(noti.nick) ,'foto_de_perfil' : str(foto_de_perfil_Completo)}
        i=i+1

    return json.dumps(finalDictionary, indent = i)