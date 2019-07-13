from flask import Flask, render_template, request, jsonify
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
                values.append(Result(node['text'], node['metadata']['type'], node['id'], val['_source']['id'], val['_source']['metadata']))

    return values

@app.route('/')
def root():
    return render_template('home.html')

@app.route('/results/', methods=['POST'])
def results():
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


@app.route('/test/')
def test():
    keyword = 'this'
    keytypeclaim = True
    keytypeevidence = True

    jsonout = jsonify(search(keyword,keytypeclaim,keytypeevidence))
    return render_template('results.html', len=len(jsonout.json), values=jsonout.json)

app.run(host='localhost',port=5000,debug=True)