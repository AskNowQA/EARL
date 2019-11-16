#!/usr/bin/python

import sys, urllib2,json
from elasticsearch import Elasticsearch

class TextMatch:
    def __init__(self):
        print "TextMatch initializing"
        self.wikiurilabeldict = json.loads(open('../data/wikiurilabeldict1.json').read())
        self.es = Elasticsearch()
        print "TextMatch initialzed"

    def textMatch(self, chunks, pagerankflag=False):
        req = urllib2.Request('http://localhost:8887/textMatch')
        req.add_header('Content-Type', 'application/json')
        inputjson = {'chunks': chunks, 'pagerankflag':pagerankflag}
        response = urllib2.urlopen(req, json.dumps(inputjson))
        response = json.loads(response.read())
        return response
 
    def getLabels(self, answers):
        for answer in answers:
            for url in answer['topkmatches']:
                if '_' in url:
                    url1,url2 = url.split('_')
                    if 'P' in url1 and 'P' in url2:
                        print(url, self.wikiurilabeldict['http://www.wikidata.org/entity/'+url][0])
                    elif 'P' in url1 and 'Q' in url2:
                        res = self.es.search(index="wikidataentitylabelindex01", body={"query":{"term":{"uri":{"value":"http://wikidata.dbpedia.org/resource/"+url2}}},"size":1})
                        print(url1+'_'+url2,self.wikiurilabeldict['http://www.wikidata.org/entity/'+url1][0],res['hits']['hits'][0]['_source']['wikidataLabel'])
                elif 'P' in url:
                    print(url, self.wikiurilabeldict['http://www.wikidata.org/entity/'+url][0])
                          


if __name__ == '__main__':
    t = TextMatch()
    print(json.dumps(t.textMatch([{'chunk': 'Who', 'surfacelength': 3, 'class': 'entity', 'surfacestart': 0}, {'chunk': 'the parent organisation', 'surfacelength': 23, 'class': 'relation', 'surfacestart': 7}, {'chunk': 'Barack Obama', 'surfacelength': 12, 'class': 'entity', 'surfacestart': 34}, {'chunk': 'is', 'surfacelength': 2, 'class': 'relation', 'surfacestart': 4}])))
#    print t.textMatch([{"chunk": "friend", "surfacelength": 6, "class": "relation", "surfacestart": 0}])
#    print(t.getLabels(t.textMatch([{"chunk": "company developed", "surfacelength": 6, "class": "relation", "surfacestart": 0}])))
#    print t.textMatch([{"chunk": "Russia", "surfacelength": 6, "class": "entity", "surfacestart": 0}])
