#!/usr/bin/python

from annoy import AnnoyIndex
from elasticsearch import Elasticsearch
import gensim
import urllib2
import numpy as np
import json,sys
import random


es = Elasticsearch()
d = json.loads(open('../../data/wikiurilabeldict1.json').read())
def getLabel(result):
    labels = []
    for url in result:
        if 'Q' in url:
            res = es.search(index="wikidataentitylabelindex01", body={"query":{"term":{"uri": 'http://wikidata.dbpedia.org/resource/'+url[4:]}},"size":100})
            labels.append( [rec['_source']['wikidataLabel'] for rec in res['hits']['hits']])
        else:
            labels.append(d['http://www.wikidata.org/entity/'+url])
    return labels


t = AnnoyIndex(300, 'angular')
t.load('predtype1.ann')
d1 = json.loads(open('predtypeurls1.json').read())
queries = ["father","president"]

for query in queries:
    req = urllib2.Request('http://localhost:8887/ftwv')
    req.add_header('Content-Type', 'application/json')
    inputjson = {'chunks':[query]}
    response = urllib2.urlopen(req, json.dumps(inputjson))
    embedding = json.loads(response.read().decode('utf8'))[0]
    #print(embedding)
    results= t.get_nns_by_vector(embedding,10)
    #print(t.get_item_vector(results[0]))
    cosinedistance = 1 - np.dot(embedding, t.get_item_vector(results[0])) / (np.linalg.norm(embedding) * np.linalg.norm(t.get_item_vector(results[0])))
    print(query, cosinedistance)
    for result in results:
        print(d1[str(result)],getLabel(d1[str(result)]))
