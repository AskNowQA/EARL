import sys
import json
from elasticsearch import Elasticsearch
from fuzzywuzzy import fuzz
import urllib2
import re
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from textblob import TextBlob
from itertools import groupby
from numpy import array
from numpy import argmax

torch.manual_seed(1)

postags = ["CC","CD","DT","EX","FW","IN","JJ","JJR","JJS","LS","MD","NN","NNS","NNP","NNPS","PDT","POS","PRP","PRP$","RB","RBR","RBS","RP","SYM","TO","UH","VB","VBD","VBG","VBN","VBP","VBZ","WDT","WP","WP$","WRB"]

def beam_search_decoder(data, k):
	sequences = [[list(), 1.0]]
	# walk over each step in sequence
	for row in data:
		all_candidates = list()
		# expand each current candidate
		for i in range(len(sequences)):
			seq, score = sequences[i]
			for j in range(len(row)):
				candidate = [seq + [j], score * -row[j]]
				all_candidates.append(candidate)
		# order all candidates by score
		ordered = sorted(all_candidates, key=lambda tup:tup[1])
		# select k best
		sequences = ordered[:k]
	return sequences

def generate_ngrams(self, s, n):
    #s = re.sub(r'[^a-zA-Z0-9\s]', ' ', s)
    if not s:
        tokens = []
    else:
        tokens = [token for token in s.split(" ") if token != ""]

    # Use the zip function to help us generate n-grams
    # Concatentate the tokens into ngrams and return
    ngrams = zip(*[tokens[i:] for i in range(n)])
    return [" ".join(ngram) for ngram in ngrams]

class LSTMTaggerEntity(nn.Module):
    def __init__(self, embedding_dim, hidden_dim, tagset_size):
        super(LSTMTaggerEntity, self).__init__()
        self.hidden_dim = hidden_dim
        self.lstm = nn.LSTM(input_size=embedding_dim, hidden_size=hidden_dim//2, num_layers=4,bidirectional=True,batch_first=True)
        self.dropout = nn.Dropout(p=0.1)
        self.relu = nn.ReLU()
        self.hidden2tag = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            self.relu,
            self.dropout,
            nn.Linear(hidden_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            self.relu,
            nn.Linear(hidden_dim, 4)
        ).cuda()


    def forward(self, sentence):
        lstm_out, _ = self.lstm(sentence)
        batch_size = lstm_out.shape[0]
        tags = self.hidden2tag(lstm_out.contiguous().view(-1, lstm_out.size(2)))
        scores = F.log_softmax(tags, dim=1)
        return scores


class LSTMTagger(nn.Module):
    def __init__(self, embedding_dim, hidden_dim, tagset_size):
        super(LSTMTagger, self).__init__()
        self.hidden_dim = hidden_dim
        self.lstm = nn.LSTM(input_size=embedding_dim, hidden_size=hidden_dim//2, num_layers=2,bidirectional=True,batch_first=True)
        self.dropout = nn.Dropout(p=0.3)
        self.relu = nn.ReLU()
        self.hidden2tag = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            self.relu,
            self.dropout,
            nn.Linear(hidden_dim, 4)
        )

    def forward(self, sentence):
        lstm_out, _ = self.lstm(sentence)
        batch_size = lstm_out.shape[0]
        tags = self.hidden2tag(lstm_out.contiguous().view(-1, lstm_out.size(2)))
        scores = F.log_softmax(tags, dim=1)
        return scores


class ERSpanDetector():
    def __init__(self):
       print("Initialising ER span detector")
       self.es = Elasticsearch()
       self.entitymodel = LSTMTaggerEntity(456, 456, 4).cuda()
       self.entitymodel.load_state_dict(torch.load('../data/espan98.0756.model'))
       self.entitymodel.eval()
       print("Initialised ER span detector")

    def erspan(self,nlquery):
        q = nlquery
        q = re.sub("\s*\?", "", q.strip())
        result = TextBlob(q)
        chunks = result.tags
        fuzzscores = []
        wordvectors = []
        chunkswords = []
        wordvector = []
        for chunk,word in zip(chunks,q.split(' ')):
            chunkswords.append((chunk,word))
        print(chunkswords)
        for idx,chunkwordtuple in enumerate(chunkswords):
            word = chunkwordtuple[1]
            req = urllib2.Request('http://localhost:8887/ftwv')
            req.add_header('Content-Type', 'application/json')
            inputjson = {'chunks':[word]}
            response = urllib2.urlopen(req, json.dumps(inputjson))
            embedding = json.loads(response.read().decode('utf8'))[0]
            wordvector = embedding
            #n-1,n
            if idx > 0:
                word = chunkswords[idx-1][1] + ' ' + chunkswords[idx][1]
                esresult = self.es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word,"fields":["wikidataLabel"]}},"size":10})
                esresults = esresult['hits']['hits']
                if len(esresults) > 0:
                    for esresult in esresults:
                        wordvector +=  [fuzz.ratio(word, esresult['_source']['wikidataLabel'])/100.0, fuzz.partial_ratio(word, esresult['_source']['wikidataLabel'])/100.0, fuzz.token_sort_ratio(word, esresult['_source']['wikidataLabel'])/100.0]
                    wordvector += (10-len(esresults)) * [0.0,0.0,0.0]
                else:
                    wordvector +=  10*[0.0,0.0,0.0]
            else:
                wordvector +=  10*[0.0,0.0,0.0]
            #n 
            word = chunkwordtuple[1]
            esresult = self.es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word,"fields":["wikidataLabel"]}},"size":10})
            esresults = esresult['hits']['hits']
            if len(esresults) > 0:
                for esresult in esresults:
                    wordvector +=  [fuzz.ratio(word, esresult['_source']['wikidataLabel'])/100.0, fuzz.partial_ratio(word, esresult['_source']['wikidataLabel'])/100.0, fuzz.token_sort_ratio(word, esresult['_source']['wikidataLabel'])/100.0]
                wordvector += (10-len(esresults)) * [0.0,0.0,0.0]
            else:
                wordvector +=  10*[0.0,0.0,0.0]
            #n,n+1
            if idx < len(chunkswords)-1:
                word = chunkswords[idx][1] + ' ' + chunkswords[idx+1][1]
                esresult = self.es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word,"fields":["wikidataLabel"]}},"size":10})
                esresults = esresult['hits']['hits']
                if len(esresults) > 0:
                    for esresult in esresults:
                        wordvector +=  [fuzz.ratio(word, esresult['_source']['wikidataLabel'])/100.0, fuzz.partial_ratio(word, esresult['_source']['wikidataLabel'])/100.0, fuzz.token_sort_ratio(word, esresult['_source']['wikidataLabel'])/100.0]
                    wordvector += (10-len(esresults)) * [0.0,0.0,0.0]
                else:
                    wordvector +=  10*[0.0,0.0,0.0]
            else:
                wordvector +=  10*[0.0,0.0,0.0]
            #n-1,n,n+1
            if idx > 0 and idx < len(chunkswords)-1:
                word = chunkswords[idx-1][1] + ' ' + chunkswords[idx][1] + ' ' + chunkswords[idx+1][1]
                esresult = self.es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word,"fields":["wikidataLabel"]}},"size":10})
                esresults = esresult['hits']['hits']
                if len(esresults) > 0:
                    for esresult in esresults:
                        wordvector +=  [fuzz.ratio(word, esresult['_source']['wikidataLabel'])/100.0, fuzz.partial_ratio(word, esresult['_source']['wikidataLabel'])/100.0, fuzz.token_sort_ratio(word, esresult['_source']['wikidataLabel'])/100.0]
                    wordvector += (10-len(esresults)) * [0.0,0.0,0.0]
                else:
                    wordvector +=  10*[0.0,0.0,0.0]
            else:
                wordvector +=  10*[0.0,0.0,0.0]
            posonehot = len(postags)*[0.0]
            posonehot[postags.index(chunk[1])] = 1
            wordvector += posonehot
            wordvectors.append(wordvector)
        nullvector = [-1]*456
        for i in range(50 - len(wordvectors)):
            wordvectors.append(nullvector)
        testxtensors = torch.tensor([wordvectors],dtype=torch.float).cuda()
        epreds = self.entitymodel(testxtensors)[0:len(chunks)]
        eseqs = beam_search_decoder(epreds.detach().cpu().numpy(),1)
        allerpredictions = []
        for eseq in eseqs:
            #relations
            erpredictions = []
            entity_labels = eseq[0]
            predwordtuplelist = []
            for word,ent in zip(q.split(' '),entity_labels):
                predwordtuplelist.append((word,ent))
            predgroup = [tuple(i for i in e) for _, e in groupby(predwordtuplelist, lambda x: x[1])]
            entpredgroups = []
            for item in predgroup:
                for t in item:
                    if  t[1] == 1:
                        entpredgroups.append(item)
                        break
            for item in entpredgroups:
                chunk = ''
                for t in item:
                    chunk += ' '+t[0]
                if item[0][1] == 1:
                    erpredictions.append({'chunk': chunk.strip(), 'surfacestart': -1, 'surfacelength':-1, 'class':'entity'})
            allerpredictions.append(erpredictions)
        return allerpredictions

if __name__ == '__main__':
    e = ERSpanDetector()
#    print(e.erspan("name the place of qaqun"))
#    print(e.erspan("who is the president of india?"))
#    print(e.erspan("Who is the president of India?"))
#    print(e.erspan("Who is the father of the mother of Barack Obama"))
#    print(e.erspan("who is the father of the mother of barack obama"))
#    print(e.erspan("How many rivers flow through Bonn?"))
#    print(e.erspan("how many rivers flow through bonn?"))
#    print(e.erspan("Which company developed Skype ?"))
#    print(e.erspan("List all the musicals with music by Elton John."))
#    print(e.erspan("Give me the names of professional skateboarders of India"))
    print(e.erspan("What award did Robert Zemeckis receive for his work in Forrest Gump ? "))

