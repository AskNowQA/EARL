import sys
import json
import re
import requests
from elasticsearch import Elasticsearch
from textblob import TextBlob
import numpy as np
from multiprocessing import Pool
from fuzzywuzzy import fuzz

postags = ["CC","CD","DT","EX","FW","IN","JJ","JJR","JJS","LS","MD","NN","NNS","NNP","NNPS","PDT","POS","PRP","PRP$","RB","RBR","RBS","RP","SYM","TO","UH","VB","VBD","VBG","VBN","VBP","VBZ","WDT","WP","WP$","WRB"]

es = Elasticsearch()
entembedcache = {}
descembedcache = {}
def getembedding(enturl):
    if enturl in entembedcache:
        return entembedcache[enturl]
    entityurl = '<http://www.wikidata.org/entity/'+enturl[37:]+'>'
    res = es.search(index="wikidataembedsindex01", body={"query":{"term":{"key":{"value":entityurl}}}})
    try:
        embedding = [float(x) for x in res['hits']['hits'][0]['_source']['embedding']]
        entembedcache[enturl] = embedding
        return embedding
    except Exception as e:
        print(enturl,' entity embedding not found')
        return None
    return None

def gettextmatchmetric(label,word):
    return [fuzz.ratio(label,word)/100.0,fuzz.partial_ratio(label,word)/100.0,fuzz.token_sort_ratio(label,word)/100.0]

def getdescriptionsembedding(entid):
    if entid in descembedcache:
        return descembedcache[entid]
    res = es.search(index="wikidataentitydescriptionsindex01", body={"query":{"term":{"entityid.keyword":entid}}})
    if len(res['hits']['hits']) == 0:
        return [0]*300
    try:
        description = res['hits']['hits'][0]['_source']['description']
        r = requests.post("http://localhost:8887/ftwv",json={'chunks': [description]},headers={'Connection':'close'})
        descembedding = r.json()[0]
        descembedcache[entid] = descembedding
        return descembedding
    except Exception as e:
        print("getdescriptionsembedding err: ",e)
        return [0]*300
    return [0]*300
 
def CreateVectors(inputcandidatetuple):
    candidatevectors = []
    tokens,questionembeddings,questionembedding,chunks,idx,chunk = inputcandidatetuple
    try:
        #n
        posonehot = len(postags)*[0.0]
        posonehot[postags.index(chunk[1])] = 1
        tokenembedding = questionembeddings[idx]
        word = chunks[idx][0]
        res = es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":chunks[idx][0]}},"size":30})
        esresults = res['hits']['hits']
        if len(esresults) > 0:
            for entidx,esresult in enumerate(esresults):
                descembedding = getdescriptionsembedding(esresult['_source']['uri'][37:])
                entityembedding = getembedding(esresult['_source']['uri'])
                label = esresult['_source']['wikidataLabel']
                textmatchmetric = gettextmatchmetric(label, word)
                if entityembedding and questionembedding :
                    candidatevectors.append([questionembedding+tokenembedding+entityembedding+descembedding+posonehot+textmatchmetric+[entidx,idx,1],esresult['_source']['uri'][37:],esresult['_source']['wikidataLabel'],tokens[idx], [idx,idx]])
        #n-1,n
        if idx > 0:
             word = chunks[idx-1][0]+' '+chunks[idx][0]
             res = es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word}},"size":30})
             esresults = res['hits']['hits']
             if len(esresults) > 0:
                 for entidx,esresult in enumerate(esresults):
                     descembedding = getdescriptionsembedding(esresult['_source']['uri'][37:])
                     entityembedding = getembedding(esresult['_source']['uri'])
                     label = esresult['_source']['wikidataLabel']
                     textmatchmetric = gettextmatchmetric(label, word)
                     if entityembedding and questionembedding :
                         candidatevectors.append([questionembedding+tokenembedding+entityembedding+descembedding+posonehot+textmatchmetric+[entidx,idx,-2],esresult['_source']['uri'][37:],esresult['_source']['wikidataLabel'],word, [idx-1,idx]])
        #n,n+1
        if idx < len(tokens) - 1:
            word = chunks[idx][0]+' '+chunks[idx+1][0]
            res = es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word}},"size":30})
            esresults = res['hits']['hits']
            if len(esresults) > 0:
                for entidx,esresult in enumerate(esresults):
                    descembedding = getdescriptionsembedding(esresult['_source']['uri'][37:])
                    entityembedding = getembedding(esresult['_source']['uri'])
                    label = esresult['_source']['wikidataLabel']
                    textmatchmetric = gettextmatchmetric(label, word)
                    if entityembedding and questionembedding :
                        candidatevectors.append([questionembedding+tokenembedding+entityembedding+descembedding+posonehot+textmatchmetric+[entidx,idx,2],esresult['_source']['uri'][37:],esresult['_source']['wikidataLabel'],word, [idx,idx+1]])

        #n-1,n,n+1
        if idx < len(tokens) - 1 and idx > 0:
            word = chunks[idx-1][0]+' '+chunks[idx][0]+' '+chunks[idx+1][0]
            res = es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word}},"size":30})
            esresults = res['hits']['hits']
            if len(esresults) > 0:
                for entidx,esresult in enumerate(esresults):
                    escembedding = getdescriptionsembedding(esresult['_source']['uri'][37:])
                    entityembedding = getembedding(esresult['_source']['uri'])
                    label = esresult['_source']['wikidataLabel']
                    textmatchmetric = gettextmatchmetric(label, word)
                    if entityembedding and questionembedding :
                        candidatevectors.append([questionembedding+tokenembedding+entityembedding+descembedding+posonehot+textmatchmetric+[entidx,idx,3],esresult['_source']['uri'][37:],esresult['_source']['wikidataLabel'],word, [idx-1,idx+1]])
        return candidatevectors
    except Exception as err:
        print(err, "Createvectorfail")
        return candidatevectors           


class Vectoriser():
    def __init__(self):
       print("Initialising Vectoriser")
       self.pool = Pool(10)
       print("Initialised Vectoriser")
   

    def vectorise(self,nlquery):
        if not nlquery:
            return []
        q = re.sub("\s*\?", "", nlquery.strip())
        pos = TextBlob(q)
        chunks = pos.tags
        candidatevectors = []
        #questionembedding
        tokens = [token for token in q.split(" ") if token != ""]
        r = requests.post("http://localhost:8887/ftwv",json={'chunks': tokens},headers={'Connection':'close'})
        questionembeddings = r.json()
        questionembedding = list(map(lambda x: sum(x)/len(x), zip(*questionembeddings)))
        true = []
        false = []
        inputcandidates = []
        for idx,chunk in enumerate(chunks):
            inputcandidates.append((tokens,questionembeddings,questionembedding,chunks,idx,chunk))
        responses = self.pool.imap(CreateVectors, inputcandidates)
        print("Received pool response")
        for response in responses:
            candidatevectors += response
        #self.pool.close()
        return candidatevectors

if __name__ == '__main__':
    v = Vectoriser()
#    print(v.vectorise("who is the president of India ?"))
    print(json.dumps(v.vectorise("what electorate does anna bligh represent?")))
