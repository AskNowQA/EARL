#!/usr/bin/python

from flask import request
from flask import Flask
from gevent.wsgi import WSGIServer
import json,sys

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
    searchfrom = 0
    for idx,chunk in enumerate(rerankedlist['chunktext']):
        chunkdict = {}
        chunkdict['uris'] = []
        startinglocation = nlquery.find(chunk, searchfrom)
        searchfrom = startinglocation+1
        chunkdict['surface'] = [startinglocation, len(chunk)]
        #print rerankedlist
        rerankedlist['rerankedlists'][idx] = rerankedlist['rerankedlists'][idx][:10] #Hamid needs top 10 only
        confidencescoresum = sum([ x[0] for x in rerankedlist['rerankedlists'][idx]])
        for uri in rerankedlist['rerankedlists'][idx]:
          chunkdict['uris'].append({'uri': uri[1], 'confidence': uri[0]/float(confidencescoresum)})
        if rerankedlist['ertypes'][idx] == 'entity':
            combinedrerankedlist['entities'].append(chunkdict)
        else:
            combinedrerankedlist['relations'].append(chunkdict)
    return combinedrerankedlist 
        
        
    

@app.route('/processQuery', methods=['POST'])
def processQuery():
    d = request.get_json(silent=True)
    nlquery = d['nlquery']
    print "Query: %s"%nlquery
    chunks = s.shallowParse(nlquery)
    print "Chunks: %s"%chunks
    erpredictions = e.erPredict(chunks)
    print "ER Predictions: %s"%erpredictions
    topkmatches = t.textMatch(erpredictions)
    print "Top text matches: %s"%topkmatches
    jointlylinked = j.jointLinker(topkmatches)
    print "ER link features: %s"%jointlylinked
    rerankedlist = r.reRank(jointlylinked)
    print "Re-reanked lists: %s"%rerankedlist
    preparedlist = prepare(rerankedlist, nlquery) #For hamid's query processor
    return json.dumps(preparedlist)

if __name__ == '__main__':
    http_server = WSGIServer(('', int(sys.argv[1])), app)
    http_server.serve_forever()
