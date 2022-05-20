from flask import Blueprint, request, jsonify
from app import app, db
from sqlalchemy import  select, and_
import json
from app.user.main import token_required
from app.models import Recomendacion, Propia, Guarda, Publicacion, Sigue
from app.action.main import guardarId, guardaRecomendacion, guardaPDF

paginationsBp = Blueprint('paginations',__name__)


@app.route('/mostrarRecomendacionesPaginadas', methods=['GET'])
@token_required
def mostrarRecomendacionesPaginadas(current_user):
    Publis = []
    
    offsetreal = 0
    limite=request.headers['limit']
    offsetreal = int(request.headers['offset'])*int(limite)
    #todosGuardados=Guarda.query.filter_by(Usuario_Nicka=current_user).all()
    recomendacion = select([Recomendacion.id ]).where(Recomendacion.Usuario_Nicka == request.headers['nick'] ).order_by(Recomendacion.id.desc()).limit(int(limite)).offset(int(offsetreal))
    recomendaciones = db.session.execute(recomendacion)

    for ids in recomendaciones:
        print("vamos: ", ids.id)
        guardarId(Publis,ids.id)

    if len(Publis) == 0:
        print("hola", " offset: ", offsetreal, "limite: ", limite)
        return jsonify({'fin': 'La lista se ha acabado no hay mas posts'})

    Publis.sort(key = customSort, reverse=True)
    finalDictionary = {}
    i=0
    x=0
    for x in  range(len(Publis)):
        guardaRecomendacion(Publis[x],finalDictionary,current_user)
        i = i + 1
    
    return json.dumps(finalDictionary, indent = i)
                

@app.route('/mostrarArticulosPaginados', methods=['GET'])
@token_required
def mostrarArticulosPaginados(current_user):
    Publis = []
    
    offsetreal = 0
    limite=request.headers['limit']
    offsetreal = int(request.headers['offset'])*int(limite)
    #todosGuardados=Guarda.query.filter_by(Usuario_Nicka=current_user).all()
    propias = select([Propia.id ]).where(Propia.Usuario_Nicka == request.headers['nick'] ).order_by(Propia.id.desc()).limit(int(limite)).offset(int(offsetreal))
    results = db.session.execute(propias)
    for ids in results:
        print("vamos: ", ids.id)
        guardarId(Publis,ids.id)

    if len(Publis) == 0:
        print("hola", " offset: ", offsetreal, "limite: ", limite)
        return jsonify({'fin': 'La lista se ha acabado no hay mas posts'})
    finalDictionary = {}
    i=0
    x=0
    for x in  range(len(Publis)):
        guardaPDF(Publis[x],finalDictionary,current_user)
        i = i + 1
    
    return json.dumps(finalDictionary, indent = i)
                

@app.route('/mostrarGuardadosPaginados', methods=['GET'])
@token_required
def mostrarGuardadosPaginados(current_user):
    Publis = []
    
    offsetreal = 0
    limite=request.headers['limit']
    offsetreal = int(request.headers['offset'])*int(limite)
    #todosGuardados=Guarda.query.filter_by(Usuario_Nicka=current_user).all()
    Publis = []
    
    todosGuardados=select([Guarda.id ]).where(Guarda.Usuario_Nicka == current_user ).order_by(Guarda.id.desc()).limit(int(limite)).offset(int(offsetreal))
    todosGuardados = db.session.execute(todosGuardados)
    for ids in todosGuardados:
        guardarId(Publis,ids.id)

    if len(Publis) == 0:
        print("hola", " offset: ", offsetreal, "limite: ", limite)
        return jsonify({'fin': 'La lista se ha acabado no hay mas posts'})
    finalDictionary = {}
    i=0
    x=0
    for x in  range(len(Publis)):
            existe = db.session.query(Propia).filter(Propia.id == Publis[x].ids ).count()
                #ver si ese ID existe en recomendacion sino es un post propio
            if bool(existe):
                guardaPDF(Publis[x],finalDictionary,current_user)
                i = i + 1
            else:
                guardaRecomendacion(Publis[x],finalDictionary,current_user)
                i = i + 1

    return json.dumps(finalDictionary, indent = i)
                
@app.route('/GuardadosArticulosPaginados', methods=['GET'])
@token_required
def GuardadosArticulosPaginados(current_user):

    Publis = []
    offsetreal = 0
    limite=request.headers['limit']
    offsetreal = int(request.headers['offset'])*int(limite)
    
    
    todosGuardados=select([Guarda.id, Guarda.Usuario_Nicka ]).where(and_(Guarda.tipo==1 , Guarda.Usuario_Nicka == current_user)) .order_by(Guarda.id.desc()).limit(int(limite)).offset(int(offsetreal)).distinct()
    todosGuardados = db.session.execute(todosGuardados)
    

    for ids in todosGuardados:
        print("CURRENT USER", current_user , "muestra la pub de: ",ids.Usuario_Nicka )
        print("vamos: ", ids.id )
        guardarId(Publis,ids.id)

    if len(Publis) == 0:
        print("hola", " offset: ", offsetreal, "limite: ", limite)
        return jsonify({'fin': 'La lista se ha acabado no hay mas posts'})
    finalDictionary = {}
    i=0
    x=0
    for x in  range(len(Publis)):
            existe = db.session.query(Propia).filter(Propia.id == Publis[x].ids ).count()
                #ver si ese ID existe en recomendacion sino es un post propio
            if bool(existe):
                guardaPDF(Publis[x],finalDictionary,current_user)
                i = i + 1

    return json.dumps(finalDictionary, indent = i)

@app.route('/GuardadosRecomendacionesPaginados', methods=['GET'])
@token_required
def GuardadosRecomendacionesPaginados(current_user):

    Publis = []
    offsetreal = 0
    limite=request.headers['limit']
    offsetreal = int(request.headers['offset'])*int(limite)

    
    todosGuardados=select([Guarda.id ]).where(and_(Guarda.tipo==2 , Guarda.Usuario_Nicka == current_user)) .order_by(Guarda.id.desc()).limit(int(limite)).offset(int(offsetreal)).distinct()
    todosGuardados = db.session.execute(todosGuardados)
    for ids in todosGuardados:
        print("vamos: ", ids.id)
        guardarId(Publis,ids.id)

    if len(Publis) == 0:
        print("hola", " offset: ", offsetreal, "limite: ", limite)
        return jsonify({'fin': 'La lista se ha acabado no hay mas posts'})
    finalDictionary = {}
    i=0
    x=0
    for x in  range(len(Publis)):
            existe = db.session.query(Recomendacion).filter(Recomendacion.id == Publis[x].ids ).count()
                #ver si ese ID existe en recomendacion sino es un post propio
            if bool(existe):
                guardaRecomendacion(Publis[x],finalDictionary,current_user)
                i = i + 1

    return json.dumps(finalDictionary, indent = i)


@app.route('/HomePaginado', methods=['GET'])
@token_required
def HomePaginado(current_user):
    
    offsetreal = 0
    limite=request.headers['limit']
    offsetreal = int(request.headers['offset'])*int(limite)
    limitereal=  (int(request.headers['offset'])*int(limite)) + int(limite)
    Publis = []


    todosSiguiendo=Sigue.query.filter_by(Usuario_Nickb=current_user).all()#   order_by(Propia.id.desc()).limit(int(limite)).offset(int(offsetreal))
    for nick in todosSiguiendo:
        posts=select([Publicacion.id ]).where(Publicacion.Usuario_Nicka == nick.Usuario_Nicka ).order_by(Publicacion.id.desc()).limit(int(limitereal))#.offset(int(offsetreal))
        posts = db.session.execute(posts)    
        for posteos in posts:
            guardarId(Publis,posteos.id)


    
    #ordenar por id
    Publis.sort(key = customSort, reverse=True)

    Publis2=[]
    for i in range (int(offsetreal), int(offsetreal) + int(limite)):
        #print("x es = ", x , "i es: ", i ," offset: ", offsetreal, "limite: ", limite, "publis[i]: ", Publis[i])
        if i< len(Publis): 
            print("i es: ", i ,"len publis: ", len(Publis))
            Publis2.append(Publis[i])

    if len(Publis2) == 0:
        print("hola", " offset: ", offsetreal, "limite: ", limite)
        return jsonify({'fin': 'La lista se ha acabado no hay mas posts'})

    finalDictionary = {}
    i=0
    x=0
    for x in  range(len(Publis2)):
            existe = db.session.query(Propia).filter(Propia.id == Publis2[x].ids ).count()
                #ver si ese ID existe en recomendacion sino es un post propio
            #print(" postesos despues: ", Publis2[x].ids)
            if bool(existe):
                guardaPDF(Publis2[x],finalDictionary,current_user)
                i = i + 1
            else:
                guardaRecomendacion(Publis2[x],finalDictionary,current_user)
                i = i + 1

    return json.dumps(finalDictionary, indent = i)
            

def customSort(k):
    return k.ids



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
