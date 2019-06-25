#!/usr/bin/python

from __future__ import print_function
import sys,json,urllib, urllib2, requests
import requests

result = []
count = 0
f = open(sys.argv[1])
s = f.read()
d1 = json.loads(s)
f.close()
lcqgold = []
earltest = []

for item in d1: 
    itarr = []
    for ent in item['entity mapping']:
        itarr.append(ent['uri'])
    for pred in item['predicate mapping']:
        itarr.append(pred['uri'])
    lcqgold.append(itarr)

f = open(sys.argv[2])
s = f.read()
d2 = json.loads(s)
f.close()
#for items in d2:
#    itarr = []
#    for item in items:
#        for k,v in item['rerankedlists'].iteritems():
#            itarr.append(v[0][1])
#    earltest.append(itarr)

for items in d2:
    itarr = []
    bestsum = 0
    bestset = None
    for item in items:
        topsum = 0.0
        for k,v in item['rerankedlists'].iteritems():
            topsum += v[0][0]
        if len(item['rerankedlists']) == 0:
            continue
        topsum = topsum/float(len(item['rerankedlists']))
        if topsum > bestsum:
            bestsum = topsum
            bestset = item
    for k,v in bestset['rerankedlists'].iteritems():
        itarr.append(v[0][1])
    earltest.append(itarr)


correct = 0
wrong = 0
total = 0
tp = 0
fp = 0
fn = 0
for idx,arr in enumerate(lcqgold):
    #print(lcqgold[idx],earltest[idx])
    for uri in arr:
        if '/resource/' in uri:
        #if  '/ontology/' in uri:
            if uri in earltest[idx]:
                tp+=1
                correct += 1
            else:
                fn += 1
                print(earltest[idx],d2[idx][0]['chunktext'],lcqgold[idx],d1[idx])
                wrong += 1
            total += 1
for idx,arr in enumerate(earltest):
    for uri in arr:
        if '/resource/' in uri:
            if uri not in lcqgold[idx]:
                fp += 1

print(total)
print("Accuracy = ",correct/float(total))
precision = tp/float(tp+fp)
recall = tp/float(tp+fn)
f1 = 2*(precision*recall)/(precision+recall)
print("precision = ",precision)
print("recall = ",recall)
print("f1 = ",f1)

