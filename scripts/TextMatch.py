#!/usr/bin/python

import sys,json
from urllib.request import urlopen
from urllib.request import Request
from urllib.parse import urlencode

class TextMatch:
    def __init__(self):
        print("TextMatch initializing")
        print("TextMatch initialized")

    def textMatch(self, chunks, pagerankflag=False):
        req = Request('http://localhost:8888/textMatch')
        req.add_header('Content-Type', 'application/json')
        body = {'chunks': chunks, 'pagerankflag':pagerankflag}
        jsondata = json.dumps(body)
        jsondataasbytes = jsondata.encode("utf-8")
        req.add_header('Content-Length', len(jsondataasbytes))
        response = urlopen(req, jsondataasbytes)
        response = json.loads(response.read()) 
        return response
                          
                     


if __name__ == '__main__':
    t = TextMatch()
    #print t.textMatch([{'chunk': 'Who', 'surfacelength': 3, 'class': 'entity', 'surfacestart': 0}, {'chunk': 'the parent organisation', 'surfacelength': 23, 'class': 'relation', 'surfacestart': 7}, {'chunk': 'Barack Obama', 'surfacelength': 12, 'class': 'entity', 'surfacestart': 34}, {'chunk': 'is', 'surfacelength': 2, 'class': 'relation', 'surfacestart': 4}])
    print(t.textMatch([{"chunk": "friend", "surfacelength": 6, "class": "relation", "surfacestart": 0}]))
