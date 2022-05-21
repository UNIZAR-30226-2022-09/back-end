from flask import Blueprint, request, jsonify
from app import app, db
import json
from app.models import Propia
from app.user.main import token_required
from app.popular.main import paginaExplorados
from app.post.main import guardaPDF, guardaRecomendacion

recentsBp = Blueprint('recents',__name__)

@app.route('/Recientes', methods=['GET'])
@token_required
def Recientes(current_user):

    Publis = []
    limite=request.headers['limit']
    paginaExplorados(Publis,current_user,request.headers['tematicas'],request.headers['filtrado'],3)

    Publis.sort(key = orderRecientes, reverse=True)


    Publis2=[]
    for i in range (0, int(limite)):
        if i< len(Publis): 
            Publis2.append(Publis[i])

    if len(Publis2) == 0:
        return jsonify({'fin': 'La lista se ha acabado no hay mas posts'})

    finalDictionary = {}
    i=0
    x=0
    for x in  range(len(Publis2)):
            existe = db.session.query(Propia).filter(Propia.id == Publis2[x].ids ).count()

            if bool(existe):
                guardaPDF(Publis2[x],finalDictionary,current_user)
                i = i + 1
            else:
                guardaRecomendacion(Publis2[x],finalDictionary,current_user)
                i = i + 1

    return json.dumps(finalDictionary, indent = i)



@app.route('/RecientesRecomendaciones', methods=['GET'])
@token_required
def RecientesRecomendaciones(current_user):

    Publis = []
    limite=request.headers['limit']
    paginaExplorados(Publis,current_user,request.headers['tematicas'],request.headers['filtrado'],2)

    Publis.sort(key = orderRecientes, reverse=True)

    Publis2=[]
    for i in range (0, int(limite)):
        if i< len(Publis): 
            Publis2.append(Publis[i])

    if len(Publis2) == 0:
        return jsonify({'fin': 'La lista se ha acabado no hay mas posts'})

    finalDictionary = {}
    i=0
    x=0
    for x in  range(len(Publis2)):
        guardaRecomendacion(Publis2[x],finalDictionary,current_user)
        i = i + 1

    return json.dumps(finalDictionary, indent = i)

@app.route('/RecientesArticulos', methods=['GET'])
@token_required
def RecientesArticulos(current_user):

    Publis = []
    limite= int(request.headers['limit'])
    paginaExplorados(Publis,current_user,request.headers['tematicas'],request.headers['filtrado'],1)

    Publis.sort(key = orderRecientes, reverse=True)

    Publis2=[]
    for i in range (0, int(limite)):
        if i< len(Publis): 
            Publis2.append(Publis[i])

    if len(Publis2) == 0:
        return jsonify({'fin': 'La lista se ha acabado no hay mas posts'})

    finalDictionary = {}
    i=0
    x=0
    for x in  range(len(Publis2)):
        guardaPDF(Publis2[x],finalDictionary,current_user)
        i = i + 1

    return json.dumps(finalDictionary, indent = i)

def orderRecientes(k):
    
    return k.timestamps
