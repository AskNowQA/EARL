import sys,os,json,re,urllib2,random
from elasticsearch import Elasticsearch

es = Elasticsearch()

dlcqtrain = json.loads(open('unifiedtraindeduplicate.json').read())
dquerytrain = json.loads(open('unifiedtraintopkmatches1.json').read())

def getembedding(entid):
    entityurl = '<http://www.wikidata.org/entity/'+entid+'>'
    res = es.search(index="wikidataembedsindex01", body={"query":{"term":{"key":{"value":entityurl}}}})
    try:
        embedding = [float(x) for x in res['hits']['hits'][0]['_source']['embedding']]
        return embedding
    except Exception as e:
        print(entid,' not found')
        return None
    return None


trainingdata = []
count = 0
for gold,query in zip(dlcqtrain,dquerytrain):
    try:
        print(count)
        count += 1
        if gold['id'] != query[0]:
            print('uid mismatch')
            sys.exit(1)
        query = query[1]
        if len(query) == 0:
            continue
        query = query[0]
        goldents = gold['entities']
        question = gold['question']
        req = urllib2.Request('http://localhost:8887/ftwv')
        req.add_header('Content-Type', 'application/json')
        inputjson = {'chunks':[question]}
        response = urllib2.urlopen(req, json.dumps(inputjson))
        embedding = json.loads(response.read().decode('utf8'))[0]
        questionembedding = embedding
        true = []
        false = []
        for chunk in query:
            for idx,entid in enumerate(chunk['topkmatches']):
                embedding = getembedding(entid)
                if embedding:
                    if entid in goldents:
                        if len(question) > 0 and len(question) < 200:
                            true.append([entid,idx,embedding,question,questionembedding,1.0])
                    else:
                        if len(question) > 0 and len(question) < 200:
                            false.append([entid,idx,embedding,question,questionembedding,0.0])
            if len(true) > 0:
                trainingdata += true 
                trainingdata.append( random.choice(false))
    except Exception as e:
        print(e)

f = open('unifiedtrainvectors1.json','w')
f.write(json.dumps(trainingdata))
f.close()
