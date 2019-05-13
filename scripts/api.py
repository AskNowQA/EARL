#!/usr/bin/python

from flask import request
from flask import Flask
from gevent.pywsgi import WSGIServer
import json,sys,requests,logging
from ShallowParser import ShallowParser
from ErPredictorES import ErPredictorES
from  TextMatch import TextMatch
from JointLinker import JointLinker
from ReRanker import ReRanker
import json
logging.basicConfig(filename='/var/log/asknowlog',level=logging.INFO)
s = ShallowParser()
e = ErPredictorES()
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
        if rerankedlist['ertypes'][idx] == 'entity':
            rerankedlist['rerankedlists'][idx] = rerankedlist['rerankedlists'][idx][:1] #Send only top entity
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
    

def isSingleEntity(topkmatches):
    if len(topkmatches) == 1:
        if topkmatches[0]['class'] == 'entity':
            return True
        else:
            return False  
    else:
        return False

def numberOfNodes(topkmatches):
    return len(topkmatches)

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
    #print "Query: %s"%json.dumps(nlquery) 
    chunks = None
    if 'chunks' not in d.keys():
        chunks = s.shallowParse(nlquery)
    else:
        chunks = d['chunks']
    print "Chunks: %s"%json.dumps(chunks)
    erpredictions = e.erPredict(chunks)
    print "ER Predictions: %s"%json.dumps(erpredictions)
    topkmatches = t.textMatch(erpredictions, pagerankflag)
    print "Top text matches: %s"%json.dumps(topkmatches)
    jointlylinked = j.jointLinker(topkmatches)
    print "ER link features: %s"%json.dumps(jointlylinked)
    rerankedlist = r.reRank(jointlylinked)
    print "Re-reanked lists: %s"%json.dumps(rerankedlist)
    return json.dumps(rerankedlist)

@app.route('/answerdetail', methods=['POST'])
def answerdetail():
    d = request.get_json(silent=True)
    nlquery = d['nlquery']
    if 'remote_addr' not in d:
        d['remote_addr'] = None
    pagerankflag = False
    try:
        if 'pagerankflag' in d:
            pagerankflag = d['pagerankflag']
    except Exception,err:
        print err
        return 422
    print "Query: %s"%json.dumps(nlquery)
    chunks = s.shallowParse(nlquery)
    print "Chunks: %s"%json.dumps(chunks)
    erpredictions = e.erPredict(chunks)
    print "ER Predictions: %s"%json.dumps(erpredictions)
    topkmatches = t.textMatch(erpredictions, pagerankflag)
    print "Top text matches: %s"%json.dumps(topkmatches, pagerankflag)
    if not isSingleEntity(topkmatches):
        if numberOfNodes(topkmatches) > 4:
           print numberOfNodes(topkmatches)
           logging.info(json.dumps({'remote_addr':d['remote_addr'],'answers':[],'sparql':[],'preparedlist':[],'topkmatches':topkmatches,'erpredictions':erpredictions,'chunks':chunks,'question':nlquery}))
           return json.dumps({'answers':[],'sparql':'','preparedlist':'','topkmatches':topkmatches,'erpredictions':erpredictions,'chunks':chunks,'question':nlquery})
        else:
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
            logging.info(json.dumps({'remote_addr':d['remote_addr'],'answers':answers,'sparql':sparql,'preparedlist':preparedlist,'topkmatches':topkmatches,'erpredictions':erpredictions,'chunks':chunks,'question':nlquery}))
            return json.dumps({'answers':answers,'sparql':sparql,'preparedlist':preparedlist,'topkmatches':topkmatches,'erpredictions':erpredictions,'chunks':chunks,'question':nlquery})
    else:
        logging.info(json.dumps({'remote_addr':d['remote_addr'],'answers':[[{'u_0': {'type': 'uri','value': topkmatches[0]['topkmatches'][0]}}]],'sparql':[],'preparedlist':[],'topkmatches':topkmatches,'erpredictions':erpredictions,'chunks':chunks,'question':nlquery}))
        return json.dumps({'answers':[[{'u_0': {'type': 'uri','value': topkmatches[0]['topkmatches'][0]}}]],'sparql':'','preparedlist':'','topkmatches':topkmatches,'erpredictions':erpredictions,'chunks':chunks,'question':nlquery})
        


if __name__ == '__main__':
    http_server = WSGIServer(('', int(sys.argv[1])), app)
    http_server.serve_forever()
