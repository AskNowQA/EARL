#!/usr/bin/python

from __future__ import print_function
import sys,json,urllib, urllib2, requests
import requests

f1 = open('outputerspanlower.json','w')

result = []
count = 0
f = open(sys.argv[1])
s = f.read()
d = json.loads(s)
f.close()
for item in d: 
    req = urllib2.Request('http://localhost:4445/processQuery')
    req.add_header('Content-Type', 'application/json')
    inputjson = {'nlquery': item['question'].lower()}
    response = urllib2.urlopen(req, json.dumps(inputjson))
    response = json.loads(response.read())
    #j = json.dumps(response, indent=4)
    print(count, len(d))
    result.append(response)
    count += 1
print(json.dumps(result),file=f1)
f1.close()

