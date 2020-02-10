import sys
import json
import re
import requests
from elasticsearch import Elasticsearch
import numpy as np


class Vectoriser():
    def __init__(self):
       print("Initialising Vectoriser")
       self.es = Elasticsearch()
       print("Initialised Vectoriser")
   
    def getembedding(self, enturl):
        entityurl = '<http://www.wikidata.org/entity/'+enturl[37:]+'>'
        res = self.es.search(index="wikidataembedsindex01", body={"query":{"term":{"key":{"value":entityurl}}}})
        try:
            embedding = [float(x) for x in res['hits']['hits'][0]['_source']['embedding']]
            return embedding
        except Exception as e:
            print(enturl,' not found')
            return None
        return None

    def vectorise(self,nlquery):
        if not nlquery:
            return []
        q = re.sub("\s*\?", "", nlquery.strip())
        candidatevectors = []
        #questionembedding
        tokens = [token for token in q.split(" ") if token != ""]
        r = requests.post("http://localhost:8887/ftwv",json={'chunks': tokens})
        questionembeddings = r.json()
        questionembedding = list(map(lambda x: sum(x)/len(x), zip(*questionembeddings))) 
        true = []
        false = []
        for idx,token in enumerate(tokens):
            #n
            tokenembedding = questionembeddings[idx]
            esresult = self.es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":tokens[idx]}},"size":30})
            esresults = esresult['hits']['hits']
            if len(esresults) > 0:
                for entidx,esresult in enumerate(esresults):
                    entityembedding = self.getembedding(esresult['_source']['uri'])
                    if entityembedding and questionembedding and tokenembedding :
                        candidatevectors.append([entityembedding+questionembedding+tokenembedding+[entidx,idx,1],esresult['_source']['uri'][37:],esresult['_source']['wikidataLabel'],tokens[idx]])
            #n-1,n
            if idx > 0:
                 word = tokens[idx-1]+' '+tokens[idx]
                 esresult = self.es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word}},"size":30})
                 esresults = esresult['hits']['hits']
                 if len(esresults) > 0:
                     for entidx,esresult in enumerate(esresults):
                         entityembedding = self.getembedding(esresult['_source']['uri'])
                         if entityembedding and questionembedding and tokenembedding:
                             candidatevectors.append([entityembedding+questionembedding+tokenembedding+[entidx,idx,-2],esresult['_source']['uri'][37:],esresult['_source']['wikidataLabel'],word])
            #n,n+1
            if idx < len(tokens) - 1:
                word = tokens[idx]+' '+tokens[idx+1]
                esresult = self.es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word}},"size":30})
                esresults = esresult['hits']['hits']
                if len(esresults) > 0:
                    for entidx,esresult in enumerate(esresults):
                        entityembedding = self.getembedding(esresult['_source']['uri'])
                        if entityembedding and questionembedding and tokenembedding:
                            candidatevectors.append([entityembedding+questionembedding+tokenembedding+[entidx,idx,2],esresult['_source']['uri'][37:],esresult['_source']['wikidataLabel'],word])
    
            #n-1,n,n+1
            if idx < len(tokens) - 1 and idx > 0:
                word = tokens[idx-1]+' '+tokens[idx]+' '+tokens[idx+1]
                esresult = self.es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word}},"size":30})
                esresults = esresult['hits']['hits']
                if len(esresults) > 0:
                    for entidx,esresult in enumerate(esresults):
                        entityembedding = self.getembedding(esresult['_source']['uri'])
                        if entityembedding and questionembedding :
                            candidatevectors.append([entityembedding+questionembedding+tokenembedding+[entidx,idx,3],esresult['_source']['uri'][37:],esresult['_source']['wikidataLabel'],word])
        return candidatevectors

if __name__ == '__main__':
    v = Vectoriser()
    print(v.vectorise("who is the president of India ?"))

