import sys
import json
from elasticsearch import Elasticsearch
from fuzzywuzzy import fuzz
import requests
import re
from textblob import TextBlob

postags = ["CC","CD","DT","EX","FW","IN","JJ","JJR","JJS","LS","MD","NN","NNS","NNP","NNPS","PDT","POS","PRP","PRP$","RB","RBR","RBS","RP","SYM","TO","UH","VB","VBD","VBG","VBN","VBP","VBZ","WDT","WP","WP$","WRB"]
es = Elasticsearch()

def givewordvectors(question):
    q = question
    #q = re.sub("\s*\?", "", q.strip())
    result = TextBlob(q)
    chunks = result.tags
    fuzzscores = []
    wordvectors = []
    chunkswords = []
    for chunk,word in zip(chunks,q.split(' ')):
        chunkswords.append((chunk,word))
    for idx,chunkwordtuple in enumerate(chunkswords):
        word = chunkwordtuple[1]
        r = requests.post("http://localhost:8887/ftwv",json={'chunks': [word]})
        embedding = r.json()[0]
        wordvector = embedding
        #n-1,n
        if idx > 0:
            word = chunkswords[idx-1][1] + ' ' + chunkswords[idx][1]
            esresult = es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word,"fields":["wikidataLabel"]}},"size":10})
            esresults = esresult['hits']['hits']
            if len(esresults) > 0:
                for esresult in esresults:
                    wordvector +=  [fuzz.ratio(word, esresult['_source']['wikidataLabel'])/100.0, fuzz.partial_ratio(word, esresult['_source']['wikidataLabel'])/100.0, fuzz.token_sort_ratio(word, esresult['_source']['wikidataLabel'])/100.0]
                wordvector += (10-len(esresults)) * [0.0,0.0,0.0]
            else:
                wordvector +=  10*[0.0,0.0,0.0]
        else:
            wordvector +=  10*[0.0,0.0,0.0]
        #n
        word = chunkwordtuple[1] 
        esresult = es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word,"fields":["wikidataLabel"]}},"size":10})
        esresults = esresult['hits']['hits']
        if len(esresults) > 0:
            for esresult in esresults:
                wordvector +=  [fuzz.ratio(word, esresult['_source']['wikidataLabel'])/100.0, fuzz.partial_ratio(word, esresult['_source']['wikidataLabel'])/100.0, fuzz.token_sort_ratio(word, esresult['_source']['wikidataLabel'])/100.0]
            wordvector += (10-len(esresults)) * [0.0,0.0,0.0]
        else:
            wordvector +=  10*[0.0,0.0,0.0]
        #n,n+1
        if idx < len(chunkswords)-1:
            word = chunkswords[idx][1] + ' ' + chunkswords[idx+1][1]
            esresult = es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word,"fields":["wikidataLabel"]}},"size":10})
            esresults = esresult['hits']['hits']
            if len(esresults) > 0:
                for esresult in esresults:
                    wordvector +=  [fuzz.ratio(word, esresult['_source']['wikidataLabel'])/100.0, fuzz.partial_ratio(word, esresult['_source']['wikidataLabel'])/100.0, fuzz.token_sort_ratio(word, esresult['_source']['wikidataLabel'])/100.0]
                wordvector += (10-len(esresults)) * [0.0,0.0,0.0]
            else:
                wordvector +=  10*[0.0,0.0,0.0]
        else:
            wordvector +=  10*[0.0,0.0,0.0]
        #n-1,n,n+1
        if idx > 0 and idx < len(chunkswords)-1:
            word = chunkswords[idx-1][1] + ' ' + chunkswords[idx][1] + ' ' + chunkswords[idx+1][1]
            esresult = es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word,"fields":["wikidataLabel"]}},"size":10})
            esresults = esresult['hits']['hits']
            if len(esresults) > 0:
                for esresult in esresults:
                    wordvector +=  [fuzz.ratio(word, esresult['_source']['wikidataLabel'])/100.0, fuzz.partial_ratio(word, esresult['_source']['wikidataLabel'])/100.0, fuzz.token_sort_ratio(word, esresult['_source']['wikidataLabel'])/100.0]
                wordvector += (10-len(esresults)) * [0.0,0.0,0.0]
            else:
                wordvector +=  10*[0.0,0.0,0.0]
        else:
            wordvector +=  10*[0.0,0.0,0.0]
        posonehot = len(postags)*[0.0]
        posonehot[postags.index(chunk[1])] = 1
        wordvector += posonehot
        if len(wordvector) != 456:
            print(len(wordvector))
            print("word vec len wrong")
            sys.exit(1)
        wordvectors.append(wordvector)
    return wordvectors


d = json.loads(open('unifieddatasets/erspans.json').read())
items = []
for item in d:
    wordvectors = givewordvectors(item['question'])
    iu = {}
    iu['question'] = item['question']
    iu['wordvectors'] = wordvectors
    iu['erspan'] = item['erspan']
    items.append(iu)
f = open('unifieddatasets/entityonlywordvecsngrams1.json','w')
f.write(json.dumps(items))
f.close()

