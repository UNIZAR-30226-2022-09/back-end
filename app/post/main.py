from flask import Blueprint, request, jsonify, redirect, url_for
import datetime
import jwt
import os
from sqlalchemy import  select, func
import json
from pdf2image import convert_from_path
from app import app, db
from app.user.main import token_required
from app.models import Publicacion, Trata_pub_del_tema, Recomendacion, Propia, Guarda, Gusta, Usuario, Comenta

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
