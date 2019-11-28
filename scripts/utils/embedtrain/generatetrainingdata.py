import sys,os,json,re,urllib2
from elasticsearch import Elasticsearch
import torch
from numpy import dot
import itertools
import traceback
from numpy.linalg import norm
import numpy as np
from annoy import AnnoyIndex

es = Elasticsearch()
t = AnnoyIndex(200,'dot')
t.load('../../../data/wikiembedrel1.ann')
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

def getjointembedding(chunkembeddings, chunkindex, entid, embedding):
    bestdot = -1
    for qchunkindex,qentities in chunkembeddings.items():
        if chunkindex == qchunkindex:
            continue
        for qentid,qembedding in qentities.items():
            queryrel = np.asarray(qembedding) - np.asarray(embedding) 
            matchedrels = t.get_nns_by_vector(queryrel, 10, include_distances = True)
            if matchedrels[1][0] > bestdot:
                bestdot = matchedrels[1][0]
            matchedrels = t.get_nns_by_vector(np.negative(queryrel), 10, include_distances = True)
            if matchedrels[1][0] > bestdot:
                bestdot = matchedrels[1][0]
    return embedding + [bestdot]


def getmeanrank(combination, listoflistofentities):
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
                 
            

trainingdata = []
c = 0
for gold,query in zip(dlcqtrain,dquerytrain):
    print(c)
    c+= 1
    try:
        if gold['uid'] != query[0]:
            print('uid mismatch')
            sys.exit(1)
        query = query[1]
        if len(query) == 0:
            continue
        goldents = re.findall( r'wd:(.*?) ', gold['sparql_wikidata'])
        question = gold['question']
        questionembedding = None
        if question and len(question) > 0:
            req = urllib2.Request('http://localhost:8887/ftwv')
            req.add_header('Content-Type', 'application/json')
            inputjson = {'chunks':[question]}
            response = urllib2.urlopen(req, json.dumps(inputjson))
            embedding = json.loads(response.read().decode('utf8'))[0]
            questionembedding = embedding
        paraphrased_question = gold['paraphrased_question']
        paraphrased_questionembedding = None
        if paraphrased_question and len(paraphrased_question) > 0:
            req = urllib2.Request('http://localhost:8887/ftwv')
            req.add_header('Content-Type', 'application/json')
            inputjson = {'chunks':[paraphrased_question]}
            response = urllib2.urlopen(req, json.dumps(inputjson))
            embedding = json.loads(response.read().decode('utf8'))[0]
            if not embedding:
                continue
            paraphrased_questionembedding = embedding
        if not questionembedding and not paraphrased_questionembedding:
            continue
        chunkembeddings = {}
        listoflistofentities = []
        for chunkindex,chunk in enumerate(query):
            for idx,entid in enumerate(chunk['topkmatches']):
                embedding = getembedding(entid)
                if not embedding:
                    print("no embedding for %s"%entid)
                    continue
                chunkembeddings[entid] = embedding
            listoflistofentities.append(query[chunkindex]['topkmatches'])
        true = False
        false = False
        if (len(query)) > 3:
            continue
        for combination in itertools.product(*listoflistofentities):
            if true and false:
                break
            meanvector = None
            meanranks = -1
            vectors = [chunkembeddings[x] for x in  list(combination)]
            if len(query) < 2:
                meanvector = vectors[0]
            else:
                meanvector = list(np.mean(np.array(vectors), axis=0))
            meanvector = meanvector+[getmeanrank(combination,listoflistofentities)]
            if set(combination) == set(goldents) and not true:
                print("total match ",combination, goldents)
                true = True
                if len(question) > 0 and len(question) < 200 and questionembedding:
                    trainingdata.append([meanvector,questionembedding,1.0])
                if len(question) > 0 and len(question) < 200 and paraphrased_questionembedding:
                    trainingdata.append([meanvector,paraphrased_questionembedding,1.0])
            elif not false:
                print("bad match ", combination,goldents)
                false = True
                if len(question) > 0 and len(question) < 200 and questionembedding:
                    trainingdata.append([meanvector,questionembedding,0.0]) 
                if len(question) > 0 and len(question) < 200 and paraphrased_questionembedding:
                    trainingdata.append([meanvector,paraphrased_questionembedding,0.0])
    except Exception as e:
        print(e)
        #traceback.print_exc()
        #sys.exit(1)

f = open('embedjointtrainvectors1.json','w')
f.write(json.dumps(trainingdata))
f.close()
