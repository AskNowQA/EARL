# /usr/bin/python

import numpy as np
from elasticsearch import Elasticsearch
import urllib2,copy,json,sys,torch
device = torch.device('cuda')

class ReRanker:
    def __init__(self):
        self.es = Elasticsearch()
        print "ReRanker initializing"
        try:
            N, D_in, H1, H2, H3, D_out = 100, 501, 300, 100, 10, 1
            self.model = torch.nn.Sequential(
              torch.nn.Linear(D_in, H1),
              torch.nn.ReLU(),
              torch.nn.Linear(H1, H2),
              torch.nn.ReLU(),
              torch.nn.Linear(H2, H3),
              torch.nn.ReLU(),
              torch.nn.Linear(H3, D_out)
            ).to(device)
            self.model.load_state_dict(torch.load('../data/embedentreranker.044678.model'))
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

    def getentityembedding(self,entid):
        entityurl = '<http://www.wikidata.org/entity/'+entid+'>'
        res = self.es.search(index="wikidataembedsindex01", body={"query":{"term":{"key":{"value":entityurl}}}})
        try:
            embedding = [float(x) for x in res['hits']['hits'][0]['_source']['embedding']]
            return embedding
        except Exception as e:
            print(e)
            return None
        return None

    def rerank(self, topklists, nlquery):
        rerankedlists = []
        question = nlquery
        for chunk in topklists:
            question = question.replace(chunk['chunk']['chunk'], "")
        questionembedding = self.getsentenceembedding(question)
        for chunk in topklists:
            inputfeatures = []
            for idx,entid in enumerate(chunk['topkmatches']):
                entityembedding = self.getentityembedding(entid)
                if not entityembedding or not questionembedding:
                    continue
                vector = [idx]+entityembedding+questionembedding
                inputfeatures.append(vector)
            x = torch.FloatTensor(inputfeatures).to(device)
            preds = self.model(x).to(device).reshape(-1).cpu().detach().numpy()
            l = [(float(p),u) for p,u in zip(preds, chunk['topkmatches'])]
            reranked = sorted(l, key=lambda x: x[0], reverse=True)
            if reranked[0][0] < 0.5:
                continue
            reranked = [x[1] for x in reranked]
            cchunk = copy.deepcopy(chunk)
            cchunk['reranked'] = reranked
            rerankedlists.append(cchunk)
        return rerankedlists
            
if __name__ == '__main__':
    r = ReRanker()
    print(r.rerank([{"chunk": {"chunk": "India", "surfacelength": -1, "class": "entity", "surfacestart": -1}, "topkmatches": ["Q1488929", "Q17055962", "Q22043425", "Q11157534", "Q16578519", "Q36548019", "Q274592", "Q15975440", "Q16429066", "Q50755762", "Q3624238", "Q5802812", "Q39542602", "Q668", "Q23642847", "Q17055987", "Q17014026", "Q2060630", "Q1936198", "Q39611746", "Q39457540", "Q47586501", "Q1963604", "Q6019237", "Q6019242", "Q6019245", "Q37186648", "Q6866034", "Q6866064", "Q712499"], "class": "entity"}], "who is the president of india ?"))
