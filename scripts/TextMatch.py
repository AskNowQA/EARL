#!/usr/bin/python

import sys, urllib2,json
from fuzzywuzzy import fuzz
from elasticsearch import Elasticsearch

class TextMatch:
    def __init__(self):
        print "TextMatch initializing"
        self.es = Elasticsearch()
        print "TextMatch initialized"

    def textMatch(self, chunks, nlquery, pagerankflag=False):
        req = urllib2.Request('http://localhost:8887/textMatch')
        req.add_header('Content-Type', 'application/json')
        relationchunks = []
        entitychunks = []
        matchedchunks = []
        for chunk in chunks:
            if chunk['class'] == 'entity':
                entitychunks.append(chunk)
            else:
                relationchunks.append(chunk)
        inputjson = {'chunks': relationchunks, 'pagerankflag':pagerankflag}
        response = urllib2.urlopen(req, json.dumps(inputjson))
        matchedchunks = json.loads(response.read())
        
        for chunk in entitychunks:
            res = self.es.search(index="dbentityindex11", doc_type="records", body={"query":{"multi_match":{"query":chunk['chunk'],"fields":["wikidataLabel", "dbpediaLabel^1.5"]}},"size":200})
            _topkents = []
            topkents = []
            for record in res['hits']['hits']:
                if 'dbpediaLabel' in record['_source']:
                    _topkents.append((record['_source']['uri'],record['_source']['edgecount'],fuzz.ratio(nlquery,record['_source']['dbpediaLabel']),fuzz.partial_ratio(nlquery,record['_source']['dbpediaLabel']),fuzz.token_sort_ratio(nlquery,record['_source']['dbpediaLabel']),fuzz.token_set_ratio(nlquery,record['_source']['dbpediaLabel'])))
                if 'wikidataLabel' in record['_source']:
                    _topkents.append((record['_source']['uri'],record['_source']['edgecount'],fuzz.ratio(nlquery,record['_source']['wikidataLabel']),fuzz.partial_ratio(nlquery,record['_source']['wikidataLabel']),fuzz.token_sort_ratio(nlquery,record['_source']['wikidataLabel']),fuzz.token_set_ratio(nlquery,record['_source']['wikidataLabel'])))
            _topkents =  sorted(_topkents, key=lambda k: k[3], reverse=True)
            #if pagerankflag:
            #    _topkents =  sorted(_topkents, key=lambda k: k[1], reverse=True)
            for record in _topkents:
                if len(topkents) >= 30:
                    break
                if record in topkents:
                    continue
                else:
                    topkents.append(record)
            matchedchunks.append({'chunk':chunk, 'topkmatches': topkents, 'class': 'entity'})
        return matchedchunks


if __name__ == '__main__':
    t = TextMatch()
    print t.textMatch([{'chunk': 'Who', 'surfacelength': 3, 'class': 'entity', 'surfacestart': 0}, {'chunk': 'the parent organisation', 'surfacelength': 23, 'class': 'relation', 'surfacestart': 7}, {'chunk': 'Barack Obama', 'surfacelength': 12, 'class': 'entity', 'surfacestart': 34}, {'chunk': 'is', 'surfacelength': 2, 'class': 'relation', 'surfacestart': 4}],"who is the president")
    #print t.textMatch([{"chunk": "friend", "surfacelength": 6, "class": "relation", "surfacestart": 0}])
