from flask import Flask, render_template, request, jsonify, session
import requests
import json
from cassandra.cluster import Cluster
import csv
#import requests_cache
#requests_cache.install_cache('crime_api_cache', backend='sqlite', expire_after=36000)

jokes_url_template = 'http://api.icndb.com/jokes/random?exclude=Array'

cluster = Cluster(contact_points=['172.17.0.2'], port=9042)
session = cluster.connect()
app = Flask(__name__)

@app.route('/jokes', methods=['POST','GET'])
def getjoke():
    response = requests.get(jokes_url_template)
    if response.ok:
        parsed = response.json()
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>",parsed)
        joke = parsed['value']['joke'].replace("'","")

        insert = session.execute("""INSERT INTO jokes.data (Id, Joke) VALUES ({}, '{}')""".format(parsed['value']['id'], joke))
        return jsonify(parsed)
    else:
        return jsonify(response.reason)

@app.route('/getjokes', methods=['GET'])
def alljokes():
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    rows = session.execute("""SELECT * from jokes.data""")
    print(rows._current_rows)
    k=rows._current_rows
    if rows:
        return jsonify({'data':k}), 200
    return jsonify({'error':'No data present'}), 404

@app.route('/getjokes/<id>', methods=['GET'])
def one_joke(id):
    rows = session.execute("""SELECT * FROM jokes.data where id = {} ALLOW FILTERING""".format(id))
    print('>>>>>>>>>>>>>>>>>>>>>>>',rows._current_rows)
    if rows:
        return jsonify({'data':rows[0]}), 200
    return jsonify({'message':'Joke for this ID does not exist'}), 404

@app.route('/getjokes/update/<id>/<joke>', methods=['PUT','GET'])
def update_joke(id, joke):

    rows = session.execute("""SELECT * FROM jokes.data WHERE id={} ALLOW FILTERING""".format(id))
    if not rows:
        return jsonify({'error':'No such jokeID exists'}), 404
    rows_update = session.execute("""UPDATE jokes.data set Joke='{}' WHERE id={}""".format(joke, id))
    return jsonify({'ID':id,'NewJoke':joke}), 200

@app.route('/getjokes/delete/<id>', methods=['DELETE','GET'])
def delete_joke(id):
    row=session.execute("""SELECT * FROM jokes.data WHERE id={}""".format(id))
    if row:
        deletedRows=session.execute("""DELETE from jokes.data WHERE id={}""".format(id))
        print('>>>>>>>>>>>>>>>>>>>>>>>>',deletedRows._current_rows)
        return jsonify({'ID':id, 'Message':'Deleted'}), 200
    return jsonify({"message":"This joke doesn't exist"}), 404

if __name__=='__main__':
	app.run(host='0.0.0.0', port=80)
