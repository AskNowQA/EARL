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

    def getdescriptionsembedding(self, entid):
        res = self.es.search(index="wikidataentitydescriptionsindex01", body={"query":{"term":{"entityid.keyword":entid}}})
        try:
            description = res['hits']['hits'][0]['_source']['description']
            req = urllib2.Request('http://localhost:8887/ftwv')
            req.add_header('Content-Type', 'application/json')
            inputjson = {'chunks':[description]}
            response = urllib2.urlopen(req, json.dumps(inputjson))
            descembedding = json.loads(response.read().decode('utf8'))[0]
            return descembedding
        except Exception as e:
            #print("getdescriptionsembedding err: ",e)
            return [0]*300
        return [0]*300
     
    def getlabelembedding(self,label):
        try:
            req = urllib2.Request('http://localhost:8887/ftwv')
            req.add_header('Content-Type', 'application/json')
            inputjson = {'chunks':[label]}
            response = urllib2.urlopen(req, json.dumps(inputjson))
            labelembedding = json.loads(response.read().decode('utf8'))[0]
            return labelembedding
        except Exception as e:
            #print("getdescriptionsembedding err: ",e)
            return [0]*300
        return [0]*300

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
                    descembedding = self.getdescriptionsembedding(esresult['_source']['uri'][37:])
                    labelembedding = self.getlabelembedding(esresult['_source']['wikidataLabel'])
                    candidatevectors.append([questionembedding+tokenembedding+descembedding+labelembedding+entityembedding+[entidx,idx,1],esresult['_source']['uri'][37:],esresult['_source']['wikidataLabel'],tokens[idx], [idx,idx]])
            #n-1,n
            if idx > 0:
                 word = tokens[idx-1]+' '+tokens[idx]
                 esresult = self.es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word}},"size":30})
                 esresults = esresult['hits']['hits']
                 if len(esresults) > 0:
                     for entidx,esresult in enumerate(esresults):
                         entityembedding = self.getembedding(esresult['_source']['uri'])
                         descembedding = self.getdescriptionsembedding(esresult['_source']['uri'][37:])
                         labelembedding = self.getlabelembedding(esresult['_source']['wikidataLabel'])
                         candidatevectors.append([questionembedding+tokenembedding+descembedding+labelembedding+entityembedding+[entidx,idx,1],esresult['_source']['uri'][37:],esresult['_source']['wikidataLabel'],word, [idx-1,idx]])
            #n,n+1
            if idx < len(tokens) - 1:
                word = tokens[idx]+' '+tokens[idx+1]
                esresult = self.es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word}},"size":30})
                esresults = esresult['hits']['hits']
                if len(esresults) > 0:
                    for entidx,esresult in enumerate(esresults):
                        entityembedding = self.getembedding(esresult['_source']['uri'])
                        descembedding = self.getdescriptionsembedding(esresult['_source']['uri'][37:])
                        labelembedding = self.getlabelembedding(esresult['_source']['wikidataLabel'])
                        candidatevectors.append([questionembedding+tokenembedding+descembedding+labelembedding+entityembedding+[entidx,idx,1],esresult['_source']['uri'][37:],esresult['_source']['wikidataLabel'],word, [idx,idx+1]])
    
            #n-1,n,n+1
            if idx < len(tokens) - 1 and idx > 0:
                word = tokens[idx-1]+' '+tokens[idx]+' '+tokens[idx+1]
                esresult = self.es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word}},"size":30})
                esresults = esresult['hits']['hits']
                if len(esresults) > 0:
                    for entidx,esresult in enumerate(esresults):
                        entityembedding = self.getembedding(esresult['_source']['uri'])
                        descembedding = self.getdescriptionsembedding(esresult['_source']['uri'][37:])
                        labelembedding = self.getlabelembedding(esresult['_source']['wikidataLabel'])
                        candidatevectors.append([questionembedding+tokenembedding+descembedding+labelembedding+entityembedding+[entidx,idx,1],esresult['_source']['uri'][37:],esresult['_source']['wikidataLabel'],word, [idx-1,idx+1]])
        return candidatevectors

if __name__ == '__main__':
    v = Vectoriser()
#    print(v.vectorise("who is the president of India ?"))
    print(v.vectorise("what language is spoken in haiti today?"))

