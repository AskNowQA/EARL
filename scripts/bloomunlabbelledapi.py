#!/usr/bin/python

from flask import request
from flask import Flask
import json,sys
import itertools
from operator import itemgetter
from pybloom import BloomFilter

f = open('../data/blooms/bloom1hoppredicate.pickle')
bloom1hoppred = BloomFilter.fromfile(f)
f.close()

f = open('../data/blooms/bloom1hopentity.pickle')
bloom1hopentity = BloomFilter.fromfile(f)
f.close()

f = open('../data/blooms/bloom2hoppredicate.pickle')
bloom2hoppredicate = BloomFilter.fromfile(f)
f.close()

f = open('../data/blooms/bloom2hoptypeofentity.pickle')
bloom2hoptypeofentity = BloomFilter.fromfile(f)
f.close()


reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)

@app.route('/findBloomPaths', methods=['POST'])
def findBloomPaths():
    d = request.get_json(silent=True)
    es_content = d['ES_content']
    lists = []
    count = 1
    for listitem in es_content:
        lists.append(listitem['list'+str(count)])
        count += 1
    sequence = range(len(lists))
    result = []
    nodestats = {}
    for listt in lists:
        for uriset in listt:
            uri1 = uriset['uri']
            if uri1 not in nodestats:
                nodestats[uri1] = {'connections':0, 'sumofhops':0, 'elasticsearchscore': uriset['score']}
    for perm in itertools.permutations(sequence, 2):
        for uriset1 in lists[perm[0]]:
            for uriset2 in lists[perm[1]]:
                uri1 = uriset1['uri']
                uri2 = uriset2['uri']
                s = uri1+':'+uri2
                if s in bloom1hoppred:
                    result.append('%s has 1 hop entity:predicate connection in knowledgebase'%s)
                    if uri1 not in nodestats:
                        nodestats[uri1] = {'connections':0, 'sumofhops':0,   'elasticsearchscore': uriset1['score']}
                    nodestats[uri1]['connections'] += 1
                    nodestats[uri1]['sumofhops'] += 0.5
                    if uri2 not in nodestats:
                        nodestats[uri2] = {'connections':0, 'sumofhops':0,   'elasticsearchscore': uriset2['score']}
                    nodestats[uri2]['connections'] += 1
                    nodestats[uri2]['sumofhops'] += 0.5
                elif s in bloom1hopentity:
                    result.append('%s has 1 hop entity:entity connection in knowledgebase'%s)
                    if uri1 not in nodestats:
                        nodestats[uri1] = {'connections':0, 'sumofhops':0,  'elasticsearchscore': uriset1['score']}
                    nodestats[uri1]['connections'] += 1
                    nodestats[uri1]['sumofhops'] += 1
                    if uri2 not in nodestats:
                        nodestats[uri2] = {'connections':0, 'sumofhops':0,  'elasticsearchscore': uriset2['score']}
                    nodestats[uri2]['connections'] += 1
                    nodestats[uri2]['sumofhops'] += 1
                elif s in bloom2hoppredicate:
                    result.append('%s has 2 hop entity:predicate connection in knowledgebase'%s)
                    if uri1 not in nodestats:
                        nodestats[uri1] = {'connections':0, 'sumofhops':0,  'elasticsearchscore': uriset1['score']}
                    nodestats[uri1]['connections'] += 1
                    nodestats[uri1]['sumofhops'] += 1.5
                    if uri2 not in nodestats:
                        nodestats[uri2] = {'connections':0, 'sumofhops':0,  'elasticsearchscore': uriset2['score']}
                    nodestats[uri2]['connections'] += 1
                    nodestats[uri2]['sumofhops'] += 1.5
                elif s in bloom2hoptypeofentity:
                    result.append('%s has 2 hop entity:typeof connection in knowledgebase'%s)
                    if uri1 not in nodestats:
                        nodestats[uri1] = {'connections':0, 'sumofhops':0, 'elasticsearchscore': uriset1['score']}
                    nodestats[uri1]['connections'] += 1
                    nodestats[uri1]['sumofhops'] += 2
                    if uri2 not in nodestats:
                        nodestats[uri2] = {'connections':0, 'sumofhops':0, 'elasticsearchscore': uriset2['score']}
                    nodestats[uri2]['connections'] += 1
                    nodestats[uri2]['sumofhops'] += 2
                else:
                    if uri1 not in nodestats:
                        nodestats[uri1] = {'connections':0, 'sumofhops':0,  'elasticsearchscore': uriset1['score']}
                    if uri2 not in nodestats:
                        nodestats[uri2] = {'connections':0, 'sumofhops':0,  'elasticsearchscore': uriset2['score']}
   
    finalresult = {'humanresults': result, 'nodestats': nodestats }
    return json.dumps(finalresult)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005,debug=True)
