#!/usr/bin/python

from __future__ import print_function
import sys,json,urllib, urllib2, requests
import requests,re
reload(sys)
sys.setdefaultencoding('utf8')
result = []
count = 0
f = open(sys.argv[1])
s = f.read()
d1 = json.loads(s)
f.close()
lcqgold = []
earltest = []
qaldquestions = []
for item in d1['questions']:
    for q in item['question']:
        if q['language'] == 'en':
            qaldquestions.append(q['string'])
    sparql = item['query']['sparql']
    resources = re.findall('res:([^\s].*) ', sparql, re.IGNORECASE)
    itarr = []
    for resource in resources:
        itarr.append('http://dbpedia.org/resource/'+resource.split(' ')[0])
    entities = re.findall('<http://dbpedia.org/resource/([^\s].*)>', sparql, re.IGNORECASE)
    for entity in entities:
        itarr.append('http://dbpedia.org/resource/'+entity.split('>')[0])
    lcqgold.append(itarr)
f = open(sys.argv[2])
s = f.read()
d2 = json.loads(s)
f.close()
#for items in d2:
#    itarr = []
#    for item in items:
#        for k,v in item['rerankedlists'].iteritems():
#            if '/resource/' in v[0][1]:
#                itarr.append(v[0][1])
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
chunkingerror = 0
for idx,arr in enumerate(lcqgold):
    #print(lcqgold[idx],earltest[idx])
    for uri in arr:
        if '/resource/' in uri:
        #if  '/ontology/' in uri:
            if uri in earltest[idx]:
                tp+=1
                correct += 1
                print('correct')
            else:
                fn += 1
                wrong += 1
                print('wrong')
            reschunks = []
            for chunktext in d2[idx][0]['chunktext']:
                if chunktext['class'] == 'entity':
                    reschunks.append(chunktext['chunk'])
#            lcqchunks = []
#            for ent in d1[idx]['entity mapping']:
#                lcqchunks.append(ent['label'])
#            for lcqchunk in lcqchunks:
#                corr = False
#                for reschunk in reschunks:
#                    if reschunk.lower() == lcqchunk.lower():
#                        corr = True
#                if corr is not True:
#                    chunkingerror += 1
#                     
            print(qaldquestions[idx],'-',reschunks,'-',earltest[idx],'-', lcqgold[idx])
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
print("total = ",total)
print("chunking error = ",chunkingerror)
