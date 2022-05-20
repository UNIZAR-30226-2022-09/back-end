from flask import Blueprint, request, jsonify
from app import app, db
from sqlalchemy import  select , and_
import json
from app.models import Usuario, Prefiere, Sigue, Publicacion, Trata_pub_del_tema, Propia, Recomendacion
from app.action.main import guardarId, guardaPDF, guardaRecomendacion
from app.user.main import token_required

popularsBp = Blueprint('populars',__name__)

@app.route('/Populares', methods=['GET'])
@token_required
def Populares(current_user):


# class Trata_pub_del_tema(db.Model):

#     id = db.Column(db.Integer, db.ForeignKey('publicacion.id'),primary_key=True)
#     tema = db.Column(db.String(50), db.ForeignKey('tematica.tema'),primary_key=True)

# class Prefiere(db.Model):

#     Usuario_Nicka = db.Column(db.String(20), db.ForeignKey('usuario.nick'),primary_key=True)
#     tema = db.Column(db.String(50), db.ForeignKey('tematica.tema'),primary_key=True)

    Publis = []
    limite=request.headers['limit']
    todosUsuarios = Usuario.query.all()
    for nicks in todosUsuarios:
        if nicks.nick != current_user:
            leSigue= db.session.query(Sigue).filter(and_(Sigue.Usuario_Nicka== 'nicks.nick' and Sigue.Usuario_Nickb== 'current_user')).first()
            if leSigue is None:
                preferidas = []
                if request.headers['tematicas']=="pref":
                    tema = select([Prefiere.tema]).where((Prefiere.Usuario_Nicka == current_user))
                    temas = db.session.execute(tema)
                    for row in temas:
                        preferidas.append(row.tema)
                else:
                    preferidas.append(request.headers['tematicas'])

                posts=""
                if request.headers['filtrado']!="":
                    search = "%{}%".format(request.headers['filtrado'])
                    posts =  db.session.query(Publicacion).filter(and_(Publicacion.descripcion.like(search), Publicacion.Usuario_Nicka == nicks.nick)).all()
                else:
                    posts=select([Publicacion.id ]).where(Publicacion.Usuario_Nicka == nicks.nick )
                    posts = db.session.execute(posts)  

                for posteos in posts:
                    pref = False
                    print("PREFERIDAS: ",preferidas )
                    for temas in preferidas:
                        
                        prefiere = Trata_pub_del_tema.query.filter_by(id=posteos.id ,tema= temas).first()
                        if prefiere:
                            print("si: ", posteos.id)
                            pref = True
                        else:
                            print("no: ", posteos.id, "tema: ", temas )

                    if pref ==True:
                        guardarId(Publis,posteos.id)
            # else:
            #     print(leSigue)
            #     print("este user: ", current_user , " sigue a este: ",nicks.nick  )



    Publis.sort(key = orderLikes, reverse=True)

    # for x in  range(len(Publis)):
    #     print("MEGUSTAS DE ID: ", Publis[x].ids ," gustas: ", Publis[x].Gustas )

    Publis2=[]
    for i in range (0, int(limite)):
        #print("x es = ", x , "i es: ", i ," offset: ", offsetreal, "limite: ", limite, "publis[i]: ", Publis[i])
        if i< len(Publis): 
            # print("i es: ", i ,"likes publis: ", Publis[i].Gustas)
            Publis2.append(Publis[i])

    if len(Publis2) == 0:
        # print("hola", "limite: ", limite)
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




@app.route('/PopularesRecomendaciones', methods=['GET'])
@token_required
def PopularesRecomendaciones(current_user):

    Publis = []
    limite=request.headers['limit']
    offsetreal = int(request.headers['offset'])*int(limite)
    paginaExplorados(Publis,current_user,request.headers['tematicas'],request.headers['filtrado'],2)



    Publis.sort(key = orderLikes, reverse=True)

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
        print("hola soy el id: ", Publis2[x].ids)
        guardaRecomendacion(Publis2[x],finalDictionary,current_user)
        i = i + 1

    return json.dumps(finalDictionary, indent = i)


@app.route('/PopularesArticulos', methods=['GET'])
@token_required
def PopularesArticulos(current_user):

    Publis = []
    limite=request.headers['limit']
    offsetreal = int(request.headers['offset'])*int(limite)
    paginaExplorados(Publis,current_user,request.headers['tematicas'],request.headers['filtrado'],1)


    Publis.sort(key = orderLikes, reverse=True)

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
        guardaPDF(Publis2[x],finalDictionary,current_user)
        i = i + 1

    return json.dumps(finalDictionary, indent = i)


def orderLikes(k):
    
    return k.Gustas

def paginaExplorados(Publis,current_user,tematicas,filtrado,art):

    todosUsuarios = Usuario.query.all()
    for nicks in todosUsuarios:
        if nicks.nick != current_user:
            leSigue= db.session.query(Sigue).filter(and_(Sigue.Usuario_Nicka== 'nicks.nick' , Sigue.Usuario_Nickb== 'current_user')).first()
            if leSigue is None:
                preferidas = []
                if tematicas=="pref":
                    tema = select([Prefiere.tema]).where((Prefiere.Usuario_Nicka == current_user))
                    temas = db.session.execute(tema)
                    for row in temas:
                        preferidas.append(row.tema)
                else:
                    preferidas.append(tematicas)

                posts=""
                if filtrado!="":
                    search = "%{}%".format(filtrado)
                    posts =  db.session.query(Publicacion).filter(and_(Publicacion.descripcion.like(search), Publicacion.Usuario_Nicka == nicks.nick)).all()
                else:
                    posts=select([Publicacion.id ]).where(Publicacion.Usuario_Nicka == nicks.nick )
                    posts = db.session.execute(posts)  

                for posteos in posts:
                    pref = False
                    #print("PREFERIDAS: ",preferidas )
                    for temas in preferidas:
                        
                        prefiere = db.session.query(Trata_pub_del_tema).filter(and_(Trata_pub_del_tema.id==posteos.id ,Trata_pub_del_tema.tema== temas)).first()
                        if prefiere:
                            pref = True

                    if pref ==True:
                        existeP = db.session.query(Propia).filter(Propia.id == posteos.id ).count()
                        existeR = db.session.query(Recomendacion).filter(Recomendacion.id == posteos.id ).count()
                        if bool(existeP and art==1):
                            guardarId(Publis,posteos.id)
                        elif bool(existeR and art==2):
                            guardarId(Publis,posteos.id)
                        elif bool(art==3):
                            guardarId(Publis,posteos.id)
     