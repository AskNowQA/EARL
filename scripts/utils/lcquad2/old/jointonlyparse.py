#!/usr/bin/python

from __future__ import print_function
import sys,json,urllib, urllib2, requests
import requests
from multiprocessing import Pool

def hiturl(questionserial):
    question = questionserial[0]
    serial = questionserial[1]
    req = urllib2.Request('http://localhost:4440/processQuery')
    req.add_header('Content-Type', 'application/json')
    inputjson = {'nlquery': question.lower()}
    try:
        response = urllib2.urlopen(req, json.dumps(inputjson))
        response = response.read()
        return (int(serial),response)
    except Exception,e:
        return(int(serial),'[]')

f = open('lcquad2.0.json')
s = f.read()
d = json.loads(s)
f.close()
questions = []

for item in d:
    questions.append((item['question'],item['uid']))

pool = Pool(9)
responses = pool.imap(hiturl,questions)

_results = []

count = 0
for response in responses:
    count += 1
    print(count)
    _results.append((response[0],json.loads(response[1])))

_results = sorted(_results, key=lambda tup: tup[0])

results = []
for result in _results:
    results.append(result[1])

 
f1 = open('jointonlyparse1.json','w')
print(json.dumps(results),file=f1)
f1.close()
