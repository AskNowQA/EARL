#!/usr/bin/python

from __future__ import print_function
import sys,json,urllib, urllib2, requests
import requests,re
from multiprocessing import Pool

def hiturl(questionserial):
    question = questionserial[0]
    print(question)
    serial = questionserial[1]
    if not question:
        print('question none')
        return(int(serial), '[]')
    if len(question) > 1000:
        print('too long')
        return(int(serial), '[]')
    try:
        req = urllib2.Request('http://localhost:4440/processQuery')
        req.add_header('Content-Type', 'application/json')
        question = re.sub('[^0-9a-zA-Z]+', ' ', question)
        inputjson = {'nlquery': question.lower()}
        response = urllib2.urlopen(req, json.dumps(inputjson))
        response = response.read()
        return (int(serial),response)
    except Exception,e:
        print('damn')
        return(int(serial),'[]')

f = open('/data/home/sda-srv05/debayan/LC-QuAD2.0/dataset/train.json')
s = f.read()
d = json.loads(s)
f.close()
questions = []

for item in d:
    questions.append((item['question'],item['uid']))

pool = Pool(10)

responses = pool.imap(hiturl,questions)

_results = []

count = 0
for response in responses:
    count += 1
    print(count)
    _results.append((response[0],json.loads(response[1])))

#_results = sorted(_results, key=lambda tup: tup[0])

#results = []
#for result in _results:
#    results.append(result[1])

 
f1 = open('ngramtesttilerelations1.json','w')
print(json.dumps(_results, indent=4, sort_keys=True),file=f1)
f1.close()
