from journal import app
from flask import request, jsonify, render_template, Response
import re
import json
import datetime
import logging
from journal.queries import *
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps
from collections import OrderedDict

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
    text = data['text']
    user = data['user']
    category = data['category']
    oid, tags = add_post(text,user,collection, category)
    app.logger.info('Added post: ' + oid+' '+ text[:20])
    return get_post(collection, oid)

@app.route('/journal/<collection>', methods=['DELETE'])
def drop_collection(collection):
    db[collection].drop()
    return jsonify({"journal_deleted":  collection})

@app.route('/journal/<collection>/metadata', methods=['GET', 'POST'])
def get_collection_info(collection):
    if request.method == "GET":
        return jsonify({"tags":get_tags_metadata(collection),
                    "categories": get_categories_metadata(collection)})
    elif request.method =="POST":
        data = request.get_json()
        if data['method'] == "related_tags":
            tags_metadata = db['journal_metadata'].find_one({"collection":collection})
            if tags_metadata == None:
                db['journal_metadata'].insert_one(
                        {"collection": collection, "tags": []})
                return jsonify({"related_tags": []})
            rel_tags = []
            for t in tags_metadata['tags']:
                if t['tag'] in data['tags']:
                    for tr in t['related_tags']:
                        if tr not in rel_tags:
                            rel_tags.append(tr)
            return jsonify({'related_tags': rel_tags})


def get_tags_metadata(collection):
    '''This function returns the tags used in the collection'''
    tags_metadata = db['journal_metadata'].find_one({"collection":collection})
    if tags_metadata == None:
        db['journal_metadata'].insert_one(
                {"collection": collection, "tags": []})
        return {}
    tags = {}
    for t in tags_metadata['tags']:
        tags[t['tag']] = t['total_used']
    result = OrderedDict()
    for k in  sorted(tags, key=tags.get, reverse=True):
        result[k] = tags[k]
    return result

def get_categories_metadata(collection):
    '''This function returns the categories used in the collection'''
    pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    result = OrderedDict()
    for t in db[collection].aggregate(pipeline):
        result[t['_id']] = t['count']
    return result


def get_last_posts(collection, limit):
    '''This function return the last post in the collection'''
    coll = db[collection]
    docs = [doc for doc in coll.find({},limit=limit)
                .sort('timestamp',-1)]
    return docs


@app.route('/journal/<collection>/query', methods=['POST'])
def query_post(collection):
    '''This entrypoint query a journal'''
    data = request.get_json()
    coll = db[collection]
    query_data = parse_query(data['query'])
    query_json = {}
    query_json.update(query_data['query'])
    if "user" in data:
        query_json['user'] = data['user']
    if "properties" in data:
        for p in data['properties']:
            query_json.update(p)
    if "category" in data:
        if data['category'] != "ALL":
            query_json['category']= data['category']
    #getting limit of n. of items
    lim = data['limit']
    #getting all documents in descending order
    docs = [doc for doc in coll.find(query_json,limit=lim)
                .sort('timestamp',-1)]
    #getting related_tags in order
    rel_tags = {}
    for doc in docs:
        for tg in doc['tags']:
            if tg in query_data['tags']:
                continue
            if tg in rel_tags:
                rel_tags[tg] +=1
            else:
                rel_tags[tg] = 1
    related_tags = OrderedDict()
    for k in  sorted(rel_tags, key=rel_tags.get, reverse=True):
        related_tags[k] = rel_tags[k]
    #result object
    result =  {"docs" : docs, "related_tags":related_tags}
    app.logger.info("Query: {}, results: {}".format(query_json, len(docs)))
    return Response(dumps(result), mimetype='application/json')


@app.route('/journal/<collection>/<post_id>', methods=['GET'])
def get_post(collection, post_id):
    '''Getting a specific post'''
    doc = db[collection].find_one({'_id':ObjectId(post_id)})
    return Response(dumps(doc), mimetype='application/json')


@app.route('/journal/<collection>/<post_id>', methods=['DELETE'])
def drop_post(collection, post_id):
    '''Deleting a specific post'''
    db[collection].delete_one({"_id":ObjectId(post_id)})
    return jsonify({"post_deleted": post_id})


def add_post(text, user, collection, category):
    '''This function extracts metadata from a post
    and creates the document to insert in the db'''
    post = {
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
    #final text without tags and properties
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
    #adding the fixed text
    post['text'] = text
    #inserting in the dictionary
    oid = db[collection].insert_one(post).inserted_id
    #inserting the tags metadata
    add_tags(post['tags'], collection)
    return (str(oid),post['tags'])

def add_tags(tags, collection):
    '''This function updates the metadata document for the collection
    after a new post'''
    tags_metadata = db['journal_metadata'].find_one({"collection":collection})
    if tags_metadata == None:
        tags_metadata = {"collection": collection, "tags": []}
    mtags = [tg['tag'] for tg in tags_metadata['tags']]
    for tag in tags:
        if tag not in mtags:
            tags_metadata['tags'].append({"tag": tag,
                 "total_used": 1, "related_tags":{}})
            mtags.append(tag)
    for tag in tags:
        for tgm in tags_metadata['tags']:
            if (tag != tgm['tag']) and (tgm['tag'] in tags):
                if tag in tgm['related_tags']:
                    tgm['related_tags'][tag] +=1
                else:
                    tgm['related_tags'][tag] = 1
            elif (tag == tgm['tag']):
                tgm['total_used'] +=1

    result = db['journal_metadata'].update_one(
            {"collection":collection},
            {"$set": tags_metadata},
            upsert=True)
