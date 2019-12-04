import sys
import json
from elasticsearch import Elasticsearch
from fuzzywuzzy import fuzz
import requests
import re
from textblob import TextBlob

postags = ["CC","CD","DT","EX","FW","IN","JJ","JJR","JJS","LS","MD","NN","NNS","NNP","NNPS","PDT","POS","PRP","PRP$","RB","RBR","RBS","RP","SYM","TO","UH","VB","VBD","VBG","VBN","VBP","VBZ","WDT","WP","WP$","WRB"]
es = Elasticsearch()


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



def givewordvectors(question,entities):
    if not question:
        return []
    q = question
    q = re.sub("\s*\?", "", q.strip())
    result = TextBlob(q)
    chunks = result.tags
    candidatevectors = []
    chunkswords = []
    #questionembedding
    r = requests.post("http://localhost:8887/ftwv",json={'chunks': [q]})
    questionembedding = r.json()[0]
    for chunk,word in zip(chunks,q.split(' ')):
        chunkswords.append((chunk,word))
    for idx,chunkwordtuple in enumerate(chunkswords):
        #word vector
        word = chunkwordtuple[1]
        r = requests.post("http://localhost:8887/ftwv",json={'chunks': [word]})
        wordvector = r.json()[0]
        #n
        esresult = es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word}},"size":3})
        esresults = esresult['hits']['hits']
        if len(esresults) > 0:
            for idx,esresult in enumerate(esresults):
                entityembedding = getembedding(esresult['_source']['uri'])
                if entityembedding and questionembedding and wordvector:
                    if esresult['_source']['uri'][37:] in entities:
                        candidatevectors.append([entityembedding+[idx]+questionembedding+wordvector,esresult['_source']['uri'][37:],1.0])
                    else:
                        candidatevectors.append([entityembedding+[idx]+questionembedding+wordvector,esresult['_source']['uri'][37:],0.0])
    return candidatevectors


d = json.loads(open('unifieddatasets/unifiedtestdeduplicate.json').read())
labelledcandidates = []
for idx,item in enumerate(d):
    print(idx,item['question'])
    candidatevectors = givewordvectors(item['question'],item['entities'])
    labelledcandidates.append(candidatevectors)
f = open('unifieddatasets/pointercandidatevectorstest1.json','w')
f.write(json.dumps(labelledcandidates))
f.close()
