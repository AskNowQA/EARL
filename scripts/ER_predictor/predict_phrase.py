#Script for predicting a phrase as Entity or relation(predicate)
#Run the script with the phrase as a parameter.
import pandas as pd
import numpy as np
import re
from collections import defaultdict
from keras.engine import Input
from keras.engine import Model
from keras.layers import Dense, Dropout, Embedding, LSTM, Bidirectional, Conv1D, GlobalAveragePooling1D, GlobalMaxPooling1D
from keras.layers.merge import Concatenate, Add, concatenate
from keras.preprocessing import sequence
from keras import backend as K
from keras.layers.core import Lambda
from keras.optimizers import Adam
from sklearn.metrics import accuracy_score
import cPickle
import functools
from itertools import product
from keras.callbacks import EarlyStopping
from gensim.models import word2vec
from sklearn.model_selection import KFold
from collections import defaultdict
from collections import Counter
from keras.utils import np_utils
from sklearn.metrics import f1_score
from keras.models import model_from_json
from gensim import models
import gensim
from keras.layers.normalization import BatchNormalization
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
import functools
from sklearn.model_selection import StratifiedKFold
from gensim.models.keyedvectors import KeyedVectors
import sys
import json

model_j = 'EARL/models/er.json'
model_wgt = 'EARL/models/er.h5'
max_len = 283
#lc_quad_j = './lcQuad.json'

#load the model
json_file = open(model_j, 'r')
model_json = json_file.read()
json_file.close()
model = model_from_json(model_json)
model.load_weights(model_wgt)

print("Loaded model from disk")

adam = Adam(lr=0.0001)
model.compile(loss='categorical_crossentropy', optimizer=adam, metrics=['accuracy'])


def clean_str(string, TREC=False):
    """
    Tokenization/string cleaning for all datasets except for SST.
    Every dataset is lower cased except for TREC
    """
    string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
    string = re.sub(r"\'s", " \'s", string)
    string = re.sub(r"\'ve", " \'ve", string)
    string = re.sub(r"n\'t", " n\'t", string)
    string = re.sub(r"\'re", " \'re", string)
    string = re.sub(r"\'d", " \'d", string)
    string = re.sub(r"\'ll", " \'ll", string)
    string = re.sub(r",", " , ", string)
    string = re.sub(r"!", " ! ", string)
    string = re.sub(r"\(", " \( ", string)
    string = re.sub(r"\)", " \) ", string)
    string = re.sub(r"\?", " \? ", string)
    string = re.sub(r"\s{2,}", " ", string)
    return string.strip()

def predict_phrase(phrase):
   #load the model
   #preprocess the phrase
   
   #phrase_clean = clean_str(phrase)
   phrase_clean = phrase 
   #load the dictionary
   char_dict = np.load('char_dict.npy').item()
   #phrase_clean = [char for char in phrase_clean]
   #print phrase_clean
   
   phrase_clean = [char_dict[char] for char in phrase_clean]

   #print phrase_clean
   
   #print np.concatenate((np.zeros(max_len-len(phrase_clean)), phrase_clean) )
   prediction = model.predict(np.concatenate((np.zeros((270-len(phrase_clean))), phrase_clean)).reshape(1,270))

   print prediction[0]
   
   pred = np.argmax(prediction[0])

   return 'R' if pred == 0 else 'E'

def predict_cln_phrs(clean_phrase):
   
   tags = []
   print clean_phrase
   for phr in clean_phrase:
        print phr
	tags.append(predict_phrase(phr))
   
   return tags

if __name__ == '__main__':
   #phrase = sys.argv[1:]
   lc_quad_j = sys.argv[1]
   #print phrase
   #predict_phrase(phrase)
   #Read the json file
   #lcquad = json.loads(open(lc_quad_j).read())
   #chunks = [dat['CleanPhrase'] for dat in lcquad['PhraseChunked_LC-QuAD']]


   #for dat in lcquad['PhraseChunked_LC-QuAD']:
   #    dat['E-R-predictor']  = predict_cln_phrs(dat['CleanPhrase'].replace('[','').replace(']','').split(','))

   #print lcquad['PhraseChunked_LC-QuAD'][0]
   #np.save('lcquad.npy',lcquad)
   #with open('lcQuad_ers.json','w') as f:
   #	json.dump(lcquad, f)
   print predict_phrase(list(lc_quad_j))
