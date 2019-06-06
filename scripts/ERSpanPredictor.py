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

class LSTMTagger(nn.Module):
    def __init__(self, embedding_dim, hidden_dim, tagset_size):
        super(LSTMTagger, self).__init__()
        self.lstm = nn.LSTM(embedding_dim, hidden_dim//2, bidirectional=True)
        self.hidden2tag1 = nn.Linear(hidden_dim, hidden_dim)
        self.hidden2tag2 = nn.Linear(hidden_dim, tagset_size)

    def forward(self, sentence):
        lstm_out, _ = self.lstm(sentence)
        tag_space1 = self.hidden2tag1(lstm_out)
        tag_space2 = self.hidden2tag2(tag_space1)
        tag_scores = F.log_softmax(tag_space2, dim=1)
        return tag_scores


class ERSpanDetector():
    def __init__(self):
       print("Initialising ER span detector")
       self.es = Elasticsearch()
       self.model = LSTMTagger(341, 300, 4)#.cuda()
       self.model.load_state_dict(torch.load('../data/erspan.model',map_location='cpu'))
       self.model.eval()
       print("Initialised ER span detector")

    def erspan(self,nlquery):
        q = nlquery
        q = re.sub("\s*\?", "", q.strip())
        result = TextBlob(q)
        chunks = result.tags
        fuzzscores = []
        wordvectors = []
        for chunk,word in zip(chunks,q.split(' ')):
            req = urllib2.Request('http://localhost:8887/ftwv')
            req.add_header('Content-Type', 'application/json')
            inputjson = {'chunk':word}
            response = urllib2.urlopen(req, json.dumps(inputjson))
            embedding = json.loads(response.read())
            esresult = self.es.search(index="dbentityindex11", body={"query":{"multi_match":{"query":word,"fields":["wikidataLabel", "dbpediaLabel^1.5"]}},"size":10})
            esresults = esresult['hits']['hits']
            wordvector = embedding
            if len(esresults) > 0:
                for esresult in esresults:
                    if 'dbpediaLabel' in esresult['_source']:
                        wordvector +=  [float(esresult['_score']), fuzz.ratio(word, esresult['_source']['dbpediaLabel']), fuzz.partial_ratio(word, esresult['_source']['dbpediaLabel']), fuzz.token_sort_ratio(word, esresult['_source']['dbpediaLabel'])]
                    if 'wikidataLabel' in esresult['_source']:
                        wordvector +=  [float(esresult['_score']), fuzz.ratio(word, esresult['_source']['wikidataLabel']), fuzz.partial_ratio(word, esresult['_source']['wikidataLabel']), fuzz.token_sort_ratio(word, esresult['_source']['wikidataLabel'])]
                wordvector += (10-len(esresults)) * [0.0,0.0,0.0,0.0]
            else:
                wordvector +=  10*[0.0,0.0,0.0,0.0]
            wordvector += [postags.index(chunk[1])]
            wordvectors.append(wordvector)
        nullvector = [-1]*341
        for i in range(50 - len(wordvectors)):
            wordvectors.append(nullvector)
    
        testxtensors = torch.tensor([wordvectors],dtype=torch.float)
        preds = self.model(testxtensors)[0][0:len(chunks)]
        print(preds.shape)
        seqs = beam_search_decoder(preds,4)
        allerpredictions = []
        for seq in seqs:
            erpredictions = []
            pred_labels = seq[0]
            predwordtuplelist = []
            for pred,word in zip(pred_labels,q.split(' ')):
                predwordtuplelist.append((word,pred))
            predgroup = [tuple(i for i in e) for _, e in groupby(predwordtuplelist, lambda x: x[1])]
            entpredgroups = []
            for item in predgroup:
                for t in item:
                    if t[1] == 1 or t[1] == 2:
                        entpredgroups.append(item)
                        break
            for item in entpredgroups:
                chunk = ''
                for t in item:
                    chunk += ' '+t[0]
                if item[0][1] == 1:
                    erpredictions.append({'chunk': chunk.strip(), 'surfacestart': -1, 'surfacelength':-1, 'class':'entity'})
                if item[0][1] == 2:
                    erpredictions.append({'chunk': chunk.strip(), 'surfacestart': -1, 'surfacelength':-1, 'class':'relation'})
            allerpredictions.append(erpredictions)
        return allerpredictions

if __name__ == '__main__':
    e = ERSpanDetector()
    print(e.erspan("who is the president of india?"))
    print(e.erspan("Who is the president of India?"))
    print(e.erspan("Who is the father of the mother of Barack Obama"))
    print(e.erspan("who is the father of the mother of barack obama"))
    print(e.erspan("How many rivers flow through Bonn?"))
    print(e.erspan("how many rivers flow through bonn?"))
