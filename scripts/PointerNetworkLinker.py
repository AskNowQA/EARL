from elasticsearch import Elasticsearch
import tensorflow as tf
import numpy as np
import pointer_net
import time,os,sys,json,re,requests
from Vectoriser import Vectoriser
import copy

tf.app.flags.DEFINE_integer("max_input_sequence_len", 3000, "Maximum input sequence length.")
tf.app.flags.DEFINE_integer("max_output_sequence_len", 100, "Maximum output sequence length.")
tf.app.flags.DEFINE_integer("rnn_size", 512, "RNN unit size.")
tf.app.flags.DEFINE_integer("attention_size", 128, "Attention size.")
tf.app.flags.DEFINE_integer("num_layers", 1, "Number of layers.")
tf.app.flags.DEFINE_integer("beam_width", 1, "Width of beam search .")
tf.app.flags.DEFINE_float("learning_rate", 0.001, "Learning rate.")
tf.app.flags.DEFINE_string("test_data", "./a.txt", "Learning rate.")
tf.app.flags.DEFINE_float("max_gradient_norm", 5.0, "Maximum gradient norm.")
tf.app.flags.DEFINE_boolean("forward_only", True, "Forward Only.")
tf.app.flags.DEFINE_string("models_dir", "../data/pointermodelwebqs6/", "Log directory")
tf.app.flags.DEFINE_integer("batch_size", 1, "batchsize")
FLAGS = tf.app.flags.FLAGS

class PointerNetworkLinker():
    def __init__(self):
        print("Initialising PointerNetworkLinker")
        self.forward_only = True
        self.graph = tf.Graph()
        with self.graph.as_default():
            config = tf.ConfigProto()
            config.gpu_options.allow_growth = True
            config.operation_timeout_in_ms=10000
            self.sess = tf.Session(config=config)
        self.build_model()
        print("Initialised PointerNetworkLinker")
    
    
    def build_model(self):
        with self.graph.as_default():
            self.model = pointer_net.PointerNet(batch_size=FLAGS.batch_size,
                        max_input_sequence_len=FLAGS.max_input_sequence_len,
                        max_output_sequence_len=FLAGS.max_output_sequence_len,
                        rnn_size=FLAGS.rnn_size,
                        attention_size=FLAGS.attention_size,
                        num_layers=FLAGS.num_layers,
                        beam_width=FLAGS.beam_width,
                        learning_rate=FLAGS.learning_rate,
                        max_gradient_norm=FLAGS.max_gradient_norm,
                        forward_only=self.forward_only)
            ckpt = tf.train.get_checkpoint_state(FLAGS.models_dir)
            print(ckpt, FLAGS.models_dir)
            if ckpt and tf.train.checkpoint_exists(ckpt.model_checkpoint_path):
                print("Load model parameters from %s" % ckpt.model_checkpoint_path)
                self.model.saver.restore(self.sess, ckpt.model_checkpoint_path)
            self.sess.graph.finalize()

    def merge(self, entitytuple, entdict):
        span = entitytuple[1]
        tempentdict = copy.deepcopy(entdict)
        for k,v in tempentdict.items():
            for entchunk in v:
                entspan = entchunk[1]
                x = range(span[0],span[1]+1)
                y = range(entspan[0],entspan[1]+1)
                if len(set(x).intersection(y)) > 0:
                    if entitytuple in entdict[k]:
                        print("Exact already present, skip")
                        continue
                    print("Merging ", entitytuple, " into ", entdict)
                    entdict[k].append((entitytuple))
        

    def overlap(self,span,entdict):
        for k,v in entdict.items():
            for entchunk in v:
                entspan = entchunk[1]
                x = range(span[0],span[1]+1)
                y = range(entspan[0],entspan[1]+1)
                if len(set(x).intersection(y)) > 0:
                    print("Overlap exists between ",span," and ",entspan)
                    return True
        return False 
                    
    def processentities(self, entities):
        entdict = {}
        clustercount = 0
        for entitytuple in entities:
            entid,span, spanphrase, storedlabel = entitytuple
            if len(entdict) == 0:
                entdict[clustercount] = [entitytuple]
            else:
                if self.overlap(span, entdict):
                    self.merge(entitytuple,entdict)
                else:
                    clustercount += 1
                    entdict[clustercount] =  [entitytuple]
            print("entdict: ",entdict)
        return entdict

    def link(self, vectors):
        print("Entered pointer network linker ...")
        inputs = []
        self.outputs = []
        enc_input_weights = []
        dec_input_weights = []
        maxlen = 0
        questioninputs = []
        enc_input_len = len(vectors)
        if enc_input_len > FLAGS.max_input_sequence_len:
            print("Length too long, skip")
            return []
        for idx,word in enumerate(vectors):
            questioninputs.append(word[0])
        for i in range(FLAGS.max_input_sequence_len-enc_input_len):
            questioninputs.append([0]*1403)
        weight = np.zeros(FLAGS.max_input_sequence_len)
        weight[:enc_input_len]=1
        enc_input_weights.append(weight)
        inputs.append(questioninputs)
        self.test_inputs = np.stack(inputs)
        self.test_enc_input_weights = np.stack(enc_input_weights)
        predicted_ids,outputs = self.model.step(self.sess, self.test_inputs, self.test_enc_input_weights, update=False) 
        print("predicted_ids: ",list(predicted_ids[0][0]))
        entities = []
        for entnum in list(predicted_ids[0][0]):
            if entnum <= 0:
                continue
            wordindex = vectors[entnum-1][0][1401]
            #if wordindex in seen:
            #    continue
            span = vectors[entnum-1][4] # [startindex, endindex]
            spanphrase = vectors[entnum-1][3] # of India
            storedlabel = vectors[entnum-1][2] # India
            entid = vectors[entnum-1][1] #Q668
            entities.append((entid,span, spanphrase, storedlabel))
            print(vectors[entnum-1][0][1401], vectors[entnum-1][0][1402],vectors[entnum-1][0][1400], vectors[entnum-1][1], vectors[entnum-1][2], vectors[entnum-1][3], vectors[entnum-1][4])
        #groupedentities = self.processentities(entities)
        #print("predents: ",groupedentities)
        print("unprocessed predicted ents: ", entities)
        return entities

if __name__ == '__main__':
    v = Vectoriser()
    vectors = v.vectorise("which city in India is located in Tamil Nadu ?")
    p = PointerNetworkLinker()
    entities = p.link(vectors)
    

