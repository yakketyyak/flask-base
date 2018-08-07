# -*- coding: utf-8 -*-

from flask import Flask, jsonify, Response, json, request
from flask_restful import Resource, Api
from flaskext.mysql import MySQL
from flask_cors import CORS
import re

from passlib.context import CryptContext

mysql = MySQL()


app = Flask(__name__)
api = Api(app)
CORS(app)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'flask_base'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


#la référence de ce code http://blog.tecladocode.com/learn-python-encrypting-passwords-python-flask-and-passlib/
pwd_context = CryptContext(
        schemes=["pbkdf2_sha256"],
        default="pbkdf2_sha256",
        pbkdf2_sha256__default_rounds=30000
)



#Nous allons créer un user dans la base de données via les données recupérées en POST
#https://www.pythonanywhere.com/forums/topic/11589/
@app.route('/flask-base/create',methods=['POST'])
def create():
    cursor = None
    db = None
    try:
        dataReq = request.data
        dataReq = json.loads(dataReq)
        if not isNotEmpty(dataReq.get('datas')):
             return jsonify({'hasError' : True , 'status': {'code':'900','message':'La liste est vide' }})

        db = mysql.connect()
        cursor = db.cursor()
        for user in dataReq.get('datas'):
            
            if isBlank(user.get('userName')):#user.get('email') n'est pas source d'erreur contrairement a user['email']
                return jsonify({'hasError' : True , 'status': {'code':'900','message':'L\' identifiant est obligatoire' }})
            
            if isBlank(user.get('password')):#user.get('email') n'est pas source d'erreur contrairement a user['email']
                return jsonify({'hasError' : True , 'status': {'code':'900','message':'Le mot de passe est obligatoire' }})
           
            hashedPassword = encrypt_password(user.get('password'))
            user['password'] = hashedPassword
            user['user_name'] = user.pop('userName')#eviter une erreur lors de l'insertions en base
            #la colonne en base est user_name (on remplace donc userName par user_name)
            createUser(cursor,user)
            if cursor.lastrowid < 0:
                return jsonify({'hasError' : True , 'status': {'code':'900','message':'Errur d\'insertion' }})
        
        if db != None:
            db.commit()
    except Exception as e:
        print (e)
        if db != None:
            db.rollback()

        if cursor != None:
             cursor.close()
        return jsonify({'hasError' : True , 'status': {'code':'900','message':str(e) }})
    finally:
        if cursor != None:
            cursor.close()

    return jsonify({ 'status': {},'hasError' : False})


#USER
def createUser(cursor,user):
    try:
        insertKeys =  ','.join('{}'.format(key) for key in user)
        insertValues =  ','.join('"{}"'.format(value) for value in user.values())
        query = "INSERT INTO user({insertKeys})  VALUES({values})".format(insertKeys = insertKeys, values = insertValues)
        cursor.execute(query)

    except Exception as e:
        print (e)
        return jsonify({'hasError' : True , 'message' :str(e)})

    return jsonify({'hasError' : False})

def getUserByKey(cursor,userKey,userValue):
    query = "SELECT * FROM user  where {key} = '{value}'" .format(key = userKey,value = userValue)
    try:

        cursor.execute(query)
        user = [dict((cursor.description[i][0], value) for i, value in enumerate(row) if value != None) for row in cursor.fetchall()]
      
    except Exception as e:
        print (e)
        return jsonify({'hasError' : True, 'message' : str(e)})

    return jsonify({'user' : user, 'hasError' : False})

def userUpdate(cursor,user):
    try:
        insertValues = updateValues(user)

        userId = user.get('id')
        query = "UPDATE user set{values} where id={id} ".format(id = userId, values = insertValues)
        cursor.execute(query)

    except Exception as e:
        print (e)
        return jsonify({'hasError' : True , 'message' :str(e)})

    return jsonify({ 'hasError' : False})

def userDelete(cursor,userIds):
    try:
        format_strings = ','.join(['%s'] * len(userIds))
        query = "DELETE FROM user where id in (%s) " % format_strings
        cursor.execute(query,tuple(userIds,))

    except Exception as e:
        print (e)
        return jsonify({'hasError' : True , 'message' : str(e)})

    return jsonify({ 'hasError' : False})

def userGetAll(requestData,cursor):
    query = "SELECT * from user "
    
    if requestData != None and isNotBlank(requestData.get('userName')):
        if "where" not in query: 
            query = query +  " where `user_name` = {key}".format(key =  requestData['userName'])
        else:
           query = query +  " and `user_name` = {key}".format(key =  requestData['userName'])  
       

    if requestData != None and  isNotBlank(requestData.get('email')):
       if "where" not in query: 
           query = query +  " where `email` = {value}".format(value =  requestData['email'])
       else:
           query = query +  " and `email` = {value}".format(value =  requestData['email'])  

    query = query + " order by id desc"

    index = 0
    size = 0
    if requestData != None and isInteger(requestData.get('index')):
        index = requestData['index']

    if requestData != None and isInteger(requestData.get('size')):
        size = requestData['size']
    
    if index >= 0 and size > 0:
        fromIndex = index * size
        completeQuery = " LIMIT {size} OFFSET {fromIndex} ".format(fromIndex = fromIndex, size=size)
        query = query + completeQuery

    try:
       cursor.execute(query)
       users = [dict((cursor.description[i][0], value)
              for i, value in enumerate(row)) for row in cursor.fetchall()]
    except Exception as e:
        print (e)
        return jsonify({'hasError' : True, 'message' :str(e)})

    return jsonify({'users' : users , 'hasError' : False})

def encrypt_password(password):
    return pwd_context.encrypt(password)


def check_encrypted_password(password, hashed):
    return pwd_context.verify(password, hashed)

def updateValues(toUpdate):
    updates = list()
    try:
        for key, value in toUpdate.iteritems(): 
            val = "" +'{key}'.format(key = key) + "=" + '"{value}"'.format(value = value)
            updates.append(val)
        updates = ','.join(str(e) for e in updates)
    
    except Exception as e:
        print (e)
    
    return updates

def isNotBlank (strValue):
    return bool(strValue != None and str(strValue) and str(strValue).strip())

def isBlank (strValue):
    return not (strValue != None and str(strValue) and str(strValue).strip())

def  isNotEmpty(listOfObject):
    return bool(listOfObject != None and len(listOfObject) > 0)


def isInteger(value):
    try:
        if value is None:
            return False
            
        value = int(value)
        return True
    except ValueError:
        if isBlank(value):
            return False  
        if value.isdigit():
            return True
        else:
            return False  

    return False


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0')#pour permettre à tout ip d'appeler les services REST
