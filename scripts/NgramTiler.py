import sys
import urllib
import json
from elasticsearch import Elasticsearch
from fuzzywuzzy import fuzz
import torch
import numpy as np
from  more_itertools import unique_everseen
from pybloom import ScalableBloomFilter

device = torch.device('cpu')

class NgramTiler:
    def __init__(self):
       print("Initialising Ngram tiler, loading blooms")
       self.es = Elasticsearch()
       D_in = 9
       H = 9
       D_out = 1
       self.entityfiltermodel = torch.nn.Sequential(
          torch.nn.Linear(D_in, H),
          torch.nn.ReLU(),
          torch.nn.Linear(D_in, H),
          torch.nn.ReLU(),
          torch.nn.Linear(H, D_out)#,
#          torch.nn.Sigmoid()
        ).to(device)
       self.entityfiltermodel.load_state_dict(torch.load('../data/entityfilter0.65loss.model', map_location=device))
       self.entityfiltermodel.eval()
       print("Initialised ngram tiler")

    def filterbybloom(self, relchunks, sortedentityuris):
        added = {}
        filteredrelchunks = []
        for entityuri in sortedentityuris:
            for relationdict in relchunks:
                for relationuri in relationdict['uris']:
                    if relationuri in added:
                        continue
                    bloomstring = entityuri['uri']+':'+relationuri
                    if (bloomstring in self.bloom1hoppred) or (bloomstring in self.bloomqualifier) or  (bloomstring in self.bloom1hoptypeofentity):
                        added[relationuri] = None
                        filteredrelchunks.append(relationdict)
                        #print(len(sortedentityuris), len(relchunks), bloomstring,relationdict)
        #print(len(filteredrelchunks))
        return filteredrelchunks

    def generate_ngrams(self, s, n):
        #s = re.sub(r'[^a-zA-Z0-9\s]', ' ', s)
        if not s:
            tokens = []
        else:
            tokens = [token for token in s.split(" ") if token != ""]

        # Use the zip function to help us generate n-grams
        # Concatentate the tokens into ngrams and return
        ngrams = zip(*[tokens[i:] for i in range(n)])
        return [" ".join(ngram) for ngram in ngrams]


    def ngramtiler(self, nlquery):
        q = nlquery
        entities = {}
        relations = []
        uricounter = {}
        #entities
        for i in range(1,4):
            ngrams = self.generate_ngrams(q, i)
            for ngram in ngrams:
                #entitycandidates
                res = self.es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":ngram,"fields":["wikidataLabel"]}},"size":100})
                for idx,hit in enumerate(res['hits']['hits']):
                    eslabel = hit['_source']['wikidataLabel']
                    uri = hit['_source']['uri']
                    fuzzvector = [fuzz.ratio(eslabel, ngram)/100.0, fuzz.partial_ratio(eslabel, ngram)/100.0, fuzz.token_sort_ratio(eslabel, ngram)/100.0, fuzz.ratio(eslabel, q)/100.0, fuzz.partial_ratio(eslabel, q)/100.0, fuzz.token_sort_ratio(eslabel, q)/100.0, idx, i]
                    if uri in uricounter:
                        uricounter[uri] += 1
                    else:
                        uricounter[uri] = 1
                    entities[uri+'_'+str(uricounter[uri])] = {'eslabel':eslabel, 'ngram': ngram, 'vector': fuzzvector, 'uri': uri, 'class': 'entity', 'uricounter':uricounter[uri]}
        testuris = []
        testvectors = []
        for uri,ngramdetail in entities.items():
            testuris.append(ngramdetail)
            testvectors.append(ngramdetail['vector']+[ngramdetail['uricounter']])
        testtensors = torch.tensor(testvectors,dtype=torch.float).to(device)
        testpreds = self.entityfiltermodel(testtensors)
        testpreds = [num[0] for num in testpreds.tolist()]
        sortedentityuris = list(unique_everseen([{'uri':uri['uri'],'ngram':uri['ngram'], 'eslabel':uri['eslabel'], 'predscore': pred, 'class':'entity'} for pred,uri in sorted(zip(testpreds,testuris), key=lambda x: x[0], reverse=True)]))[:100]
        #relations
        relchunks = []
        for i in range(1,4):
            ngrams = self.generate_ngrams(q, i)
            for ngram in ngrams:
                if len(ngram) < 4:
                    continue
                relchunks.append({'chunk': ngram, 'ngramsize': i,  'surfacelength': len(ngram), 'class': 'relation', 'surfacestart': -1})
        #relation candidates
        inputJson = {'chunks': relchunks, 'pagerankflag':False}
        params = json.dumps(inputJson).encode('utf8')
        req = urllib.request.Request('http://localhost:8887/textMatch', data=params,
                             headers={'content-type': 'application/json'})
        response = urllib.request.urlopen(req)

        relchunkdistances = json.loads(response.read())
        purerelchunks = []
        for relchunk in relchunkdistances:
            purerelchunks += relchunk['topkmatches']
        purerelchunks = sorted(purerelchunks, key=lambda s: s['distance'])[:100]
        #bloomcheckrels = self.filterbybloom(purerelchunks, sortedentityuris)
        #connectedreluris = [{'uri':uri,'ngram':rel['inputlabel']} for rel in bloomcheckrels for uri in rel['uris']]
        return({'question':q, 'entities': sortedentityuris, 'relations': purerelchunks}) 
 
      

if __name__ == '__main__':
    e = NgramTiler()
#    print(e.ngramtiler("name the place of qaqun"))
#    print(e.ngramtiler("who is the president of india?"))
#    print(e.ngramtiler("Who is the president of India?"))
#    print(e.ngramtiler("Who is the father of the mother of Barack Obama"))
#    print(e.ngramtiler("who is the father of the mother of barack obama"))
#    print(e.ngramtiler("How many rivers flow through Bonn?"))
#    print(e.ngramtiler("how many rivers flow through bonn?"))
#    print(e.ngramtiler("List all the musicals with music by Elton John."))
#    print(e.ngramtiler("Give me the names of professional skateboarders of India"))
    print(json.dumps(e.ngramtiler("Was Jessica Chastain nominated for Academy Award for Best Picture ?")))
