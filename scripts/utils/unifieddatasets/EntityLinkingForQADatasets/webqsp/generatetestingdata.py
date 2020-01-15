import sys,os,json,re,urllib2,random
from elasticsearch import Elasticsearch
import torch
from numpy import dot
import itertools
import traceback
from numpy.linalg import norm
import numpy as np

es = Elasticsearch()
dlcqtrain = json.loads(open('input/webqsp.test.entities.with_classes.json').read())
dquerytrain = json.loads(open('webqstestout.json').read())

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

def getrelembedding(entityurl):
    res = es.search(index="wikidataembedsindex01", body={"query":{"term":{"key":{"value":entityurl}}}})
    try:
        embedding = [float(x) for x in res['hits']['hits'][0]['_source']['embedding']]
        return embedding
    except Exception as e:
        print(e)
        return None
    return None

def getjointembedding(chunkembeddings, chunkindex, embedding):
    bestdot = -1
    for qchunkindex,qentities in chunkembeddings.items():
        if chunkindex == qchunkindex:
            continue
        for qentid,qembedding in qentities.items():
            dotproduct = np.dot(np.asarray(qembedding),np.asarray(embedding))
            if dotproduct > bestdot:
                bestdot = dotproduct
    return embedding + [bestdot]

trainingdata = []
c = 0
for gold,query in zip(dlcqtrain,dquerytrain):
    print(c)
    c+= 1
    try:
        if gold['question_id'] != query[0]:
            print('uid mismatch')
            sys.exit(1)
        query = query[1]
        if len(query) == 0:
            continue
        goldents = gold['entities']
        question = gold['utterance']
        questionembedding = None
        if question and len(question) > 0:
            req = urllib2.Request('http://localhost:8887/ftwv')
            req.add_header('Content-Type', 'application/json')
            inputjson = {'chunks':[question]}
            response = urllib2.urlopen(req, json.dumps(inputjson))
            embedding = json.loads(response.read().decode('utf8'))[0]
            questionembedding = embedding
        if not questionembedding:
            continue
        chunkembeddings = {}
        listoflistofentities = []
        for chunkindex,chunk in enumerate(query):
            if chunkindex not in chunkembeddings:
                chunkembeddings[chunkindex] = {}
            for idx,entid in enumerate(chunk['topkmatches']):
                embedding = getembedding(entid)
                if not embedding:
                    print("no embedding for %s"%entid)
                    continue
                chunkembeddings[chunkindex][entid] = embedding
            listoflistofentities.append(query[chunkindex]['topkmatches'])
        true = False
        false = False
        if (len(query)) > 3:
            continue
        for chunkidx,listofentities in enumerate(listoflistofentities):
            if true and false:
                continue
            truearr = []
            falsearr = []
            for entidx,entid in enumerate(listofentities):
                entembedding = chunkembeddings[chunkidx][entid]
                vector = getjointembedding(chunkembeddings,chunkidx,entembedding)
                if len(question) > 0 and len(question) < 200 and questionembedding and entid in goldents:
                    truearr.append([vector+[entidx]+questionembedding,1.0])
                if len(question) > 0 and len(question) < 200 and questionembedding and entid not in goldents:
                    falsearr.append([vector+[entidx]+questionembedding,0.0])
            trainingdata += truearr
            trainingdata += random.sample(falsearr, len(truearr))
    except Exception as e:
        print(e)
        #traceback.print_exc()
        #sys.exit(1)

f = open('embedjointtestvectors1.json','w')
f.write(json.dumps(trainingdata))
f.close()
