import sys,os,json,re
from elasticsearch import Elasticsearch
from fuzzywuzzy import fuzz
from itertools import groupby

def generate_ngrams(s, n):
    if not s:
        tokens = []
    else:
        tokens = [token for token in s.split(" ") if token != ""]
    
    # Use the zip function to help us generate n-grams
    # Concatentate the tokens into ngrams and return
    ngrams = zip(*[tokens[i:] for i in range(n)])
    return [" ".join(ngram) for ngram in ngrams]


es = Elasticsearch()

d = json.loads(open('unifieddatasets/unifiedtrain.json').read())
spanarr = []
for iddx,item in enumerate(d):
    unit = {}
    entities = item['entities']
    question = item['question']
    ngrammatchdict = {}
    for i in range(1,4):
        ngrams = generate_ngrams(question, i)
        for ngram in ngrams:
            #entities
            res = es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":ngram,"fields":["wikidataLabel"]}},"size":200})
            for idx,hit in enumerate(res['hits']['hits']):
                entid = hit['_source']['uri'][37:] 
                if entid in entities:
                    if entid in ngrammatchdict:
                        if idx < ngrammatchdict[entid]['esrank']:
                            ngrammatchdict[entid] = {'ngram':ngram,'esrank':idx}
                    else:
                        ngrammatchdict[entid] = {'ngram':ngram,'esrank':idx}
             
    unit['uid'] = item['id']
    unit['question'] = item['question']
    unit['spanmatch'] = ngrammatchdict
    spanarr.append(unit)
    print(iddx,item['id'],unit,entities)

f = open('unifieddatasets/unifiedtrainbestspans1.json','w')
f.write(json.dumps(spanarr,indent=4, sort_keys=True))
f.close()
