# /usr/bin/python

import numpy as np
from elasticsearch import Elasticsearch
import urllib2,copy,json,sys,torch,re,requests
device = torch.device('cuda')

class ReRanker:
    def __init__(self):
        self.es = Elasticsearch()
        print "ReRanker initializing"
        try:
            N, D_in, H1, H2, H3 ,H4, D_out = 200, 801, 500, 300, 150, 50, 1

            self.model = torch.nn.Sequential(
              torch.nn.Linear(D_in, H1),
              torch.nn.ReLU(),
              torch.nn.Linear(H1, H2),
              torch.nn.ReLU(),
              torch.nn.Linear(H2, H3),
              torch.nn.ReLU(),
              torch.nn.Linear(H3, H4),
              torch.nn.ReLU(),
              torch.nn.Linear(H4, D_out)
            ).to(device)
            self.model.load_state_dict(torch.load('../../../data/jointreranker.037242.model'))
            self.model.eval()
        except Exception,e:
            print e
            sys.exit(1)
        print "ReRanker initialized"

    def getsentenceembedding(self, nlquery):
        req = urllib2.Request('http://localhost:8887/ftwv')
        req.add_header('Content-Type', 'application/json')
        inputjson = {'chunks':[nlquery]}
        response = urllib2.urlopen(req, json.dumps(inputjson))
        embedding = json.loads(response.read().decode('utf8'))[0]
        return embedding

    def getentityembedding(self,enturl):
        entityurl = '<http://www.wikidata.org/entity/'+enturl[37:]+'>'
        res = self.es.search(index="wikidataembedsindex01", body={"query":{"term":{"key":{"value":entityurl}}}})
        try:
            embedding = [float(x) for x in res['hits']['hits'][0]['_source']['embedding']]
            return embedding
        except Exception as e:
            print(e)
            return None
        return None

    def rerank(self, nlquery):
        candidatevectors = []
        candidateids = []
        #questionembedding
        r = requests.post("http://localhost:8887/ftwv",json={'chunks': [nlquery]})
        questionembedding = r.json()[0]
        for idx,word in enumerate(nlquery.split(' ')):
            #word vector
            r = requests.post("http://localhost:8887/ftwv",json={'chunks': [word]})
            wordvector = r.json()[0]
            #n
            esresult = self.es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word}},"size":3})
            esresults = esresult['hits']['hits']
            if len(esresults) > 0:
                for idx,esresult in enumerate(esresults):
                    entityembedding = self.getentityembedding(esresult['_source']['uri'])
                    if entityembedding and questionembedding and wordvector:
                        candidatevectors.append([entityembedding+[idx]+questionembedding+wordvector])
                        candidateids.append(esresult['_source']['uri'][37:])
        x = torch.FloatTensor(candidatevectors).to(device)
        preds = self.model(x).to(device).reshape(-1).cpu().detach().numpy()
        l = [(float(p),u) for p,u in zip(preds, candidateids)]
        reranked = sorted(l, key=lambda x: x[0], reverse=True)
        print(reranked)
        sys.exit(1)
            
if __name__ == '__main__':
    r = ReRanker()
    d = json.loads(open('unifieddatasets/LC-QuAD2.0/dataset/test.json').read())
    for item in d:
        #print(item)
        question = item['question']
        question = re.sub(r"[^a-zA-Z0-9]+", ' ', question)
        print(question)
        goldents = re.findall( r'wd:(.*?) ', item['sparql_wikidata'])
        print(goldents)
        if not question:
            continue
        entities = r.rerank(question)
    



    #print(r.rerank([{"chunk": {"chunk": "India", "surfacelength": -1, "class": "entity", "surfacestart": -1}, "topkmatches": ["Q1488929", "Q17055962", "Q22043425", "Q11157534", "Q16578519", "Q36548019", "Q274592", "Q15975440", "Q16429066", "Q50755762", "Q3624238", "Q5802812", "Q39542602", "Q668", "Q23642847", "Q17055987", "Q17014026", "Q2060630", "Q1936198", "Q39611746", "Q39457540", "Q47586501", "Q1963604", "Q6019237", "Q6019242", "Q6019245", "Q37186648", "Q6866034", "Q6866064", "Q712499"], "class": "entity"}], "who is the president of india ?"))
