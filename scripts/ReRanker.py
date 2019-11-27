# /usr/bin/python

import numpy as np
from elasticsearch import Elasticsearch
import urllib2,copy,json,sys,torch,itertools
from numpy import dot
import traceback
from numpy.linalg import norm

device = torch.device('cuda')

class ReRanker:
    def __init__(self):
        self.es = Elasticsearch()
        print "ReRanker initializing"
        try:
            N, D_in, H1, H2, H3, H4, D_out = 100, 500, 300, 100, 50, 10, 1
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
            self.model.load_state_dict(torch.load('../data/jointembedentreranker0.1145.model'))
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

    def getmeanrank(self, combination, listoflistofentities):
        ranktot = 0
        for uri1 in combination:
            found = False
            for l in listoflistofentities:
                if found:
                    continue
                for idx,uri2 in enumerate(l):
                    if uri1 == uri2:
                        ranktot += idx
                        found = True
                        break
        ranktot /= float(len(listoflistofentities))
        return ranktot

    def getconnectivity(self, chunkembeddings, chunkindex, entid, embedding):
        bestdot = -1
        for qchunkindex,qentities in chunkembeddings.items():
            if chunkindex == qchunkindex:
                continue
            for qentid,qembedding in qentities.items():
                queryrel = np.asarray(qembedding) - np.asarray(embedding)
                matchedrels = self.t.get_nns_by_vector(queryrel, 10, include_distances = True)
                if matchedrels[1][0] > bestdot:
                    bestdot = matchedrels[1][0]
                matchedrels = self.t.get_nns_by_vector(np.negative(queryrel), 10, include_distances = True)
                if matchedrels[1][0] > bestdot:
                    bestdot = matchedrels[1][0]
        return [bestdot]

    def rerank(self, topklists, nlquery):
        rerankedlists = []
        questionembedding = self.getsentenceembedding(nlquery)
        chunkembeddings = {}
        for chunkindex,chunk in enumerate(topklists):
            for idx,entid in enumerate(chunk['topkmatches']):
                embedding = self.getentityembedding(entid)
                if not embedding:
                    continue
                chunkembeddings[entid] = embedding
        listoflistofentities = [x['topkmatches']  for x in topklists]
        inputfeatures = []
        entitytuples = []
        if len(topklists) > 3:
            return []
        for combination in itertools.product(*listoflistofentities):
            print(combination)
            meanvector = None
            vectors = []
            try:
                vectors = [chunkembeddings[x] for x in  list(combination)]
                print(vectors)
            except Exception as e:
                print(e)
                continue
            if len(topklists) < 2:
                meanvector = vectors[0]
            else:
                meanvector = list(np.mean(np.array(vectors), axis=0))
            inputfeatures.append(meanvector+questionembedding)
            entitytuples.append(combination)
        x = torch.FloatTensor(inputfeatures).to(device)
        preds = self.model(x).to(device).reshape(-1).cpu().detach().numpy()
        l = [(float(p),u) for p,u in zip(preds, entitytuples)]
        reranked = sorted(l, key=lambda x: x[0], reverse=True)
        reranked = [x[1] for x in reranked]
        #cchunk = copy.deepcopy(chunk)
        #cchunk['reranked'] = reranked
        rerankedlists = reranked
        return rerankedlists
            
if __name__ == '__main__':
    r = ReRanker()
    print(r.rerank([{"chunk": {"chunk": "India", "surfacelength": -1, "class": "entity", "surfacestart": -1}, "topkmatches": ["Q1488929", "Q17055962", "Q22043425", "Q11157534", "Q16578519", "Q36548019", "Q274592", "Q15975440", "Q16429066", "Q50755762", "Q3624238", "Q5802812", "Q39542602", "Q668", "Q23642847", "Q17055987", "Q17014026", "Q2060630", "Q1936198", "Q39611746", "Q39457540", "Q47586501", "Q1963604", "Q6019237", "Q6019242", "Q6019245", "Q37186648", "Q6866034", "Q6866064", "Q712499"], "class": "entity"}], "who is the president of india ?"))
#    print(r.rerank([{"chunk": {"chunk": "India", "surfacelength": -1, "class": "entity", "surfacestart": -1}, "topkmatches": ["Q1488929"], "class": "entity"}], "who is the president of india ?"))
    #print(r.rerank([{u'chunk': {u'chunk': u'Russia', u'surfacelength': 6, u'class': u'entity', u'surfacestart': 0}, u'topkmatches': [u'Q159', u'Q3772566', u'Q4350653', u'Q21193357', u'Q18600282', u'Q2477732', u'Q24058892', u'Q4165777', u'Q4504164', u'Q182648', u'Q23890440', u'Q7381938', u'Q17287317', u'Q3708651', u'Q6168351', u'Q2624171', u'Q104717', u'Q20657737', u'Q42195226', u'Q42195225', u'Q17287321', u'Q1401527', u'Q3537636', u'Q28155299', u'Q30595979', u'Q30601289', u'Q30644595', u'Q30685173', u'Q30806888', u'Q32901003'], u'class': u'entity'}, {u'chunk': {u'chunk': u'Vladimir Putin', u'surfacelength': 6, u'class': u'entity', u'surfacestart': 0}, u'topkmatches': [u'Q7747', u'Q19300851', u'Q1498647', u'Q30746096', u'Q1207817', u'Q29577677', u'Q27332322', u'Q4388316', u'Q3023172', u'Q17052997', u'Q50805606', u'Q24957718', u'Q17008022', u'Q5468438', u'Q24957710', u'Q18342268', u'Q28434454', u'Q48840994', u'Q2458166', u'Q50809370', u'Q4246593', u'Q4349227', u'Q17010981', u'Q24957731', u'Q233282', u'Q45023984', u'Q6163912', u'Q27921525', u'Q7938589', u'Q55637192'], u'class': u'entity'}], "Is Vladimir Putin the president of Russia ?"))
    #print(r.rerank([{"chunk": {"chunk": "Robert Zemeckis", "surfacelength": -1, "class": "entity", "surfacestart": -1}, "topkmatches": ["Q187364", "Q8722965", "Q8951889", "Q109331", "Q21065468", "Q1160186", "Q23681360", "Q36951156", "Q91540", "Q17183895", "Q6447592", "Q2661044", "Q2363927", "Q230552", "Q52814646", "Q25361103", "Q379873", "Q26857995", "Q10916729", "Q23767052", "Q91558", "Q8897633", "Q19967522", "Q224225", "Q3434382", "Q18536001", "Q27793310", "Q33563636", "Q6110081", "Q7341175"], "class": "entity"}, {"chunk": {"chunk": "Forest Gump", "surfacelength": -1, "class": "entity", "surfacestart": -1}, "topkmatches": ["Q5618227", "Q5618229", "Q1554518", "Q5618237", "Q50357429", "Q5514813", "Q23035371", "Q3301643", "Q2411812", "Q37556041", "Q27050096", "Q134773", "Q2917935", "Q5365088", "Q22034107", "Q1345707", "Q52442489", "Q552213", "Q342307", "Q4778916", "Q5618235", "Q5039694", "Q16196037", "Q3077690", "Q55236297", "Q970822", "Q22655521", "Q20362751", "Q24099971", "Q46249531"], "class": "entity"}], "Is Robert Zemeckis is the director of The Forest Gump"))
