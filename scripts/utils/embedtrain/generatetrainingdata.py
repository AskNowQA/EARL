import sys,os,json,re,urllib2,random
from elasticsearch import Elasticsearch
import torch

es = Elasticsearch()

dlcqtrain = json.loads(open('LC-QuAD2.0/dataset/train.json').read())
dquerytrain = json.loads(open('embedsimpletrain1.json').read())

def getembedding(entid):
    entityurl = '<http://www.wikidata.org/entity/'+entid+'>'
    res = es.search(index="wikidataembedsindex01", body={"query":{"term":{"key":{"value":entityurl}}}})
    try:
        embedding = [float(x) for x in res['hits']['hits'][0]['_source']['embedding']]
        return embedding
    except Exception as e:
        print(e)
        return None
    return None


trainingdata = []
for gold,query in zip(dlcqtrain,dquerytrain):
    try:
        if gold['uid'] != query[0]:
            print('uid mismatch')
            sys.exit(1)
        query = query[1]
        if len(query) == 0:
            continue
        goldents = re.findall( r'wd:([Q][0-9]*)', gold['sparql_wikidata'])
        question = gold['question']
        for chunk in query:
            question = question.replace(chunk['chunk']['chunk'], "")
        question = re.sub(r"[^a-zA-Z0-9]+", ' ', question)
        req = urllib2.Request('http://localhost:8887/ftwv')
        req.add_header('Content-Type', 'application/json')
        inputjson = {'chunks':[question]}
        response = urllib2.urlopen(req, json.dumps(inputjson))
        embedding = json.loads(response.read().decode('utf8'))[0]
        questionembedding = embedding
        #paraphrased_question = gold['paraphrased_question']
        #req = urllib2.Request('http://localhost:8887/ftwv')
        #req.add_header('Content-Type', 'application/json')
        #inputjson = {'chunks':[paraphrased_question]}
        #response = urllib2.urlopen(req, json.dumps(inputjson))
        #embedding = json.loads(response.read().decode('utf8'))[0]
        #paraphrased_questionembedding = embedding
        true = []
        false = []
        for chunk in query:
            for idx,entid in enumerate(chunk['topkmatches']):
                embedding = getembedding(entid)
                if embedding:
                    if entid in goldents:
                        if len(question) > 0 and len(question) < 200:
                            true.append([entid,idx,embedding,question,questionembedding,1.0])
                        #if len(paraphrased_question) > 0 and len(paraphrased_question) < 200:
                        #    trainingdata.append([entid,idx,embedding,paraphrased_question,paraphrased_questionembedding,1.0])
                    else:
                        if len(question) > 0 and len(question) < 200:
                            false.append([entid,idx,embedding,question,questionembedding,0.0])
                        #if len(paraphrased_question) > 0 and len(paraphrased_question) < 200:
                        #    trainingdata.append([entid,idx,embedding,paraphrased_question,paraphrased_questionembedding,0.0])
        trainingdata += true
        trainingdata += [random.choice(false) for i in range(len(true)) ] 
    except Exception as e:
        print(e)

f = open('embedsimpletrainvectors1.json','w')
f.write(json.dumps(trainingdata))
f.close()
