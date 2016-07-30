from journal import app
from flask import request, jsonify, render_template, Response
import re
import json
import datetime
import logging
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps

#init the db client
client = MongoClient("localhost", 27017)
db = client['journal_db']


@app.route('/journal', methods=['GET'])
def get_journals():
    '''This method returns the list of journals'''
    return Response(dumps(db.collection_names()),
                          mimetype='application/json')

@app.route('/journal/<collection>', methods=['POST'])
def  add_post(collection):
    '''This entrypoint adds a post to a journal'''
    data = request.get_json()
    print(data)
    text = data['text']
    user = data['user']
    category = data['category']
    oid = addPost(text,user,collection, category)
    app.logger.info('Added post: ' + oid+' '+ text[:20])
    return jsonify({"post_created": oid})

@app.route('/journal/<collection>', methods=['DELETE'])
def drop_collection(collection):
    db[collection].drop()
    return jsonify({"journal_deleted":  collection})

@app.route('/journal/<collection>/info', methods=['GET'])
def get_collection_info(collection):
    pass


@app.route('/journal/<collection>/query', methods=['POST'])
def query_post(collection):
    '''This entrypoint query a journal'''
    data = request.get_json()
    coll = db[collection]
    query_json = {}
    if "tags" in data:
        if len(data['tags'])>0:
            query_json["tags"] = { "$all" : data['tags']}
    if "user" in data:
        query_json['user'] = data['user']
    if "properties" in data:
        for p in data['properties']:
            query_json.update(p)
    if "category" in data:
        query_json = data['category']
    #getting limit of n. of items
    lim = data['limit']
    app.logger.info("Query: {}".format(query_json))
    #getting all documents in descending order
    docs = [doc for doc in coll.find(query_json,limit=lim)
                .sort('timestamp',-1)]
    return Response(dumps(docs), mimetype='application/json')


@app.route('/journal/<collection>/<post_id>', methods=['GET'])
def get_post(collection, post_id):
    '''Getting a specific post'''
    doc = db[collection].find_one({'_id':ObjectId(post_id)})
    print(doc)
    return Response(dumps(doc), mimetype='application/json')

@app.route('/journal/<collection>/<post_id>', methods=['DELETE'])
def drop_post(collection, post_id):
    '''Deleting a specific post'''
    db[collection].delete_one({"_id":ObjectId(post_id)})
    return jsonify({"post_deleted": post_id})

def addPost(text, user, collection, category):
    '''This function extracts metadata from a post
    and creates the document to insert in the db'''
    post = {
        "text": text,
        "timestamp": datetime.datetime.utcnow(),
        "tags" : [],
        "props" : {},
        "user" : user,
        "category": category
        }
    #reading metadata
    p_re = re.compile(r'#(?P<prop>\w*?):(?P<value>.*?)(?=[\s#@]|$)')
    t_re = re.compile(r'#(?P<tag>.*?)(?=[\s#:]|$)')
    num_re = re.compile(r'^[\-]?[0-9]*\.?[0-9]+([eE][0-9]+)?$')
    #proprieties
    for m in p_re.finditer(text):
        prop = m.group('prop')
        value =  m.group('value')
        if num_re.match(value):
            value = float(value)
        post['props'][prop] = value
        #proprieties are added also as tags
        if prop not in post['tags']:
            post['tags'].append(prop)
    #tags
    for t in t_re.finditer(text):
        tag = t.group('tag')
        if tag not in post['tags']:
            post['tags'].append(t.group('tag'))
    #inserting in the dictionary
    oid = db[collection].insert_one(post).inserted_id
    return str(oid)