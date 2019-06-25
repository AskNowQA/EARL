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
    response = urllib2.urlopen(req, json.dumps(inputjson))
    response = response.read()
    return (int(serial),response)

f = open(sys.argv[1])
s = f.read()
d = json.loads(s)
f.close()
questions = []

for item in d['questions']:
    #questions.append((item['question'],item['SerialNumber']))
    for q in item['question']:
        if q['language'] == 'en':
            questions.append((q['string'],item['id']))

pool = Pool(8)
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

 
f1 = open('outputerspanlowerfullqald.json','w')
print(json.dumps(results),file=f1)
f1.close()
