#!/usr/bin/python

from sets import Set
from flask import request
from flask import Flask
from gevent.pywsgi import WSGIServer
from elasticsearch import Elasticsearch
#import gensim
from model import Model #lexvec
import numpy as np
import json,sys

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)

#model = gensim.models.KeyedVectors.load_word2vec_format('../data/lexvec.commoncrawl.ngramsubwords.300d.W.pos.bin')
model = Model('../data/lexvec.commoncrawl.ngramsubwords.300d.W.pos.bin')
print "CosineServer initialized"

def ConvertVectorSetToVecAverageBased(vectorSet, ignore = []):
    if len(ignore) == 0:
        return np.mean(vectorSet, axis = 0)
    else:
        return np.dot(np.transpose(vectorSet),ignore)/sum(ignore)


def phrase_similarity(_phrase_1, _phrase_2):
    phrase_1 = _phrase_1.split(" ")
    phrase_2 = _phrase_2.split(" ")
    vw_phrase_1 = []
    vw_phrase_2 = []
    for phrase in phrase_1:
        try:
            # print phrase
            vw_phrase_1.append(model.word_rep(phrase.lower()))
        except:
            # print traceback.print_exc()
            continue
    for phrase in phrase_2:
        try:
            vw_phrase_2.append(model.word_rep(phrase.lower()))
        except Exception,e:
            continue
    if len(vw_phrase_1) == 0 or len(vw_phrase_2) == 0:
        return 0
    v_phrase_1 = ConvertVectorSetToVecAverageBased(vw_phrase_1)
    v_phrase_2 = ConvertVectorSetToVecAverageBased(vw_phrase_2)
    cosine_similarity = np.dot(v_phrase_1, v_phrase_2) / (np.linalg.norm(v_phrase_1) * np.linalg.norm(v_phrase_2))
    return cosine_similarity

@app.route('/cosine', methods=['POST'])
def cosine():
    pagerankflag = False
    d = request.get_json(silent=True)
    phrase1 = d['phrase1']
    phrase2 = d['phrase2']
    score = phrase_similarity(phrase1, phrase2)
    return json.dumps({'score': str(score)})

if __name__ == '__main__':
    http_server = WSGIServer(('', int(sys.argv[1])), app)
    http_server.serve_forever()
