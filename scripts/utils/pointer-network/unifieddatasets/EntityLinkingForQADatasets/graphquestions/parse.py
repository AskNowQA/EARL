#!/usr/bin/python

from __future__ import print_function
import sys,json,urllib, urllib2, requests
import requests,re
from multiprocessing import Pool

def hiturl(questionserial):
    question = questionserial[0]
    qid = questionserial[1]
    req = urllib2.Request('http://localhost:4440/processQuery')
    req.add_header('Content-Type', 'application/json')
    try:
        print(question)
        question = re.sub(r"[^a-zA-Z0-9]+", ' ', question)
        print(question)
        inputjson = {'nlquery': question}
        response = urllib2.urlopen(req, json.dumps(inputjson))
        response = response.read()
        return (qid,response)
    except Exception,e:
        return(qid,'[]')

d = json.loads(open('input/graph.test.entities.json').read())
count = 0
questions = []
for item in d:
    q = item['utterance']
    questions.append((q,item['question_id']))
    count += 1

pool = Pool(8)
responses = pool.imap(hiturl,questions)

_results = []

count = 0
totalentchunks = 0
tpentity = 0
fpentity = 0
fnentity = 0
for response in responses:
    count += 1
    print(count)
    _results.append((response[0],json.loads(response[1])))

results = []
for result in _results:
    results.append(result)

 
f1 = open('gqsout.json','w')
print(json.dumps(results),file=f1)
f1.close()
