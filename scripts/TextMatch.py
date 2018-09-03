#!/usr/bin/python

import sys, urllib2,json

class TextMatch:
    def __init__(self):
        print "TextMatch initializing"
        print "TextMatch initialized"

    def textMatch(self, chunks, pagerankflag=False):
        req = urllib2.Request('http://localhost:8888/textMatch')
        req.add_header('Content-Type', 'application/json')
        inputjson = {'chunks': chunks, 'pagerankflag':pagerankflag}
        response = urllib2.urlopen(req, json.dumps(inputjson))
        response = json.loads(response.read()) 
        return response
                          
                     


if __name__ == '__main__':
    t = TextMatch()
    #print t.textMatch([{'chunk': 'Who', 'surfacelength': 3, 'class': 'entity', 'surfacestart': 0}, {'chunk': 'the parent organisation', 'surfacelength': 23, 'class': 'relation', 'surfacestart': 7}, {'chunk': 'Barack Obama', 'surfacelength': 12, 'class': 'entity', 'surfacestart': 34}, {'chunk': 'is', 'surfacelength': 2, 'class': 'relation', 'surfacestart': 4}])
    print t.textMatch([{"chunk": "friend", "surfacelength": 6, "class": "relation", "surfacestart": 0}])
