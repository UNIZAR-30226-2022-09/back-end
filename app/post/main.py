from flask import Blueprint, request, jsonify, redirect, url_for
from datetime import datetime
import jwt
import os
import json
from pdf2image import convert_from_path
from app import app, db
from app.user.main import token_required
from app.models import Publicacion, Trata_pub_del_tema, Recomendacion, Propia
from app.action.main import guardarId, guardaPDF, guardaRecomendacion

ABSOLUTE_PATH_TO_YOUR_PDF_FOLDER ='../static/pdf'

postsBp = Blueprint('posts',__name__)

class Comentario:
  def __init__(self, id,idComen,nick, foto_de_perfil,comentario):
    self.id = id
    self.nick = nick
    self.foto_de_perfil = foto_de_perfil
    self.comentario = comentario
    self.idComen = idComen


class PublicacionHome:
  def __init__(self, nick,Nombre_de_usuario, foto_de_perfil,ids,descripciones,timestamps,Gustas,Guardados,Comentarios):
    self.nick = nick
    self.Nombre_de_usuario = Nombre_de_usuario
    self.foto_de_perfil = foto_de_perfil
    self.ids = ids
    self.descripciones = descripciones
    self.timestamps = timestamps
    self.Gustas = Gustas
    self.Guardados = Guardados
    self.Comentarios = Comentarios

class Pdfs(PublicacionHome):
    """Clase que representa a un pdf"""

    def __init__(self, nick,Nombre_de_usuario, foto_de_perfil,ids,descripciones,timestamps,Gustas,Guardados,Comentarios,pdf,portada):
        """Constructor de clase pdf"""

        # Invoca al constructor de clase Persona
        PublicacionHome.__init__(self, nick,Nombre_de_usuario, foto_de_perfil,ids,descripciones,timestamps,Gustas,Guardados,Comentarios)

        # Nuevos atributos
        self.pdf = pdf
        self.portada = portada

class Recomendados(PublicacionHome):
    """Clase que representa a un pdf"""

    def __init__(self, nick,Nombre_de_usuario, foto_de_perfil,ids,descripciones,timestamps,Gustas,Guardados,Comentarios,links,titulos,autores):
        """Constructor de clase pdf"""

        # Invoca al constructor de clase Persona
        PublicacionHome.__init__(self,nick, Nombre_de_usuario, foto_de_perfil,ids,descripciones,timestamps,Gustas,Guardados,Comentarios)

        # Nuevos atributos
        self.links = links
        self.titulos = titulos
        self.autores = autores

    
@app.route('/subirPost', methods=['POST'])
@token_required
def subirPost(current_user):

    data= request.get_json()
    
    publicacion = Publicacion(descripcion=data['descripcion'],Usuario_Nicka=current_user) #coger id
    db.session.add(publicacion)
    db.session.commit()
    print (data['tematicas'], "+",data['descripcion'],"+",data['tipo'])
    tematicas = data['tematicas']
    for temas in tematicas:
        #temita = Tematica.query.filter_by(tema=temas).first()
        #if temita:
            nuevo = Trata_pub_del_tema(id=publicacion.id, tema = temas)
            db.session.add(nuevo)
    db.session.commit()
    if (data['tipo']=="1"): # articulo
        return jsonify({'id' : publicacion.id})
        #guardarPDF(request.files['pdf'], publicacion.id)
    elif(data['tipo']=="2"): # recomendacion
        recomendacion = Recomendacion(link=data['link'],titulo=data['titulo'], autor = data['autor'], id = publicacion.id, Usuario_Nicka=current_user)
        db.session.add(recomendacion)
        
    db.session.commit()
    token = jwt.encode({'nick' : current_user, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
    return jsonify({'token' : token.decode('UTF-8')})

@app.route('/subirPdf', methods=['POST'])
@token_required
def guardarPDF(current_user):
    print("bn : " + request.headers['id'])
    _id=request.headers['id']

    propia = Propia( id = _id, Usuario_Nicka=current_user)
    db.session.add(propia)
    db.session.commit()
    propia = Propia.query.filter_by(id=_id).first()
    if propia:
        if request.files['pdf'] is not None:
            file = request.files['pdf']
            filename = str(_id) + '.pdf'
            file.save(os.path.join(ABSOLUTE_PATH_TO_YOUR_PDF_FOLDER, filename))
            propia.pdf = filename
            
            path= ABSOLUTE_PATH_TO_YOUR_PDF_FOLDER + '/' +  filename
            pages = convert_from_path(path, 0)
            for page in pages:
                output = str(_id) + '.png'
                pathimage = 'static/portadasPdf/' + output
                page.save(pathimage, 'PNG')
                propia.portada = output
                db.session.add(propia)
                db.session.commit()
                token = jwt.encode({'nick' : current_user, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
                return jsonify({'token' : token.decode('UTF-8')})
        else:
            print("pdf nulo")
            return jsonify({'error': 'No existe parámetro PDF'}), 403
    else:
        return jsonify({'error': 'Mal envio'}), 403

@app.route('/infoPost', methods=['GET'])
@token_required
def infoPost(current_user):
    Publis = []
    guardarId(Publis,request.headers['id'])
    finalDictionary = {}
    i=0
    x=0
    for x in  range(len(Publis)):
            existe = db.session.query(Propia).filter(Propia.id == Publis[x].ids ).count()
                #ver si ese ID existe en recomendacion sino es un post propio
            #print(" postesos despues: ", Publis2[x].ids)
            if bool(existe):
                guardaPDF(Publis[x],finalDictionary,current_user)
                i = i + 1
            else:
                guardaRecomendacion(Publis[x],finalDictionary,current_user)
                i = i + 1

    return json.dumps(finalDictionary, indent = i)

@app.route('/display3/<filename>')
def portadaGet(filename):
    return redirect(url_for('static', filename='portadasPdf/' + filename),code = 301)


@app.route('/display2/<filename>')
def pdf(filename):
    return redirect(url_for('static', filename='pdf/' + filename),code = 301)
