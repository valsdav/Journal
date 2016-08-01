from journal import app
from flask import render_template
from journal import journal_api as japi

@app.route('/journal/<collection>', methods=['GET'])
def welcome(collection):
    return render_template('collection_index.template',
            tags=sorted(list((japi.count_tags(collection).keys()))),
            docs= japi.get_last_posts(collection, 10))
