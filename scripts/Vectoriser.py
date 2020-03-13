import sys
import json
import re
import requests
from elasticsearch import Elasticsearch
from textblob import TextBlob
import numpy as np
postags = ["CC","CD","DT","EX","FW","IN","JJ","JJR","JJS","LS","MD","NN","NNS","NNP","NNPS","PDT","POS","PRP","PRP$","RB","RBR","RBS","RP","SYM","TO","UH","VB","VBD","VBG","VBN","VBP","VBZ","WDT","WP","WP$","WRB"]

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
            print(enturl,' entity embedding not found')
            return None
        return None

    def getdescriptionsembedding(self, entid):
        res = self.es.search(index="wikidataentitydescriptionsindex01", body={"query":{"term":{"entityid.keyword":entid}}})
        if len(res['hits']['hits']) == 0:
            return [0]*300
        try:
            description = res['hits']['hits'][0]['_source']['description']
            r = requests.post("http://localhost:8887/ftwv",json={'chunks': [description]})
            descembedding = r.json()[0]
            return descembedding
        except Exception as e:
            print("getdescriptionsembedding err: ",e)
            return [0]*300
        return [0]*300
     
    def getlabelembedding(self,label):
        try:
            r = requests.post("http://localhost:8887/ftwv",json={'chunks': [label]})
            labelembedding = r.json()[0]
            return labelembedding
        except Exception as e:
            print("getlabelsembedding err: ",e)
            return [0]*300
        return [0]*300

    def vectorise(self,nlquery):
        if not nlquery:
            return []
        q = re.sub("\s*\?", "", nlquery.strip())
        pos = TextBlob(q)
        chunks = pos.tags
        candidatevectors = []
        #questionembedding
        tokens = [token for token in q.split(" ") if token != ""]
        r = requests.post("http://localhost:8887/ftwv",json={'chunks': tokens})
        questionembeddings = r.json()
        questionembedding = list(map(lambda x: sum(x)/len(x), zip(*questionembeddings))) 
        true = []
        false = []
        for idx,chunk in enumerate(chunks):
            try:
                #n
                posonehot = len(postags)*[0.0]
                posonehot[postags.index(chunk[1])] = 1
                print(posonehot)
                tokenembedding = questionembeddings[idx]
                res = self.es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":chunks[idx][0]}},"size":30})
                esresults = res['hits']['hits']
                if len(esresults) > 0:
                    for entidx,esresult in enumerate(esresults):
                        entityembedding = self.getembedding(esresult['_source']['uri'])
                        descembedding = self.getdescriptionsembedding(esresult['_source']['uri'][37:])
                        labelembedding = self.getlabelembedding(esresult['_source']['wikidataLabel'])
                        if entityembedding and questionembedding :
                            candidatevectors.append([questionembedding+tokenembedding+descembedding+labelembedding+entityembedding+posonehot+[entidx,idx,1],esresult['_source']['uri'][37:],esresult['_source']['wikidataLabel'],tokens[idx], [idx,idx]])
                #n-1,n
                if idx > 0:
                     word = chunks[idx-1][0]+' '+chunks[idx][0]
                     res = self.es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word}},"size":30})
                     esresults = res['hits']['hits']
                     if len(esresults) > 0:
                         for entidx,esresult in enumerate(esresults):
                             entityembedding = self.getembedding(esresult['_source']['uri'])
                             descembedding = self.getdescriptionsembedding(esresult['_source']['uri'][37:])
                             labelembedding = self.getlabelembedding(esresult['_source']['wikidataLabel'])
                             if entityembedding and questionembedding :
                                 candidatevectors.append([questionembedding+tokenembedding+descembedding+labelembedding+entityembedding+posonehot+[entidx,idx,-2],esresult['_source']['uri'][37:],esresult['_source']['wikidataLabel'],word, [idx-1,idx]])
                #n,n+1
                if idx < len(tokens) - 1:
                    word = chunks[idx][0]+' '+chunks[idx+1][0]
                    res = self.es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word}},"size":30})
                    esresults = res['hits']['hits']
                    if len(esresults) > 0:
                        for entidx,esresult in enumerate(esresults):
                            entityembedding = self.getembedding(esresult['_source']['uri'])
                            descembedding = self.getdescriptionsembedding(esresult['_source']['uri'][37:])
                            labelembedding = self.getlabelembedding(esresult['_source']['wikidataLabel'])
                            if entityembedding and questionembedding :
                                candidatevectors.append([questionembedding+tokenembedding+descembedding+labelembedding+entityembedding+posonehot+[entidx,idx,2],esresult['_source']['uri'][37:],esresult['_source']['wikidataLabel'],word, [idx,idx+1]])
        
                #n-1,n,n+1
                if idx < len(tokens) - 1 and idx > 0:
                    word = chunks[idx-1][0]+' '+chunks[idx][0]+' '+chunks[idx+1][0]
                    res = self.es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word}},"size":30})
                    esresults = res['hits']['hits']
                    if len(esresults) > 0:
                        for entidx,esresult in enumerate(esresults):
                            entityembedding = self.getembedding(esresult['_source']['uri'])
                            descembedding = self.getdescriptionsembedding(esresult['_source']['uri'][37:])
                            labelembedding = self.getlabelembedding(esresult['_source']['wikidataLabel'])
                            if entityembedding and questionembedding :
                                candidatevectors.append([questionembedding+tokenembedding+descembedding+labelembedding+entityembedding+posonehot+[entidx,idx,3],esresult['_source']['uri'][37:],esresult['_source']['wikidataLabel'],word, [idx-1,idx+1]])
            except Exception as e:
                print('mainfunerror: ',e)
        return candidatevectors

if __name__ == '__main__':
    v = Vectoriser()
#    print(v.vectorise("who is the president of India ?"))
    print(json.dumps(v.vectorise("what electorate does anna bligh represent?")))

