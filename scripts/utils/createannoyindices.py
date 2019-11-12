#!/usr/bin/python

from annoy import AnnoyIndex
from elasticsearch import Elasticsearch
import gensim
import numpy as np
import json,sys
import random

reload(sys)
sys.setdefaultencoding('utf8')

def ConvertVectorSetToVecAverageBased(vectorSet, ignore = []):
    if len(ignore) == 0:
        return np.mean(vectorSet, axis = 0)
    else:
        return np.dot(np.transpose(vectorSet),ignore)/sum(ignore)


def labeltovec(_phrase_1):
    phrase_1 = _phrase_1.split(" ")
    vw_phrase_1 = []
    for phrase in phrase_1:
        try:
            # print phrase
            vw_phrase_1.append(model.word_vec(phrase.lower()))
        except:
            # print traceback.print_exc()
            continue
    if len(vw_phrase_1) == 0:
        return 300*[0.0]
    v_phrase_1 = ConvertVectorSetToVecAverageBased(vw_phrase_1)
    return v_phrase_1

def phrase_similarity(_phrase_1, _phrase_2):
    phrase_1 = _phrase_1.split(" ")
    phrase_2 = _phrase_2.split(" ")
    vw_phrase_1 = []
    vw_phrase_2 = []
    for phrase in phrase_1:
        try:
            # print phrase
            vw_phrase_1.append(model.word_vec(phrase.lower()))
        except:
            # print traceback.print_exc()
            continue
    for phrase in phrase_2:
        try:
            vw_phrase_2.append(model.word_vec(phrase.lower()))
        except Exception,e:
            continue
    if len(vw_phrase_1) == 0 or len(vw_phrase_2) == 0:
        return 0
    v_phrase_1 = ConvertVectorSetToVecAverageBased(vw_phrase_1)
    v_phrase_2 = ConvertVectorSetToVecAverageBased(vw_phrase_2)
    cosine_similarity = np.dot(v_phrase_1, v_phrase_2) / (np.linalg.norm(v_phrase_1) * np.linalg.norm(v_phrase_2))
    return cosine_similarity

es = Elasticsearch()
model = gensim.models.KeyedVectors.load_word2vec_format('../../data/fasttext-wiki-news-subwords-300')


t = AnnoyIndex(300, 'angular') #approx nearest neighbour search lib
f = open('../../data/wikilabeluridict1.json')
s = f.read()
f.close()
labelhash = json.loads(s)
numberurlhash = {}
count = 0
veccount = 0
for _label,urls in labelhash.iteritems():
    labeltokens = _label.split(" ")
    vw_label = []
    for token in labeltokens:
        try:
            # print phrase
            vw_label.append(model.word_vec(token.lower()))
        except:
            # print traceback.print_exc()
            continue
    if len(vw_label) == 0:
        continue
    v_label = ConvertVectorSetToVecAverageBased(vw_label)
    t.add_item(count,list(v_label))
    numberurlhash[count] = urls
    print(count)
    count += 1
f = open('../../data/types.json')
typearray = json.loads(f.read())
f.close()
for typeid in typearray:
    res = es.search(index="wikidataentitylabelindex01", body={"query":{"term":{"uri": 'http://wikidata.dbpedia.org/resource/'+typeid}},"size":100})
    for record in res['hits']['hits']:
        vw_label = []
        label = record['_source']['wikidataLabel']
        for token in label.split(" "):
            try:
                vw_label.append(model.word_vec(token.lower()))
            except:
                continue
        if len(vw_label) == 0:
            continue
        v_label = ConvertVectorSetToVecAverageBased(vw_label)
        t.add_item(count,list(v_label))
        numberurlhash[count] = ['P31_'+typeid]
        count += 1
        print(count)

t.build(20)
t.save('predtype1.ann')
f = open('predtypeurls1.json','w')
f.write(json.dumps(numberurlhash, indent=4))
f.close()
