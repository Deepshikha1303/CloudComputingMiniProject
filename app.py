from flask import Flask, render_template, request, jsonify,session, redirect, g
import uuid
from cassandra.cluster import Cluster

cluster = Cluster(contact_points=['172.17.0.2'], port=9042)
session = cluster.connect()
app = Flask(__name__)

@app.route('/pokemon', methods=['GET'])
def pokemons():
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    rows = session.execute("""SELECT * from pokemon.stats""")
    print(rows._current_rows)
    k=rows._current_rows
    if rows:
        return jsonify({'data':k})
    return jsonify({'error':'No data present'})

@app.route('/pokemon/<name>', methods=['GET'])
def one_pokemon(name):
    #name = request.json.get('name')
    name=name.capitalize()
    print('name>>>>>>>',name)
    rows = session.execute("""SELECT * FROM pokemon.stats where name = '{}' ALLOW FILTERING""".format(name))
    print('>>>>>>>>>>>>>>>>>>>>>>>',rows._current_rows)
    if rows:
        return jsonify({'data':rows[0]})
    return jsonify({'message':'no such pokemon exists'})

@app.route('/pokemon/<name>/<type1>/<type2>/<total>/<hp>/<attack>/<defence>/<spAttack>/<spDefence>/<speed>/<generation>/<legendary>', methods=['POST', 'GET'])
def add_pokemon(name, type1, type2, total, hp, attack, defence, spAttack, spDefence, speed, generation, legendary):

    name=name.capitalize()
    type1=type1.capitalize()
    type2=type2.capitalize()
    legendary=legendary.capitalize()    
    print("test>>>>>>>>>>>>>>>>>>>>",name,"    ",type1,"     ",type2,"    ",total,"      ",legendary)
    #if not request.json or not name:
    if not name:
        return jsonify({'error':'The pokemon needs to have a name'}), 400
    rows = session.execute("""SELECT * FROM pokemon.stats WHERE name = '{}' ALLOW FILTERING""".format(name))
    if rows:
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",rows[0][0])
        if rows[0].name==name:
            return jsonify({'message':'Pokemon already exists', 'pokemon':rows[0]}), 400
    insert = session.execute("""INSERT INTO pokemon.stats (Name, Type1, Type2, Total, HP, Attack, Defence, SpAttack, SpDefence, Speed, Generation, Legendary) VALUES ('{}','{}','{}',{},{},{},{},{},{},{},{},{})""".format(name, type1, type2, total, hp, attack, defence, spAttack, spDefence, speed, generation, legendary))
    return jsonify({'Name':name, 'Type1':type1, 'Type2':type2, 'Total':total, 'HP':hp, 'Attack':attack, 'Defence':defence, 'SpAttack':spAttack, 'SpDefence':spDefence, 'Speed':speed, 'Generation':generation, 'Legendary':legendary})

@app.route('/pokemon/update/<name>/<total>/<attack>/<defence>/<speed>', methods=['PUT','GET'])
def update_characteristics(name, total, attack, defence, speed):

    name=name.capitalize()
    #only total, attack, defence, and speed are updateable
    rows = session.execute("""SELECT * FROM pokemon.stats WHERE name='{}' ALLOW FILTERING""".format(name))
    if not rows:
        return jsonify({'error':'No such pokemon exists'})
    rows_update = session.execute("""UPDATE pokemon.stats set Total={}, Attack={}, Defence={}, Speed={} WHERE Name='{}'""".format(total, attack, defence, speed,name))
    return jsonify({'Name':name, 'NewTotal':total, 'NewAttack':attack, 'Newdefence':defence, 'NewSpeed':speed})

@app.route('/pokemon/delete/<name>', methods=['DELETE','GET'])
def delete_pok(name):
    name=name.capitalize()
    #row = session.execute("""DELETE * FROM table pokemon.stats WHERE Name='{}'""".format(name))
    prepared_statement=session.prepare('SELECT * FROM pokemon.stats WHERE name=?')
    rows=session.execute(prepared_statement, (name,))
    if rows:
        prepared_statement=session.prepare('DELETE from pokemon.stats WHERE name=?')
        rows=session.execute(prepared_statement, (name,))
        print('>>>>>>>>>>>>>>>>>>>>>>>>',rows._current_rows)
        return jsonify({'Name':name, 'Message':'Deleted'})
    return jsonify({"message":"This pokemon doesn't exist"})

if __name__=='__main__':
	app.run(host='0.0.0.0', port=80)
