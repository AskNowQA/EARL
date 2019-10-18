import numpy as np
import sys
import json
import urllib
from fuzzywuzzy import fuzz
from pybloom import ScalableBloomFilter
from elasticsearch import Elasticsearch
from SPARQLWrapper import SPARQLWrapper, JSON

#import pandas as pd
#import tensorflow as tf
#from util import make_w2v_embeddings
#from util import split_and_zero_padding
#from util import ManDist
#
class SiameseReranker:
    def __init__(self):
        print("SiameseReranker Initializing")
        #self.siamesemodel = tf.keras.models.load_model('../data/weights-improvement-24-0.54.hdf5', custom_objects={'ManDist': ManDist}) 
        self.es = Elasticsearch()
        self.wikiurilabeldict = json.loads(open('../data/wikiurilabeldict1.json').read())
        print("SiameseReranker Initialized")

    def sparqlQuery(self, query):
        sparql = SPARQLWrapper("http://localhost:8890/sparql")
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        return results

    def concatlabels(self, urls):
        concatlabels = []
        l = [] #list of lists, each list has labels. each list = 1 url
        for url in urls:
            if 'entity' in url:
                l.append(self.wikiurilabeldict[url])
            if 'resource' in url:
                eslabels = []
                print(url)
                res = self.es.search(index="wikidataentitylabelindex01", body={"query":{"term":{"uri":url}},"size":100})
                print(res)
                for idx,hit in enumerate(res['hits']['hits']):
                    eslabels.append(hit['_source']['wikidataLabel'])
                l.append(eslabels)
        print(urls)
        print(l) 
        return l

    def expandpath(self, connectednodes):
        candidatesubpathsandlabels = {}
        for bloomconnection in connectednodes['bloomconnections']:
            url1,url2 = bloomconnection['bloomstring'].split(':http')
            url2 = 'http'+url2
            if 'resource' in url1 and 'resource' in url2:
                query="SELECT DISTINCT ?p WHERE {<%s> ?p <%s>}"%(url1,url2)
                print(query)
                results = self.sparqlQuery(query)
                for result in results["results"]["bindings"]:
                    candidatesubpathsandlabels[url1+':'+result['p']["value"]+':'+url2] = self.concatlabels([url1,result['p']["value"],url2])
            else:
                candidatesubpathsandlabels[url1+':'+url2] = self.concatlabels([url1,url2])
        return None 

    def siamesereranker(self, entsrels):
        params = json.dumps(entsrels).encode('utf8')
        req = urllib.request.Request('http://localhost:8886/bloomconnections', data=params,
                             headers={'content-type': 'application/json'})
        response = urllib.request.urlopen(req).read()
        connectednodes = json.loads(response)
        labeldict = self.expandpath(connectednodes) 
        return connectednodes

if __name__=='__main__':
    d = json.loads(open('sample1.json').read())
    s = SiameseReranker()
    print(s.siamesereranker(d))

