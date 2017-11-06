#!/usr/bin/python

from flask import request
from flask import Flask
from gevent.wsgi import WSGIServer
import json,sys
import itertools
from operator import itemgetter
from pybloom import BloomFilter

f = open('blooms/bloom1hoppredicate.pickle')
bloom1hoppred = BloomFilter.fromfile(f)
f.close()

f = open('blooms/bloom1hopentity.pickle')
bloom1hopentity = BloomFilter.fromfile(f)
f.close()

f = open('blooms/bloom2hoppredicate.pickle')
bloom2hoppredicate = BloomFilter.fromfile(f)
f.close()

f = open('blooms/bloom2hoptypeofentity.pickle')
bloom2hoptypeofentity = BloomFilter.fromfile(f)
f.close()


reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)

@app.route('/findBloomPaths', methods=['POST'])
def findBloomPaths():
    d = request.get_json(silent=True)
    es_content = d['ES_content']
    correct = d['correct']
    lists = []
    count = 1
    for listitem in es_content:
        lists.append(listitem['list'+str(count)])
        count += 1
    sequence = range(len(lists))
    result = []
    finalresult = {}
    nodestats = {}
    nodescorecounter = {}
    for perm in itertools.permutations(sequence, len(lists)):
        listpermutation = [lists[i] for i in perm]
        for sequence in itertools.product(*listpermutation):
            pathlength = 0
            sumhopspath = 0
            for i in range(len(sequence) - 1):
                s = sequence[i]['uri']+':'+sequence[i+1]['uri']
                if s in bloom1hoppred:
                    pathlength += 1
                    sumhopspath += 0.5
                if s in bloom1hopentity:
                    pathlength += 1
                    sumhopspath += 1.0
                if s in bloom2hoppredicate:
                    pathlength += 1
                    sumhopspath += 1.5
                if s in bloom2hoptypeofentity:
                    pathlength += 1
                    sumhopspath += 2 
            for uriset in sequence:
                if uriset['uri'] not in nodescorecounter:
                    nodescorecounter[uriset['uri']] = {'pathlength':0, 'sumhopspath':0}
                nodescorecounter[uriset['uri']]['pathlength'] += pathlength/float(len(lists))
                nodescorecounter[uriset['uri']]['sumhopspath'] += sumhopspath/float(len(lists))
    nodescorecounter = [(k,v['pathlength'],v['sumhopspath']) for k,v in nodescorecounter.iteritems()]
    nodescorecounter.sort(key=lambda x: x[1], reverse=True)
    return json.dumps(nodescorecounter)

if __name__ == '__main__':
    http_server = WSGIServer(('', int(sys.argv[1])), app)
    http_server.serve_forever()
