#!/usr/bin/python

from __future__ import print_function
import sys,json,urllib, urllib2, requests
import requests
from elasticsearch import Elasticsearch

es = Elasticsearch()

f = open(sys.argv[1])
s = f.read()
d = json.loads(s)
f.close()
count = 0
for item in d: 
    question = item['question']
    res = es.index(index="autocompleteindex1", doc_type='questions',  body={"question":{"input":[question]}})
    count += 1
    print(count)
    print(res)

