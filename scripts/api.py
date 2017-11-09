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
    return json.dumps(rerankedlist)

if __name__ == '__main__':
    http_server = WSGIServer(('', int(sys.argv[1])), app)
    http_server.serve_forever()
