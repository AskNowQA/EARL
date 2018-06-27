#!/usr/bin/python

from flask import request
from flask import Flask
from gevent.pywsgi import WSGIServer
import json,sys,requests

from ShallowParser import ShallowParser
from ErPredictor import ErPredictor
from  TextMatch import TextMatch
from JointLinker import JointLinker
from ReRanker import ReRanker

s = ShallowParser()
e = ErPredictor()
t = TextMatch()
j = JointLinker()
r = ReRanker()

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)


def prepare(rerankedlist, nlquery):
    combinedrerankedlist = {}
    combinedrerankedlist['question'] = nlquery
    combinedrerankedlist['relations'] = []
    combinedrerankedlist['entities'] = []
    combinedrerankedlist['kb'] = 'dbpedia'
    searchfrom = 0
    for idx,chunk in enumerate(rerankedlist['chunktext']):
        chunkdict = {}
        chunkdict['uris'] = []
        chunkdict['surface'] = [chunk['surfacestart'], chunk['surfacelength']]
        #print rerankedlist
        rerankedlist['rerankedlists'][idx] = rerankedlist['rerankedlists'][idx]
        confidencescoresum = sum([ x[0] for x in rerankedlist['rerankedlists'][idx]])
        for uri in rerankedlist['rerankedlists'][idx]:
          chunkdict['uris'].append({'uri': uri[1], 'confidence': uri[0]/float(confidencescoresum)})
        if rerankedlist['ertypes'][idx] == 'entity':
            combinedrerankedlist['entities'].append(chunkdict)
        else:
            combinedrerankedlist['relations'].append(chunkdict)
    return combinedrerankedlist 
        
def getsparql(preparedlist):
    r = requests.post("http://localhost:5000/qg/api/v1.0/query", data=json.dumps(preparedlist), headers={"content-type": "application/json"}) # This sends a request to https://github.com/AskNowQA/SQG
    print r
    return json.loads(r.text)

def solvesparql(sparql):
    answers = []
    if sparql:
        for query in sparql['queries']:
            q = query
            url = "http://131.220.9.219/sparql" # or http://dbpedia.org/sparql
            p = {'query': q}
            h = {'Accept': 'application/json'}
            r = requests.get(url, params=p, headers=h)
            print("code {}\n".format(r.status_code))
            d =json.loads(r.text)
            try:
                answers.append(d['results']['bindings'])
            except Exception,e:
                answers.append([])
            break #Answer only top sparql
    return answers
        

@app.route('/processQuery', methods=['POST'])
def processQuery():
    d = request.get_json(silent=True)
    nlquery = d['nlquery']
    print "Query: %s"%json.dumps(nlquery)
    chunks = s.shallowParse(nlquery)
    print "Chunks: %s"%json.dumps(chunks)
    erpredictions = e.erPredict(chunks)
    print "ER Predictions: %s"%json.dumps(erpredictions)
    topkmatches = t.textMatch(erpredictions)
    print "Top text matches: %s"%json.dumps(topkmatches)
    jointlylinked = j.jointLinker(topkmatches)
    print "ER link features: %s"%json.dumps(jointlylinked)
    rerankedlist = r.reRank(jointlylinked)
    print "Re-reanked lists: %s"%json.dumps(rerankedlist)
    return json.dumps(rerankedlist)

@app.route('/answer', methods=['POST'])
def answer():
    d = request.get_json(silent=True)
    nlquery = d['nlquery']
    print "Query: %s"%json.dumps(nlquery)
    chunks = s.shallowParse(nlquery)
    print "Chunks: %s"%json.dumps(chunks)
    erpredictions = e.erPredict(chunks)
    print "ER Predictions: %s"%json.dumps(erpredictions)
    topkmatches = t.textMatch(erpredictions)
    print "Top text matches: %s"%json.dumps(topkmatches)
    jointlylinked = j.jointLinker(topkmatches)
    print "ER link features: %s"%json.dumps(jointlylinked)
    rerankedlist = r.reRank(jointlylinked)
    print "Re-reanked lists: %s"%json.dumps(rerankedlist)
    preparedlist = prepare(rerankedlist, nlquery) #For hamid's query processor
    print "Pre-pared list: %s"%json.dumps(preparedlist)
    sparql = getsparql(preparedlist)
    print "sparql: %s"%json.dumps(sparql)
    answers = solvesparql(sparql)
    print "answer: %s"%json.dumps(answers)
    return json.dumps(answers)


if __name__ == '__main__':
    http_server = WSGIServer(('', int(sys.argv[1])), app)
    http_server.serve_forever()
