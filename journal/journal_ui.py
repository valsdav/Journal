from journal import app
from flask import render_template

@app.route('/journal/<collection>', methods=['GET'])
def welcome(collection):
    return render_template('collection_index.template')
