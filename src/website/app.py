from flask import Flask, escape, request, render_template, redirect, url_for, jsonify
import sys
import os
from engine import SearchEngine
from functions import parse_config, isValidConfig

app = Flask(__name__)
config = parse_config('/home/abdurasul/Repos/SearchEngine/config.json')
if not isValidConfig(config):
    raise Exception('Invalid config')
engine = SearchEngine(config)

@app.route('/', methods=['GET'])
def main():
    return render_template('main.html')

@app.route('/document/<int:id>')
def get_document(id):
    doc = engine.get_document(id)
    return render_template('document.html', id=id, doc=doc)

@app.route('/update', methods=['POST'])
def update():
    additions = request.json['additions']
    deletions = request.json['deletions']
    engine.process_crawler_data(additions, deletions)
    return jsonify({"verdict": "1"})

@app.route('/', methods=['POST'])
def search():
    global engine
    query = None
    for key, value in request.form.items():
        query = value
    if query is None or query == '':
        return redirect(url_for('main'))
    res, rquery = engine.search(query)
    docs = engine.get_answers(res)
    return render_template('search.html', oquery=query, rquery=rquery, docs=docs)

if __name__ == '__main__':

    app.run(debug=True, threaded=True)