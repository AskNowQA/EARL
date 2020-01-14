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

writef = open('newvectorfiles/webquestionstest_unigram.json', 'a')



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
    try:
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
        r = requests.post("http://localhost:8887/ftwv",json={'chunks': tokens})
        wordvectors = r.json()
        wordcount = 0
        for wordvector,token in zip(wordvectors,tokens):
            word = token
            esresult = es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word}},"size":30})
            esresults = esresult['hits']['hits']
            if len(esresults) > 0:
                for idx,esresult in enumerate(esresults):
                    entityembedding = getembedding(esresult['_source']['uri'])
                    if entityembedding and questionembedding and wordvector:
                        if esresult['_source']['uri'][37:] in entities:
                            candidatevectors.append([entityembedding+questionembedding+wordvector+[idx,wordcount],esresult['_source']['uri'][37:],1.0])
                        else:
                            candidatevectors.append([entityembedding+questionembedding+wordvector+[idx,wordcount],esresult['_source']['uri'][37:],0.0])
            wordcount += 1
        #candidatevectors += true
        #candidatevectors += random.sample(false,k=len(true))
        writef.write(json.dumps([id,item['entities'],candidatevectors])+'\n')
        return candidatevectors
    except Exception as e:
        print(e)
        return []


d = json.loads(open('unifieddatasets/unifiedtest.json').read())
labelledcandidates = []
for idx,item in enumerate(d):
    print(idx,item['question'])
    if item['source'] != 'webqtest':
        continue
    print(idx,item)
    candidatevectors = givewordvectors(item['id'],item['question'],item['entities'])
    #labelledcandidates.append(candidatevectors)
#f = open('unifieddatasets/pointercandidatevectorstrain1.json','w')
#f.write(json.dumps(labelledcandidates,indent=4))
#f.close()
writef.close()
