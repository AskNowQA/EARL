#!/usr/bin/python

import numpy as np
import re
from keras.engine import Input
from keras.engine import Model
from keras.layers import Dense, Dropout, Embedding, LSTM, Bidirectional, Conv1D, GlobalAveragePooling1D, GlobalMaxPooling1D
from keras.layers.merge import Concatenate, Add, concatenate
from keras.preprocessing import sequence
from keras import backend as K
from keras.layers.core import Lambda
from keras.optimizers import Adam
from sklearn.metrics import accuracy_score
from keras.callbacks import EarlyStopping
from gensim.models import word2vec
from sklearn.model_selection import KFold
from keras.utils import np_utils
from sklearn.metrics import f1_score
from keras.models import model_from_json
from gensim import models
import gensim
from keras.layers.normalization import BatchNormalization
#from nltk.corpus import stopwords
import sys, string


class ErPredictor:
    def __init__(self):
        print "Er Predictor Initializing"
        try:
            model_j = '../models/er.json'
            model_wgt = '../models/er.h5'
            max_len = 283
            json_file = open(model_j, 'r')
            model_json = json_file.read()
            json_file.close()
            self.model = model_from_json(model_json)
            self.model.load_weights(model_wgt)
            adam = Adam(lr=0.0001)
            self.model.compile(loss='categorical_crossentropy', optimizer=adam, metrics=['accuracy'])
        except Exception,e:
            print e
            sys.exit(1)
        print "Er Predictor Initialized"


    def erPredict(self, chunks):
        erpredictions = []
        for chunk in chunks:
            chunk = chunk.translate(None, string.punctuation)
            char_dict = np.load('../models/char_dict.npy').item()
            chunk_clean = [char_dict[char] for char in chunk]
            prediction = self.model.predict(np.concatenate((np.zeros((270-len(chunk_clean))), chunk_clean)).reshape(1,270))
            pred = np.argmax(prediction[0])
            if pred == 0:
                erpredictions.append({'chunk':chunk, 'class':'relation'})
            else:
                erpredictions.append({'chunk':chunk, 'class':'entity'})
        return erpredictions

if __name__=='__main__':
    e = ErPredictor()
    print e.erPredict(['There', 'people', 'world', 'better', 'place', 'me.'])

