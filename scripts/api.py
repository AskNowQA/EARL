#!/usr/bin/python

from flask import request
from flask import Flask
from gevent.pywsgi import WSGIServer
import json,sys,requests,logging
from ERSpanPredictor import ERSpanDetector
from  TextMatch import TextMatch
from JointLinker import JointLinker
from ReRanker import ReRanker
import json
logging.basicConfig(filename='/var/log/asknow/earl.log',level=logging.INFO)
e = ERSpanDetector()
t = TextMatch()
j = JointLinker()
r = ReRanker()

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)



@app.route('/processQuery', methods=['POST'])
def processQuery():
    d = request.get_json(silent=True)
    print d
    nlquery = d['nlquery']
    pagerankflag = False
    try:
        if 'pagerankflag' in d:
            pagerankflag = d['pagerankflag']
    except Exception,err:
        print err
        return 422
    print "Query: %s"%json.dumps(nlquery) 
    erpredictions = e.erspan(nlquery)
    print "ER Predictions: %s"%json.dumps(erpredictions)
    rerankedlists = []
    for erprediction in erpredictions:
        topkmatches = t.textMatch(erprediction, pagerankflag)
        print "Top text matches: %s"%json.dumps(topkmatches)
        jointlylinked = j.jointLinker(topkmatches)
        print "ER link features: %s"%json.dumps(jointlylinked)
        rerankedlist = r.reRank(jointlylinked)
        rerankedlists.append(rerankedlist)
        print "Re-reanked lists: %s"%json.dumps(rerankedlist)
    print(json.dumps(rerankedlists))
    return json.dumps(rerankedlists, indent=4, sort_keys=True)

if __name__ == '__main__':
    http_server = WSGIServer(('', int(sys.argv[1])), app)
    http_server.serve_forever()
