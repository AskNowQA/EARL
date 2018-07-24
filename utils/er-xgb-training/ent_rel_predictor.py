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

entities_f = 'entity_sub.org'
reln_f = 'relations.org'
glove_word_vecs = './glove_wiki.bin'
model_j = 'models/er.json'
model_wgt = 'models/er.h5'
rdf2vec_pretrained = 'DB2Vec_sg_500_5_5_15_4_500'
nf_phrases = []
f_phrases = []
def w_categorical_crossentropy(y_true, y_pred, weights):

    nb_cl = len(weights)
    final_mask = K.zeros_like(y_pred[:, 0])
    y_pred_max = K.max(y_pred, axis=1)
    y_pred_max = K.expand_dims(y_pred_max, 1)
    y_pred_max_mat = K.equal(y_pred, y_pred_max)
    for c_p, c_t in product(range(nb_cl), range(nb_cl)):

        final_mask += (K.cast(weights[c_t, c_p],K.floatx()) * K.cast(y_pred_max_mat[:, c_p] ,K.floatx())* K.cast(y_true[:, c_t],K.floatx()))
    return K.categorical_crossentropy(y_pred, y_true) * final_mask

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


def get_glove_vec(word, corpus_word_vecs):

    try:
        return corpus_word_vecs[word]
    except KeyError:
        #nf_words.append(word)
        return np.random.uniform(-0.01, 0.01, 300)


def get_phrase_vector(phrase, word_vecs):

    out_vec = np.zeros((300))
    for word in phrase:
        out_vec = np.add(out_vec, get_glove_vec(word, word_vecs))

    return np.divide(out_vec, len(phrase))

def get_rdf_vecs(rdf2vec_model, phrase):

    #rdf_vecs = np.zeros((len(phrases), 500))
    #phrases = []
    prob_phrase_rel = ''.join(x for x in phrase.title() if not x.isspace())
    prob_phrase_rel = 'dbo:'+prob_phrase_rel[0].lower() + prob_phrase_rel[1:]

    prob_phrase_entity = 'dbr:'+phrase.replace(' ', '_')

    try:
        out_vec = rdf2vec_model[prob_phrase_entity]
        f_phrases.append(prob_phrase_entity)
    except KeyError:
        try:
            out_vec = rdf2vec_model[prob_phrase_rel]
            f_phrases.append(prob_phrase_rel)
        except KeyError:
            out_vec = np.random.uniform(-0.25, 0.25, 500)
            nf_phrases.append(phrase)

    return out_vec


def get_rdf_vecs_phrases(phrases, rdf2vec_model, idx2char_dict):

    print "Testing phrases rev dictionary:"
    print phrases[0]
    
    phrases = [[idx2char_dict[char] for char in phrase] for phrase in phrases]
    phrases = [''.join(phrase) for phrase in phrases]
    print "Printing joint phrases:"
    print phrases[0]

    phrases = [get_rdf_vecs(rdf2vec_model, phrase) for phrase in phrases]

    return np.array(phrases)



def test_phraser(phrase, word_vecs):
    out_vec = np.zeros((300))

    for word in phrase:
        print word
        out_vec = np.add(out_vec, get_glove_vec(word, word_vecs))

    print "Average from opr"
    print out_vec/len(phrase)
    print "Testing the averaging"
    print np.add(get_glove_vec(phrase[0], word_vecs), get_glove_vec(phrase[1], word_vecs))/2

def ent_rel_pred_nn(cv_dat, drop, max_len, embedding_length, rdf2vec_model, rev_char_dict):
    
    print "We are into the training block"

    train_x, train_y, test_x, test_y = cv_dat
    print train_x.shape, test_x.shape
    print "getting validation data"
    train_x, val_x, train_y, val_y = train_test_split(train_x, train_y, test_size=0.1, random_state=666, stratify=train_y)
    
    print "Validation shapes:" + str(val_x.shape)
    print "Data distributions:"
    print Counter([np.argmax(a) for a in train_y])
    print Counter([np.argmax(a) for a in test_y])
    print Counter([np.argmax(a) for a in val_y])
 
    #get the rdf2vec_vectors for all
    train_rdf2vec = get_rdf_vecs_phrases(train_x, rdf2vec_model, rev_char_dict)
    val_rdf2vec = get_rdf_vecs_phrases(val_x, rdf2vec_model, rev_char_dict)

    train_x = np.array(sequence.pad_sequences(train_x, maxlen=max_len), dtype=np.int)
    test_x = np.array(sequence.pad_sequences(test_x, maxlen=max_len), dtype=np.int)
    val_x = np.array(sequence.pad_sequences(val_x, maxlen=max_len), dtype=np.int)
    print "Training the neural net now"
    print train_x[0]


    #define the neural net model

    input_vec = Input(shape=(max_len,), dtype='int32', name="inp_vec")
    embedded_l = Embedding(embedding_length, 128, mask_zero=False,
                                    input_length=max_len, trainable=True)(input_vec)

    lstm_1 = LSTM(128, return_sequences=False, dropout_W=0.3, dropout_U=0.3)(embedded_l)
    dense_1 = Dense(512, activation='tanh', kernel_initializer="glorot_uniform")(lstm_1)
    drop_l = Dropout(drop)(dense_1)
    dense_2 = Dense(256, activation='tanh', kernel_initializer="glorot_uniform")(drop_l)
    drop_l_2 = Dropout(drop)(dense_2)
    #batch_norm = BatchNormalization()(drop_l)

    output_l = Dense(2, activation='softmax', name = "output_layer")(drop_l_2)
    output_rdf2vec = Dense(500, activation='softmax', name= "output_layer_2")(drop_l_2)


    model = Model([input_vec], output=[output_l, output_rdf2vec] )

    adam = Adam(lr=0.0001)


    #weighted categorical crooss entropy

    w_array = np.ones((2, 2))
    w_array[0, 1] = 1.2

    ncce = functools.partial(w_categorical_crossentropy, weights=w_array)
    ncce.__name__ ='w_categorical_crossentropy'
    model.compile(loss='categorical_crossentropy', optimizer=adam, metrics=['accuracy'], loss_weights={'output_layer': 1., 'output_layer_2': 0.4})

    earlystop = EarlyStopping(monitor='val_output_layer_loss', min_delta=0.0001, patience=3,
                          verbose=1, mode='auto')


    callbacks_list = [earlystop]
    print model.summary()
    model.fit([train_x], [train_y, train_rdf2vec], batch_size=128, epochs=30,
              verbose=1, shuffle=True, callbacks=callbacks_list, validation_data=[[val_x], [val_y, val_rdf2vec]])

    model_json = model.to_json()
    with open(model_j, "w") as json_file:
        json_file.write(model_json)
    model.save_weights(model_wgt)
    print "Saved the model to disk."

    test_predictions = model.predict([test_x], verbose=False)
    test_pred = [np.argmax(pred) for pred in test_predictions[0]]
    test_y = [np.argmax(label) for label in test_y]

    f1_value = f1_score(test_y, test_pred, average="macro")
    print f1_value
    return f1_value

def run_nn():
    print "running the models"

    #load relations and entities
    relations = (pd.read_table(reln_f))
    entities = (pd.read_table(entities_f))
    relations['label'] = 0
    entities['label'] = 1
    #load rdf2vec_model
    rdf2vec = word2vec.Word2Vec.load(rdf2vec_pretrained)



    #word_vectors = KeyedVectors.load_word2vec_format(glove_word_vecs, binary=False)
    #process data
    x_dat = np.concatenate((np.array(relations['phrase']), np.array(entities['phrase'])), axis=0)
    print x_dat[1]
    #print get_phrase_vector(clean_str(x_dat[1]), word_vectors)
    print "testing the phraser"
    #test_phraser(x_dat[1].split(),word_vectors)
    X = ([[char for char in phr] for phr in x_dat])
    print X[0:10]
    max_len = np.max([len(val) for val in X])
    print max_len
    
    #x_dat = [get_phrase_vector(phr.split(), word_vecs=word_vectors) for phr in x_dat]
    print X[1]
    char_vocab = defaultdict(float)
    for phr in X:
        for char in phr:
            char_vocab[char] += 1
    char_dict = dict(zip(char_vocab.keys(),range(0,len(char_vocab))))
    char_dict_rev = {v: k for k, v in char_dict.iteritems()}
 
    print char_dict_rev[1]
    X = np.array([[char_dict[char] for char in phr] for phr in X])
    np.save('char_dict.npy',char_dict)
    print X[1]
    print char_dict['t']
    y_dat = np_utils.to_categorical(np.concatenate((np.array(relations['label']), np.array(entities['label'])), axis=0))
    print y_dat[1], y_dat[-1]
    print y_dat.shape
    print "loading data..."
    #X = np.array(np.load('x_dat.npy'))
    #y_dat = np.load('y_dat.npy')
    print "Getting the CV data"
    #skf = StratifiedKFold(n_splits=10, random_state = 666, shuffle = True )
    
    x_train, x_test, y_tr, y_te = train_test_split(X, y_dat, test_size=0.15, stratify=y_dat)
    
    #cv_dat = x_train, y_tr, x_test, y_te
    #f1_val = ent_rel_pred_nn(cv_dat, 0.6, max_len, len(char_dict), rdf2vec, char_dict_rev)
    #print f1_val
    x_train =  get_rdf_vecs_phrases(x_train, rdf2vec, char_dict_rev)
    x_test = get_rdf_vecs_phrases(x_test, rdf2vec, char_dict_rev)

    print "entities/relations not found"
    out_nf = open('not_found_ers.txt', 'w')
    for word in nf_phrases:
        out_nf.write(word + '\n')

    out_nf.close()
 

    out_f = open('phrases_present.txt','w')
    for word in f_phrases:
	out_f.write(word + '\n')

    out_f.close()
    
    #np.save('x_dat.npy',X)
    #np.save('y_dat.npy',y_dat)

    scores = 0.0
    """
    for train_index, test_index in skf.split(X, y_dat):
        print "Generating datasets for cv"
        y_dat = np_utils.to_categorical(y_dat)
        
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y_dat[train_index], y_dat[test_index]



	print y_train[0]
        cv_dat = X_train, y_train, X_test, y_test
        print "training the model now ..."
        scores = scores + ent_rel_pred_nn(cv_dat, 0.5)
    """
    print "Done training the model."
    #print scores/10


if __name__ == '__main__':
    run_nn()

