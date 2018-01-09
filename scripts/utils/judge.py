#!/usr/bin/python

from __future__ import print_function
import sys,json,urllib, urllib2, requests
import requests

result = []
count = 0
f = open(sys.argv[1])
s = f.read()
d = json.loads(s)
f.close()
lcqgold = []
earltest = []

for item in d: 
    itarr = []
    for ent in item['entity mapping']:
        itarr.append(ent['uri'])
    for pred in item['predicate mapping']:
        itarr.append(pred['uri'])
    lcqgold.append(itarr)

f = open(sys.argv[2])
s = f.read()
d = json.loads(s)
f.close()
for item in d:
    itarr = []
    for ent in item['entities']:
         for uri in ent['uris']:
             itarr.append(uri['uri'])
             break
    for rel in item['relations']:
         for uri in rel['uris']:
             itarr.append(uri['uri'])
             break
    earltest.append(itarr)

correct = 0
wrong = 0
total = 0
for idx,arr in enumerate(lcqgold):
    print(lcqgold[idx],earltest[idx])
    for uri in arr:
        if '/resource/' in uri:
            if uri in earltest[idx]:
                correct += 1
            else:
                wrong += 1
            total += 1

print(correct/float(total))

