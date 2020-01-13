import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import json
import sys
import random
from sklearn.metrics import accuracy_score
import numpy as np
from math import log
from numpy import array
from numpy import argmax

torch.manual_seed(1)

def prepare_sequence(seq, to_ix):
    idxs = [to_ix[w] for w in seq]
    return torch.tensor(idxs, dtype=torch.long)


MAX_PAD_LIMIT = 100
#d1 = json.loads(open('wordvecsngramsparaphrased1.json').read())
d = json.loads(open('unifieddatasets/entityonlywordvecsngrams1.json').read())
random.shuffle(d)
trainsplit = d[0:int(0.9*len(d))]
testsplit = d[int(0.9*len(d)):]
trainx = []
trainlabels = []
for item in trainsplit:
    nullvector = [-1]*456
    for i in range(100 - len(item['wordvectors'])):
        item['wordvectors'].append(nullvector)
    newerspan = item['erspan'] + [3]*(100 - len(item['erspan']))
    if len(newerspan) != 100 or len(item['wordvectors']) != 100:
        print(item['question'])
        print(item['erspan'])
        continue
    trainx.append(item['wordvectors'])
    trainlabels.append(newerspan)


trainxtensors = torch.tensor(trainx,dtype=torch.float)#.cuda()
trainlabeltensors = torch.tensor(trainlabels,dtype=torch.long)#.cuda()

testx = []
testlabels = []
for item in testsplit:
    nullvector = [-1]*456
    for i in range(100 - len(item['wordvectors'])):
        item['wordvectors'].append(nullvector)
    _newerspan = item['erspan'] + [3]*(100 - len(item['erspan']))
    newerspan = [0 if x == 2 else x for x in _newerspan]
    if len(newerspan) != 100 or len(item['wordvectors']) != 100:
        print(item['question'])
        print(item['erspan'])
        continue
    testx.append(item['wordvectors'])
    testlabels.append(newerspan)
    
print(len(testx))
testxtensors = torch.tensor(testx,dtype=torch.float)#.cuda()
testlabeltensors = torch.tensor(testlabels,dtype=torch.long)#.cuda()


# These will usually be more like 32 or 64 dimensional.
# We will keep them small, so we can see how the weights change as we train.
EMBEDDING_DIM = 456
HIDDEN_DIM = 456


class LSTMTagger(nn.Module):
    def __init__(self, embedding_dim, hidden_dim, tagset_size):
        super(LSTMTagger, self).__init__()
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

model = LSTMTagger(EMBEDDING_DIM, HIDDEN_DIM, 4).cuda()
if len(sys.argv) > 1:
    model.load_state_dict(torch.load(sys.argv[1]))
    

loss_function = nn.NLLLoss()
optimizer = optim.SGD(model.parameters(), lr=0.01)
#optimizer = optim.Adam(model.parameters(), lr=0.0001)

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

iter = 0
bestacc = 0.0
batch_size=20
while 1:
    permutation = torch.randperm(trainxtensors.size()[0])

    for i in range(0,trainxtensors.size()[0],batch_size):
        indices = permutation[i:i+batch_size]
        _trainxtensors,_trainlabeltensors = trainxtensors[indices].cuda(),trainlabeltensors[indices].cuda()
        model.zero_grad()
        tag_scores = model(_trainxtensors)
        loss = loss_function(tag_scores, _trainlabeltensors.view(-1))
        loss.backward()
        optimizer.step()
        totacc = 0
        if iter%100 == 0 and iter > 0:
            print(loss)
            with torch.no_grad():
                preds = model(testxtensors[:2000].cuda())
                preds = preds.view((int(preds.shape[0]/100),100,4))
                _, pred_labels = torch.max(preds, dim=-1)
                y_true = testlabeltensors[:2000].cpu().data.numpy()
                y_pred = pred_labels.cpu().data.numpy()
                for j in range(pred_labels.size()[0]):
                    end = np.where(y_true[j]==3)[0][0]
                    prednpy = preds[j].cpu().numpy()
                    prednpy = prednpy[0:end]
                    y_t = y_true[j][0:end]
                    #y_p = y_pred[i][0:end]
                    seqs = beam_search_decoder(prednpy,5)
                    bestseqacc = 0
                    for seq in seqs:
                        y_p = np.asarray(seq[0])
                        acc = accuracy_score(y_t, y_p)
                        if acc > bestseqacc:
                            bestseqacc = acc
                    totacc += bestseqacc
                if totacc > bestacc:
                    torch.save(model.state_dict(), 'espan.model')
                    bestacc = totacc
                print("Test accuracy = %f, Best accuracy = %f"%(totacc/float(pred_labels.size()[0]), bestacc/float(pred_labels.size()[0])))
        iter += 1
