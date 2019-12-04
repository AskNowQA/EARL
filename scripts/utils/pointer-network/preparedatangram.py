import sys
import json
from elasticsearch import Elasticsearch
from fuzzywuzzy import fuzz
import requests
import re,random
from nltk.util import ngrams
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
        ngramarr = []
        for n in range(1,4):
            ngramwords = list(ngrams(tokens, n))
            for tup in ngramwords:
                ngramjoined = ' '.join(tup)
                ngramarr.append([ngramjoined,n])
                #word vector
        r = requests.post("http://localhost:8887/ftwv",json={'chunks': [x[0] for x in ngramarr]})
        wordvectors = r.json()
        for wordvector,ngramtup in zip(wordvectors,ngramarr):
            word = ngramtup[0]
            n = ngramtup[1]
            esresult = es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word}},"size":10})
            esresults = esresult['hits']['hits']
            if len(esresults) > 0:
                for idx,esresult in enumerate(esresults):
                    entityembedding = getembedding(esresult['_source']['uri'])
                    if entityembedding and questionembedding and wordvector:
                        if esresult['_source']['uri'][37:] in entities:
                            true.append([entityembedding+questionembedding+wordvector+[idx,n],esresult['_source']['uri'][37:],1.0])
                        else:
                            false.append([entityembedding+questionembedding+wordvector+[idx,n],esresult['_source']['uri'][37:],0.0])
        candidatevectors += true
        candidatevectors += random.sample(false,k=len(true)) 
        return candidatevectors
    except Exception as e:
        print(e)
        return []


d = json.loads(open('unifieddatasets/unifiedtraindeduplicate.json').read())
labelledcandidates = []
for idx,item in enumerate(d):
    print(idx,item['question'])
    candidatevectors = givewordvectors(item['question'],item['entities'])
    labelledcandidates.append(candidatevectors)
f = open('unifieddatasets/pointercandidatevectorstrain1.json','w')
f.write(json.dumps(labelledcandidates,indent=4))
f.close()
