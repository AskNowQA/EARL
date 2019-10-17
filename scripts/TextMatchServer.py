#!/usr/bin/python

from annoy import AnnoyIndex
from flask import request
from flask import Flask
from gevent.pywsgi import WSGIServer
import gensim
import numpy as np
import json,sys
import random
import copy

app = Flask(__name__)


def ConvertVectorSetToVecAverageBased(vectorSet, ignore = []):
    if len(ignore) == 0:
        return np.mean(vectorSet, axis = 0)
    else:
        return np.dot(np.transpose(vectorSet),ignore)/sum(ignore)


print("TextMatch initializing, loading fastext")
try:
    fastextmodel = gensim.models.KeyedVectors.load_word2vec_format('../data/fasttext-wiki-news-subwords-300')
    print("loded fastext, loading relation labels")
    labelhash = {}
    cache = {}
    f = open('../data/wikidatareluri.json')
    s = f.read()
    labelhash = json.loads(s)
    numberlabelhash = {}
    t = AnnoyIndex(300, 'angular') #approx nearest neighbour search lib
    count = 0
    for _label,urls in labelhash.items():
        labeltokens = _label.split(" ")
        vw_label = []
        for token in labeltokens:
            try:
                # print phrase
                vw_label.append(fastextmodel.word_vec(token.lower()))
            except:
                # print traceback.print_exc()
                continue
        if len(vw_label) == 0:
            continue
        v_label = ConvertVectorSetToVecAverageBased(vw_label)
        t.add_item(count,list(v_label))
        numberlabelhash[count] = {'label':_label,'urls':urls}
        count += 1
    t.build(10)
    print("loaded relation labels, created annoy index")
except Exception as e:
    print(e)
    sys.exit(1)            
print("TextMatch initialized")


def labeltovec(_phrase_1):
    phrase_1 = _phrase_1.split(" ")
    vw_phrase_1 = []
    for phrase in phrase_1:
        try:
            # print phrase
            vw_phrase_1.append(fastextmodel.word_vec(phrase.lower()))
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
            vw_phrase_1.append(fastextmodel.word_vec(phrase.lower()))
        except:
            # print traceback.print_exc()
            continue
    for phrase in phrase_2:
        try:
            vw_phrase_2.append(fastextmodel.word_vec(phrase.lower()))
        except Exception as e:
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
            vw_phrase_1.append(fastextmodel.word_vec(phrase))
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
         if chunk['class'] == 'relation':
             tempchunk = copy.deepcopy(chunk)
             phrase = tempchunk['chunk']
             if phrase not in cache:
                 print("%s not in cache"%phrase)
                 results = []
                 max_score = 0
                 uris = []
                 results = t.get_nns_by_vector(list(labeltovec(phrase)),10, include_distances = True)
                 print(phrase, results)
                 for id,distance in zip(results[0],results[1]):
                     uris.append({'inputlabel': phrase, 'matchedlabel':numberlabelhash[id]['label'], 'uris': numberlabelhash[id]['urls'], 'distance': distance})
                 seen = set()
                 #seen_add = seen.add
                 #uriarray = [uri for uri in uris if not (uri in seen or seen_add(uri))]
                 cache[phrase] = uris
                 tempchunk['topkmatches'] = uris
                 matchedChunks.append(tempchunk)
             else:
                 print("%s in cache"%phrase)
                 tempchunk['topkmatches'] = cache[phrase]
                 matchedChunks.append(tempchunk)
                        
    return json.dumps(matchedChunks)

if __name__ == '__main__':
    http_server = WSGIServer(('', int(sys.argv[1])), app)
    http_server.serve_forever()
