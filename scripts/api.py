#!/usr/bin/python

from flask import request
from flask import Flask
from gevent.wsgi import WSGIServer
import json,sys

#from ShallowParser import shallowParse
from ErPredictor import erPredict
#from  TextMatch import textMatch
#from JointLinker import jointLinker
#from ReRanker import reRanker


reload(sys)
sys.setdefaultencoding('utf8')


@app.route('/processQuery', methods=['POST'])
def processQuery():
    d = request.get_json(silent=True)
    nlquery = d['nlquery']
    #chunks = shallowParse(nlquery)
    erpredictions = erPredict(chunks)
    #topkmatches = textMatch(erpredictions)
    #jointlylinked = jointLinker(topkmatches)
    #rerankedlist = reRank(jointlylinked)
    #return rerankedlist
    return ''



if __name__ == '__main__':
    http_server = WSGIServer(('', int(sys.argv[1])), app)
    http_server.serve_forever()
