from journal import app
from flask import render_template
from journal import journal_api as japi

@app.route('/journal/<collection>', methods=['GET'])
def welcome(collection):
    tags = japi.count_tags(collection)
    cats = japi.count_categories(collection)
    return render_template('collection_index.template',
            tags= tags,
            tags_dict= dict(tags),
            cats = cats,
            cats_dict = dict(cats),
            total_posts = sum(cats.values()),
            docs= japi.get_last_posts(collection, 10))
