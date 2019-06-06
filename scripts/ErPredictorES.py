#!/usr/bin/python

import numpy as np
import re
import urllib2
import gzip
from elasticsearch import Elasticsearch
import torch
import torch.nn as nn
import torch.utils.data as utils
import sys,json,string
from fuzzywuzzy import fuzz

class ErPredictorES:
    def __init__(self):
        print "Er Predictor ES Initializing"
        self.es  = Elasticsearch()
        n_in, n_h, n_out = 304, 200, 2
        self.ermodel = nn.Sequential(nn.Linear(n_in, n_h),
                 nn.ReLU(),
                 nn.Linear(n_h, n_h),
                 nn.ReLU(),
                 nn.Linear(n_h,n_out),
                 nn.Softmax())
        self.ermodel.load_state_dict(torch.load('../data/er.model',map_location='cpu'))
        self.ermodel.eval()
        print "Er Predictor Initialized"

    def embed(self, words):
        req = urllib2.Request('http://localhost:8887/ftwv')
        req.add_header('Content-Type', 'application/json')
        inputjson = {'chunk': words}
        response = urllib2.urlopen(req, json.dumps(inputjson))
        response = json.loads(response.read())
        return response

    def erPredict(self, chunks):
        erpredictions = []
        combinedchunks = []
        for chunk in chunks:
            wordlist = []
            surfacestart = chunk[0][2]
            for word in chunk:
                wordlist.append(word[0])
                surfacelength = word[2]+word[3] - surfacestart
            wordlist = ' '.join(wordlist)
            combinedchunks.append((wordlist,surfacestart,surfacelength))
         
        for chunk in combinedchunks:
            x = None
            chunkk = chunk[0].encode('ascii','ignore')
            chunkwords = chunkk.translate(None, string.punctuation)
            embedding = self.embed(chunkwords)
            esresult = self.es.search(index="dbentityindex11", body={"query":{"multi_match":{"query":chunkwords,"fields":["wikidataLabel", "dbpediaLabel^1.5"]}},"size":1})
            topresult = esresult['hits']['hits']
            if len(topresult) == 1:
                topresult = topresult[0]
                if 'dbpediaLabel' in topresult['_source']:
                    x = embedding + [topresult['_score']] + [fuzz.ratio(chunkwords, topresult['_source']['dbpediaLabel'])/100.0] + [fuzz.partial_ratio(chunkwords, topresult['_source']['dbpediaLabel'])/100.0] + [fuzz.token_sort_ratio(chunkwords, topresult['_source']['dbpediaLabel'])/100.0]
                if 'wikidataLabel' in topresult['_source']:
                    x = embedding + [topresult['_score']] + [fuzz.ratio(chunkwords, topresult['_source']['wikidataLabel'])/100.0] + [fuzz.partial_ratio(chunkwords, topresult['_source']['wikidataLabel'])/100.0] + [fuzz.token_sort_ratio(chunkwords, topresult['_source']['wikidataLabel'])/100.0]
            else:
                x = embedding + [0.0,0.0,0.0,0.0]
        #print(x, type(x))
            x = torch.FloatTensor(x)  
            pred = self.ermodel(x)
            print(chunkwords,pred,pred[0])
            if pred[0] >0.5:
                erpredictions.append({'chunk':chunkwords, 'surfacestart': chunk[1], 'surfacelength': chunk[2] , 'class':'entity'})
            else:
                erpredictions.append({'chunk':chunkwords, 'surfacestart': chunk[1], 'surfacelength': chunk[2] , 'class':'relation'})
        return erpredictions

if __name__=='__main__':
    e = ErPredictorES()
    #print e.erPredict(['There', 'people', 'world', 'better', 'place', 'me.'])
    print e.erPredict([[['Who', 'S-NP', 0, 3]], [['the', 'B-NP', 7, 3], ['parent', 'I-NP', 11, 6], ['organisation', 'E-NP', 18, 12]], [['Barack', 'B-NP', 34, 6], ['Obama', 'E-NP', 41, 5]], [['is', 'S-VP', 4, 2]]])
    print e.erPredict([[['Who', 'S-NP', 0, 3]], [['the', 'B-NP', 7, 3], ['parent', 'I-NP', 11, 6], ['organisation', 'E-NP', 18, 12]], [['barack', 'B-NP', 34, 6], ['obama', 'E-NP', 41, 5]], [['is', 'S-VP', 4, 2]]])

