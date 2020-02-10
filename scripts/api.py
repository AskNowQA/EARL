#!/usr/bin/python

from flask import request
from flask import Flask
from gevent.pywsgi import WSGIServer
import json,sys,requests,logging
import json
from Vectoriser import Vectoriser
from PointerNetworkLinker import PointerNetworkLinker
logging.basicConfig(filename='/var/log/asknow/earl.log',level=logging.INFO)
v = Vectoriser()
p = PointerNetworkLinker()
#j = JointLinker()

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
    print("Query: %s"%json.dumps(nlquery)) 
    vectors = v.vectorise(nlquery)
    print("Vectorisation length %d"%(len(vectors)))
    entities = p.link(vectors)
    return json.dumps({'nlquery':d['nlquery'],'entities':entities}, indent=4, sort_keys=True)

if __name__ == '__main__':
    http_server = WSGIServer(('', int(sys.argv[1])), app)
    http_server.serve_forever()
