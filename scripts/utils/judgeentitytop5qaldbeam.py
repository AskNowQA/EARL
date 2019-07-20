#!/usr/bin/python

from __future__ import print_function
import sys,json,urllib, urllib2, requests
import requests,re
import numpy as np
from pybloom import BloomFilter
reload(sys)
sys.setdefaultencoding('utf8')


f = open('../../data/blooms/bloom1hoppredicate.pickle')
bloom1hoppred = BloomFilter.fromfile(f)
f.close()
f = open('../../data/blooms/bloom1hopentity.pickle')
bloom1hopentity = BloomFilter.fromfile(f)
f.close()
f = open('../../data/blooms/bloom2hoppredicate.pickle')
bloom2hoppredicate = BloomFilter.fromfile(f)
f.close()
f = open('../../data/blooms/bloom2hoptypeofentity.pickle')
bloom2hoptypeofentity = BloomFilter.fromfile(f)
f.close()


def beam_search_decoder(data, k):
    sequences = [[list(), 1.0]]
    # walk over each step in sequence
    for row in data:
        all_candidates = list()
        # expand each current candidate
        for i in range(len(sequences)):
            seq, score = sequences[i]
            for j in range(len(row)):
                candidate = [seq + [j], score * row[j]]
                all_candidates.append(candidate)
        # order all candidates by score
        ordered = sorted(all_candidates, key=lambda tup:tup[1],reverse=True)
        # select k best
        sequences = ordered[:k]
    return sequences


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
    globallowesthopcount = 99
    globalbesturiseq = []
    globalbestseq = []
    for item in items:  
        if len(item['chunktext']) <= 1:
            continue
        maxlistlen = 0
        for k,v in item['rerankedlists'].iteritems():
            if len(v) > maxlistlen:
                maxlistlen = len(v)
        beamarrayinputscores = []
        beamuris = []
        for k,v in item['rerankedlists'].iteritems():
            scores = []
            uris = []
            for element in v:
                scores.append(element[0])
                uris.append(element[1][0])
            diff = maxlistlen - len(scores)
            scores += diff * [0.0]
            uris += ["" for x in range(diff)]
            beamarrayinputscores.append(scores)
            beamuris.append(uris)
        bainp = np.asarray(beamarrayinputscores,dtype=np.float32)
        sequences = beam_search_decoder(bainp,10)
        lowesthopcount = 99
        bestsequence = []
        besturisequence = []
        for sequence in sequences:
            row = 0
            uriseq = []
            for col in sequence[0]:
                #print(beamuris,row,col,sequence)
                uriseq.append(beamuris[row][col])
                row += 1
            uripairs = [((i), (i + 1) % len(uriseq))  for i in range(len(uriseq))]
            hopcount = 0
            for uripair in uripairs:
                bloomstring = uriseq[0]+':'+uriseq[1]
                if bloomstring in bloom1hoppred:
                    hopcount += 0.5
                elif bloomstring in bloom1hopentity:
                    hopcount += 1
                elif bloomstring in bloom2hoppredicate:
                    hopcount += 1.5
                elif bloomstring in bloom2hoptypeofentity:
                    hopcount += 2
                else:
                    hopcount += 3 #not connected
            if hopcount < lowesthopcount:
                lowesthopcount = hopcount
                besturisequence = uriseq
                bestsequence = sequence
        if (lowesthopcount < globallowesthopcount):
            globallowesthopcount = lowesthopcount
            globalbesturiseq = besturisequence
            globalbestseq = bestsequence
    print(globallowesthopcount, globalbestseq, globalbesturiseq)
    earltest.append(globalbesturiseq)
print(len(earltest))
#        itarr.append(v[0][1])

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
