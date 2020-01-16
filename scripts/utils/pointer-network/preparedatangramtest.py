import sys
import json
from elasticsearch import Elasticsearch
from fuzzywuzzy import fuzz
import requests
from annoy import AnnoyIndex
import re,random
from nltk.util import ngrams
from textblob import TextBlob

postags = ["CC","CD","DT","EX","FW","IN","JJ","JJR","JJS","LS","MD","NN","NNS","NNP","NNPS","PDT","POS","PRP","PRP$","RB","RBR","RBS","RP","SYM","TO","UH","VB","VBD","VBG","VBN","VBP","VBZ","WDT","WP","WP$","WRB"]
es = Elasticsearch()

writef = open('newvectorfiles/simpleqtestwv.json', 'a') 



def getembedding(enturl):
    entityurl = '<http://www.wikidata.org/entity/'+enturl[37:]+'>'
    res = es.search(index="wikidataembedsindex01", body={"query":{"term":{"key":{"value":entityurl}}}})
    try:
        embedding = [float(x) for x in res['hits']['hits'][0]['_source']['embedding']]
        return embedding
    except Exception as e:
        print(enturl,' not found')
        return None
    return None


fail = 0
def givewordvectors(id,question,entities):
    if not question:
        return []
    q = question
    q = re.sub("\s*\?", "", q.strip())
    candidatevectors = []
    #questionembedding
    r = requests.post("http://localhost:8887/ftwv",json={'chunks': [q]})
    questionembedding = r.json()[0]
    tokens = [token for token in q.split(" ") if token != ""]
    true = []
    false = []
    for idx,token in enumerate(tokens):
        #n
        r = requests.post("http://localhost:8887/ftwv",json={'chunks': [token]})
        wordvector = r.json()[0]
        esresult = es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":tokens[idx]}},"size":30})
        esresults = esresult['hits']['hits']
        if len(esresults) > 0:
            for entidx,esresult in enumerate(esresults):
                entityembedding = getembedding(esresult['_source']['uri'])
                if entityembedding and questionembedding :
                    if esresult['_source']['uri'][37:] in entities:
                        candidatevectors.append([entityembedding+questionembedding+wordvector+[entidx,idx,1],esresult['_source']['uri'][37:],1.0])
                    else:
                        candidatevectors.append([entityembedding+questionembedding+wordvector+[entidx,idx,1],esresult['_source']['uri'][37:],0.0])
        #n-1,n
        if idx > 0:
             word = tokens[idx-1]+' '+tokens[idx]
             esresult = es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word}},"size":30})
             esresults = esresult['hits']['hits']
             if len(esresults) > 0:
                 for entidx,esresult in enumerate(esresults):
                     entityembedding = getembedding(esresult['_source']['uri'])
                     if entityembedding and questionembedding :
                         if esresult['_source']['uri'][37:] in entities:
                             candidatevectors.append([entityembedding+questionembedding+wordvector+[entidx,idx,-2],esresult['_source']['uri'][37:],1.0])
                         else:
                             candidatevectors.append([entityembedding+questionembedding+wordvector+[entidx,idx,-2],esresult['_source']['uri'][37:],0.0])
        #n,n+1
        if idx < len(tokens) - 1:
            word = tokens[idx]+' '+tokens[idx+1]
            esresult = es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word}},"size":30})
            esresults = esresult['hits']['hits']
            if len(esresults) > 0:
                for entidx,esresult in enumerate(esresults):
                    entityembedding = getembedding(esresult['_source']['uri'])
                    if entityembedding and questionembedding :
                        if esresult['_source']['uri'][37:] in entities:
                            candidatevectors.append([entityembedding+questionembedding+wordvector+[entidx,idx,2],esresult['_source']['uri'][37:],1.0])
                        else:
                            candidatevectors.append([entityembedding+questionembedding+wordvector+[entidx,idx,2],esresult['_source']['uri'][37:],0.0])

        #n-1,n,n+1
        if idx < len(tokens) - 1 and idx > 0:
            word = tokens[idx-1]+' '+tokens[idx]+' '+tokens[idx+1]
            esresult = es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word}},"size":30})
            esresults = esresult['hits']['hits']
            if len(esresults) > 0:
                for entidx,esresult in enumerate(esresults):
                    entityembedding = getembedding(esresult['_source']['uri'])
                    if entityembedding and questionembedding :
                        if esresult['_source']['uri'][37:] in entities:
                            candidatevectors.append([entityembedding+questionembedding+wordvector+[entidx,idx,3],esresult['_source']['uri'][37:],1.0])
                        else:
                            candidatevectors.append([entityembedding+questionembedding+wordvector+[entidx,idx,3],esresult['_source']['uri'][37:],0.0])
     
    writef.write(json.dumps([id,item['entities'],candidatevectors])+'\n')
    return candidatevectors


d = json.loads(open('unifieddatasets/unifiedtest.json').read())
labelledcandidates = []
for idx,item in enumerate(d):
    if item['source'] != 'simplequestiontest':
        continue
    print(idx,item['question'])
    candidatevectors = givewordvectors(item['id'],item['question'],item['entities'])
    print(len(candidatevectors))
writef.close()
