from flask import Flask, render_template, request, jsonify, redirect, url_for, abort
from elasticsearch import Elasticsearch
from result import Result


app = Flask(__name__)
es = Elasticsearch()

def search(keyword, claim, evidence):
    body = {
        "query": {
            "query_string": {
                "fields": ["nodes.text"],
                "query": keyword
            }
        }
    }

    res = es.search(index="testdb.sadface", body=body)

    values = []

    for val in res['hits']['hits']:
        for node in val['_source']['nodes']:
            if (('claim' in node['metadata']['type'] and claim is True) or ('evidence' in node['metadata']['type'] and evidence is True)) and keyword.lower() in node['text'].lower():
                values.append(Result(node['text'], node['metadata']['type'], node['id'], val['_source']['metadata']['core']['id'], val['_source']['metadata']['extended']))

    return values

@app.route('/')
def root():
    return render_template('home.html')

@app.route('/results/', methods=['GET','POST'])
def results():
    if request.method == 'GET':
        return redirect(url_for('root'))
    keyword = request.form['name']
    keytypeclaim = True
    keytypeevidence = True
    options = request.form['options']

    if options == 'Claim':
        keytypeevidence = False

    if options == 'Evidence':
        keytypeclaim = False

    jsonout = jsonify(search(keyword, keytypeclaim, keytypeevidence))
    return render_template('results.html', len=len(jsonout.json), values=jsonout.json, keyword=keyword, options=options)

@app.route('/doc/<id>')
def doc(id):
    body = {
        "query": {
            "query_string": {
                "fields": ["metadata.core.id"],
                "query": id
            }
        }
    }

    res = es.search(index="testdb.sadface", body=body)

    if len(res['hits']['hits']) > 0:
        metadata = res['hits']['hits'][0]['_source']['metadata']['extended']
        nodes = res['hits']['hits'][0]['_source']['nodes']
        return render_template('document.html', id=id, values=nodes, len=len(nodes), metadata=metadata)
    else:
        abort(404, descrption="Document not found")

@app.route('/doc/<id>/download')
def download(id):
    body = {
        "query": {
            "query_string": {
                "fields": ["id"],
                "query": id
            }
        }
    }

    res = es.search(index="testdb.sadface", body=body)

    if len(res['hits']['hits']) > 0:
        output = res['hits']['hits'][0]['_source']
        output['edges'] = []
        return jsonify(output)
    else:
        abort(404, descrption="Document not found")

app.errorhandler(404)
def notfound(e):
    return jsonify(error=str(e)), 404


app.run(host='localhost',port=5000,debug=True)