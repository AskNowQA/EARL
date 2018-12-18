#!/usr/bin/python

import json,csv,random,time,sys,string
import numpy as np
from keras.models import  model_from_json
from keras.preprocessing import sequence
from keras.preprocessing.text import Tokenizer

random.seed(time.time())

class ErPredictor:
    def __init__(self):
        print "Er Predictor Initializing"
        try:
            data = []
            with open('../data/word_to_id.json') as f:
                data = json.load(f)
            self.word_to_id = data[0]
            json_file = open('../data/ER_model.json', 'r')
            loaded_model_json = json_file.read()
            json_file.close()
            self.loaded_model = model_from_json(loaded_model_json)
            self.loaded_model.load_weights("../data/ER_wights.h5")
            print("Loaded ER model from disk")
        except Exception,e:
            print e
            sys.exit(1)
        print "Er Predictor Initialized"


    def erPredict(self, chunks):
        erpredictions = []
        combinedchunks = []
        for chunk in chunks:
            wordlist = []
            surfacestart = chunk[0][2]
            for word in chunk:
                wordlist.append(word[0])
                surfacelength = word[2]+word[3] - surfacestart
            wordlist = ' '.join(wordlist)
            combinedchunks.append((wordlist,surfacestart,surfacelength))
             
        for chunk in combinedchunks:
            chunkwords = chunk[0].translate(None, string.punctuation)
            tmp = []
            for w in chunkwords.split(" "):
                if w not in self.word_to_id:
                    tmp.append(0)
                else:
                    tmp.append(self.word_to_id[w])
            tmp_padded = sequence.pad_sequences([tmp], maxlen=500)
            prediction = self.loaded_model.predict(np.array([tmp_padded][0]))[0][0]
            if prediction < 0.5:
                erpredictions.append({'chunk':chunkwords, 'surfacestart': chunk[1], 'surfacelength': chunk[2] , 'class':'relation'})
            else:
                erpredictions.append({'chunk':chunkwords, 'surfacestart': chunk[1], 'surfacelength': chunk[2] , 'class':'entity'})
        return erpredictions

if __name__=='__main__':
    e = ErPredictor()
    #print e.erPredict(['There', 'people', 'world', 'better', 'place', 'me.'])
    #print e.erPredict([[('Who', 'S-NP', 0, 3)], [('the', 'B-NP', 7, 3), ('parent', 'I-NP', 11, 6), ('organisation', 'E-NP', 18, 12)], [('Barack', 'B-NP', 34, 6), ('Obama', 'E-NP', 41, 5)], [('is', 'S-VP', 4, 2)]])
    print e.erPredict([[('licensor', 'S-NP', 0, 8)], [('teleserial', 'B-NP', 8, 10)], [('Obama', 'B-NP', 18, 12)]])

