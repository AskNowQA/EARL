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
            N, D_in, H1, H2, H3 ,H4, D_out = 200, 802, 500, 250, 100, 50, 1

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
            self.model.load_state_dict(torch.load('../data/embentreranker.039443.model'))
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

    def getjointembedding(self, chunkembeddings, chunkindex, embedding):
        bestdot = -1
        for qchunkindex,qentities in chunkembeddings.items():
            if chunkindex == qchunkindex:
                continue
            for qentid,qembedding in qentities.items():
                dotproduct = np.dot(np.asarray(qembedding),np.asarray(embedding))
                if dotproduct > bestdot:
                    bestdot = dotproduct
        return embedding + [bestdot]

    def getdescriptionsembedding(self,entid):
        res = self.es.search(index="wikidataentitydescriptionsindex01", body={"query":{"term":{"entityid.keyword":entid}}})
        try:
            description = res['hits']['hits'][0]['_source']['description']
            req = urllib2.Request('http://localhost:8887/ftwv')
            req.add_header('Content-Type', 'application/json')
            inputjson = {'chunks':[description]}
            response = urllib2.urlopen(req, json.dumps(inputjson))
            descembedding = json.loads(response.read().decode('utf8'))[0]
            return descembedding
        except Exception as e:
            print("getdescriptionsembedding err: ",e)
            return None
        return None


    def rerank(self, topklists, nlquery):
        questionembedding = self.getsentenceembedding(nlquery)
        chunkembeddings = {}
        rerankedlists = []
        listoflistofentities = []
        for chunkindex,chunk in enumerate(topklists):
            if chunkindex not in chunkembeddings:
                chunkembeddings[chunkindex] = {}
            for idx,entidlabel in enumerate(chunk['topkmatches']):
                entid = entidlabel[0]
                embedding = self.getentityembedding(entid)
                if not embedding:
                    print("no embedding for %s"%entid)
                    continue
                chunkembeddings[chunkindex][entid] = embedding
            listoflistofentities.append(topklists[chunkindex]['topkmatches'])
        for chunkidx,listofentities in enumerate(listoflistofentities):
            inputfeatures = []
            for entidx,entidlabel in enumerate(listofentities):
                entid = entidlabel[0]
                if entid in chunkembeddings[chunkidx]:
                    entembedding = chunkembeddings[chunkidx][entid]
                else:
                    continue
                jointembed = self.getjointembedding(chunkembeddings,chunkidx,entembedding)
                vector = jointembed+[entidx]+questionembedding
                descembed = self.getdescriptionsembedding(entid)
                if not descembed:
                    descembed = [0]*300
                inputfeatures.append(vector+descembed)
            x = torch.FloatTensor(inputfeatures).to(device)
            preds = self.model(x).to(device).reshape(-1).cpu().detach().numpy()
            l = [(float(p),u) for p,u in zip(preds, listofentities)]
            reranked = sorted(l, key=lambda x: x[0], reverse=True)
            if reranked[0][0] < 0.5:
                continue
            reranked = [x[1] for x in reranked]
            cchunk = copy.deepcopy(topklists[chunkidx])
            cchunk['reranked'] = reranked
            rerankedlists.append(cchunk)
        return rerankedlists
            
if __name__ == '__main__':
    r = ReRanker()
    print(r.rerank([{"chunk": {"chunk": "Russia", "surfacelength": -1, "class": "entity", "surfacestart": -1}, "topkmatches": [["Q159", "Russia"], ["Q3772566", "Russia"], ["Q4350653", ", Russia"], ["Q21193357", "in Russia"], ["Q18600282", "in Russia"], ["Q2477732", "Russia"], ["Q24058892", "Russia"], ["Q4165777", "in Russia"], ["Q4504164", "Russia"], ["Q182648", "Russia"], ["Q23890440", "Russia"], ["Q7381938", "Russia"], ["Q17287317", "in Russia"], ["Q3708651", "Russia"], ["Q6168351", "Russia"], ["Q2624171", "Russia"], ["Q104717", "Russia"], ["Q20657737", "Russia"], ["Q42195226", "Russia"], ["Q42195225", "Russia"], ["Q17287321", "in Russia"], ["Q1401527", "Russia"], ["Q3537636", "Russia"], ["Q28155299", "Shinty in Russia"], ["Q30595979", "Uzbeks in Russia"], ["Q30601289", "Category:Neighborhoods in Russia"], ["Q30644595", "Category:ESports in Russia"], ["Q30685173", "Category:Counts of Russia"], ["Q30806888", "Category:Welfare in Russia"], ["Q32901003", "Category:Towns in Russia"]], "class": "entity"}], "who is the president of Russia ?"))
