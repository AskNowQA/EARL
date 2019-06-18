#!/usr/bin/python

from __future__ import print_function
import sys,json,urllib, urllib2, requests
import requests
from multiprocessing import Pool

def hiturl(question):
    serialnum = question[1]
    question = question[0]
    req = urllib2.Request('http://localhost:4440/processQuery')
    req.add_header('Content-Type', 'application/json')
    inputjson = {'nlquery': question}
    response = urllib2.urlopen(req, json.dumps(inputjson))
    responsestring = response.read()
    if responsestring is None:
        return (int(serialnum),'{}')
    else:
        return (int(serialnum),responsestring)


count = 0
f = open(sys.argv[1])
s = f.read()
d = json.loads(s)
f.close()
questions = []

for item in d:
    questions.append((item['question'],item['SerialNumber']))

pool = Pool(8)
responses = pool.map(hiturl,questions)

responses = sorted(responses, key=lambda tup: tup[0])

results = []

for response in responses:
    results.append(json.loads(response[1]))
 
f1 = open('outputerspanupperfulllcquad.json','w')
print(json.dumps(results),file=f1)
f1.close()

