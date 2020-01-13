#!/usr/bin/python

from flask import request
from flask import Flask
from gevent.pywsgi import WSGIServer
import json,sys,requests,logging
from ERSpanPredictor import ERSpanDetector
from  TextMatch import TextMatch
from ReRanker import ReRanker
import json
logging.basicConfig(filename='/var/log/asknow/earl.log',level=logging.INFO)
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
    reranked = []
    print "Query: %s"%json.dumps(nlquery) 
    reranked = r.rerank(nlquery)
    print "ReRanked lists: %s"%json.dumps(reranked)
    return json.dumps(reranked)

if __name__ == '__main__':
    http_server = WSGIServer(('', int(sys.argv[1])), app)
    http_server.serve_forever()
