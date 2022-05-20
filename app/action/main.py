from flask import Blueprint, request, jsonify
from app import app, db
import jwt
import json
from sqlalchemy import  select , func
from datetime import datetime
from app.models import Usuario, Gusta, Comenta, Guarda, Propia, Sigue, Publicacion, Recomendacion
from app.user.main import token_required

actionsBp = Blueprint('actions',__name__)

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
        db.session.add(like)

    db.session.commit()

    token = jwt.encode({'nick' : current_user, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
    return jsonify({'token' : token.decode('UTF-8')})


@app.route('/comentar', methods=['POST'])
@token_required
def comentar(current_user):
    data= request.get_json()

    guardar = Comenta(idPubli=data['id'], Usuario_Nicka=current_user,comentario=data['comentario'])
    db.session.add(guardar)
    db.session.commit()


    token = jwt.encode({'nick' : current_user, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
    return jsonify({'token' : token.decode('UTF-8')})

@app.route('/verComentarios', methods=['GET'])
@token_required
def verComentarios(current_user):

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
    siguiendo = Sigue.query.filter_by(Usuario_Nicka=data['nick'], Usuario_Nickb=current_user).first()
    if siguiendo: 
        print("true")
        db.session.delete(siguiendo)
        
    else:
        print("false")
        seguir = Sigue(Usuario_Nicka=data['nick'], Usuario_Nickb=current_user)
        db.session.add(seguir)

    db.session.commit()

    token = jwt.encode({'nick' : current_user, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
    return jsonify({'token' : token.decode('UTF-8')})


def guardaPDF(Publis,finalDictionary,current_user):
    GustaMio = db.session.query(Gusta).filter(Gusta.Usuario_Nicka == current_user, Gusta.id == Publis.ids  ).count()
    GuardadoMio = db.session.query(Guarda).filter(Guarda.Usuario_Nicka == current_user, Guarda.id == Publis.ids ).count()
    nombreCompletopdf = "http://51.255.50.207:5000/display2/" + str(Publis.pdf)
    nombreCompletoPortada = "http://51.255.50.207:5000/display3/" + str(Publis.portada)
    foto_de_perfil_Completo= 'http://51.255.50.207:5000/display/' + str(Publis.foto_de_perfil)
    finalDictionary[Publis.ids] = { 'tipo' : 1 ,'pdf' :nombreCompletopdf, 'portada':  nombreCompletoPortada, 'descripcion' : str(Publis.descripciones),'usuario' : Publis.nick,'foto_de_perfil' : foto_de_perfil_Completo,'nlikes' : int(Publis.Gustas),'likemio' : bool(GustaMio),'ncomentarios' : int(Publis.Comentarios),'nguardados' : int(Publis.Guardados),'guardadomio' : bool(GuardadoMio) }

def guardaRecomendacion(Publis,finalDictionary,current_user):
    GustaMio = db.session.query(Gusta).filter(Gusta.Usuario_Nicka == current_user, Gusta.id == Publis.ids  ).count()
    #print("GustaMio: ", Publis.nick , "  ", Publis.ids , " ",GustaMio)
    GuardadoMio = db.session.query(Guarda).filter(Guarda.Usuario_Nicka == current_user, Guarda.id == Publis.ids ).count()
    foto_de_perfil_Completo= 'http://51.255.50.207:5000/display/' + str(Publis.foto_de_perfil)
    finalDictionary[Publis.ids] = { 'tipo' : 2 ,'titulo' : str(Publis.titulos), 'autor' : str(Publis.autores),'descripcion' : str(Publis.descripciones),'link' : str(Publis.links),'usuario' : Publis.nick,'foto_de_perfil' : foto_de_perfil_Completo,'nlikes' : int(Publis.Gustas),'likemio' : bool(GustaMio),'ncomentarios' : int(Publis.Comentarios),'nguardados' : int(Publis.Guardados),'guardadomio' : bool(GuardadoMio) }
                


def guardarId(Publis,id):
    Nombre_de_usuario=""
    foto_de_perfil=""
    ids=""
    Gustas=""
    Comentarios=""
    descripciones=""
    timestamps=""   
    Guardados=""
    pdfname=""
    portadaname=""
    links=""
    titulos=""
    autores=""

    publicaciones = select([Publicacion.id,Publicacion.timestamp,Publicacion.descripcion ,Publicacion.Usuario_Nicka]).where(Publicacion.id == id )
    results = db.session.execute(publicaciones)
    for a in results: 
        print(a)
        x = select([Usuario.Nombre_de_usuario, Usuario.foto_de_perfil, Usuario.nick]).where((Usuario.nick == a.Usuario_Nicka))
        resultb = db.session.execute(x)
        for b in resultb: 
            Nombre_de_usuario= str(b.Nombre_de_usuario)
            foto_de_perfil=str(b.foto_de_perfil)


            ids=str(a.id)
            Gustas=str(db.session.query(func.count(Gusta.id).filter(Gusta.id == a.id)).scalar())
            print (Gustas)
            Comentarios=str(db.session.query(Comenta).filter(Comenta.idPubli == a.id ).count())
            Guardados=(db.session.query(Guarda).filter(Guarda.id == a.id).count())
            descripciones=str(a.descripcion)
            timestamps=str(a.timestamp)
        
            pdf = Propia.query.filter_by(id=a.id).first()
            if pdf :
                #print("es un pdf este numero: " , a.id)
                pdfname , portadaname = cargarDatosPDFstr(pdfname,portadaname,a.id)
                Publis.append(Pdfs(b.nick,Nombre_de_usuario,foto_de_perfil,ids,descripciones,timestamps,Gustas,Guardados,Comentarios,pdfname,portadaname))
            else:
                links,titulos,autores = cargarDatosRecomendacionesstr(links,titulos,autores,a.id)
                Publis.append(Recomendados(b.nick,Nombre_de_usuario,foto_de_perfil,ids,descripciones,timestamps,Gustas,Guardados,Comentarios,links,titulos,autores))

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
