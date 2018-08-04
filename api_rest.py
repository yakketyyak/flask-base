# -*- coding: utf-8 -*-

from flask import Flask, jsonify, Response, json, request
from flask_restful import Resource, Api
from flaskext.mysql import MySQL
from flask_cors import CORS

from simplecrypt import encrypt

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




#Nous allons créer un user dans la base de données via les données recupérées en POST
@app.route('/flask-base/create',methods=['POST'])
def create():
    cursor = None
    db = None
    try:
        
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


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0')#pour permettre à tout ip d'appeler les services REST