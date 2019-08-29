#!/usr/bin/python

from annoy import AnnoyIndex
from sets import Set
from flask import request
from flask import Flask
from gevent.pywsgi import WSGIServer
from elasticsearch import Elasticsearch
import gensim
import numpy as np
import json,sys
import random

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)


def ConvertVectorSetToVecAverageBased(vectorSet, ignore = []):
    if len(ignore) == 0:
        return np.mean(vectorSet, axis = 0)
    else:
        return np.dot(np.transpose(vectorSet),ignore)/sum(ignore)


print "TextMatch initializing, loading word2vec"
try:
    es = Elasticsearch()
    model = gensim.models.KeyedVectors.load_word2vec_format('../data/lexvec.commoncrawl.300d.W.pos.vectors')
    print("loded word2vec, loading relation labels")
    labelhash = {}
    cache = {}
    f = open('../data/wikidatareluri.json')
    s = f.read()
    labelhash = json.loads(s)
    numberlabelhash = {}
    t = AnnoyIndex(300, 'angular') #approx nearest neighbour search lib
    count = 0
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
        numberlabelhash[count] = urls
        count += 1
    t.build(10)
    print("loaded relation labels, created annoy index, loading fastext")
    fasttextmodel = gensim.models.KeyedVectors.load_word2vec_format('../data/fasttext-wiki-news-subwords-300')
    print("loaded fastext")
except Exception,e:
    print e
    sys.exit(1)            
print "TextMatch initialized"


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

@app.route('/ftwv', methods=['POST'])
def ftwv():
    d = request.get_json(silent=True)
    chunk = d['chunk'] 
    phrase_1 = chunk.split(" ")
    vw_phrase_1 = []
    for phrase in phrase_1:
        try:
            # print phrase
            vw_phrase_1.append(fasttextmodel.word_vec(phrase))
        except:
            # print traceback.print_exc()
            continue
    if len(vw_phrase_1) == 0:
        return json.dumps(300*[0.0])
    v_phrase = ConvertVectorSetToVecAverageBased(vw_phrase_1)
    return json.dumps(v_phrase.tolist())

@app.route('/textMatch', methods=['POST'])
def textMatch():
    pagerankflag = False
    d = request.get_json(silent=True)
    if 'pagerankflag' in d:
        pagerankflag = d['pagerankflag']
    chunks = d['chunks']
    matchedChunks = []
    for chunk in chunks:
         if chunk['class'] == 'entity':
             res = es.search(index="wikidatalabelindex01", doc_type="records", body={"query":{"multi_match":{"query":chunk['chunk'],"fields":["wikidataLabel"]}},"size":200})
             _topkents = []
             topkents = []
             for record in res['hits']['hits']:
                 _topkents.append((record['_source']['uri'],record['_source']['edgecount']))
             if pagerankflag:
                 _topkents =  sorted(_topkents, key=lambda k: k[1], reverse=True)
             for record in _topkents:
                 if len(topkents) >= 30:
                     break
                 if record[0] in topkents:
                     continue
                 else:
                     topkents.append(record[0])
             matchedChunks.append({'chunk':chunk, 'topkmatches': topkents, 'class': 'entity'})
                 
         if chunk['class'] == 'relation':
             phrase = chunk['chunk']
             if phrase not in cache:
                 print "%s not in cache"%phrase
                 results = []
                 max_score = 0
                 uris = []
                 results = t.get_nns_by_vector(list(labeltovec(phrase)),100)
                 for id in results:
                     uris +=  numberlabelhash[id]
                 print(uris)
                 seen = set()
                 seen_add = seen.add
                 uriarray = [uri for uri in uris if not (uri in seen or seen_add(uri))][:30]
                 print(uriarray)
                 cache[phrase] = uriarray
                 matchedChunks.append({'chunk':chunk, 'topkmatches': uriarray, 'class': 'relation'})
             else:
                 print "%s in cache"%phrase
                 matchedChunks.append({'chunk':chunk, 'topkmatches': cache[phrase], 'class': 'relation'})
                        
    return json.dumps(matchedChunks)

if __name__ == '__main__':
    http_server = WSGIServer(('', int(sys.argv[1])), app)
    http_server.serve_forever()
                          
                     


#if __name__ == '__main__':
#    t = TextMatch()
    #print t.textMatch([{'chunk': 'Who', 'surfacelength': 3, 'class': 'entity', 'surfacestart': 0}, {'chunk': 'the parent organisation', 'surfacelength': 23, 'class': 'relation', 'surfacestart': 7}, {'chunk': 'Barack Obama', 'surfacelength': 12, 'class': 'entity', 'surfacestart': 34}, {'chunk': 'is', 'surfacelength': 2, 'class': 'relation', 'surfacestart': 4}])
#    print t.textMatch([{"chunk": "India", "surfacelength": 5, "class": "entity", "surfacestart": 0}])
