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
device = torch.device('cuda')
#d1 = json.loads(open('wordvecsngramsparaphrased1.json').read())
d = json.loads(open('ngramtraindata1.json').read())
count1 = 0
count0 = 0

for item in d:
    if item[-1] == 0:
        count0 += 1
    if item[-1] == 1:
        count1 += 1

train0 = [item for item in d if item[-1] == 0]
random.shuffle(train0)
train0 = train0[:count1]
train1 = [item for item in d if item[-1] == 1]
train = train0+train1
random.shuffle(train)

trainsplit = train[0:int(0.9*len(train))]
testsplit = train[int(0.9*len(train)):]
trainx = [vec[:-1] for vec in trainsplit]
trainlabels = [vec[-1] for vec in trainsplit]

trainxtensors = torch.tensor(trainx,dtype=torch.float).to(device)
trainlabeltensors = torch.tensor(trainlabels,dtype=torch.float).to(device)

testx = [vec[:-1] for vec in testsplit]
testlabels = [vec[-1] for vec in testsplit]

testxtensors = torch.tensor(testx,dtype=torch.float).to(device)
testlabeltensors = torch.tensor(testlabels,dtype=torch.float).to(device)

D_in = 9
H = 9
D_out = 1
model = torch.nn.Sequential(
          torch.nn.Linear(D_in, H),
          torch.nn.ReLU(),
          torch.nn.Linear(D_in, H),
          torch.nn.ReLU(),
          torch.nn.Linear(H, D_out)#,
#          torch.nn.Sigmoid()
        ).to(device)

loss_fn = torch.nn.MSELoss(reduction='mean')
optimizer = optim.Adam(model.parameters(), lr=0.0001)#,nesterov=True, momentum=0.5)
iter = 0
bestloss = 10
while 1:
    iter += 1
    y_pred = model(trainxtensors)
    loss = loss_fn(y_pred.reshape(-1), trainlabeltensors)
    model.zero_grad()
    loss.backward()
    optimizer.step()
    if (iter%100 == 0):
        print(iter,loss)
        with torch.no_grad():
            test_pred = model(testxtensors)
            testloss = loss_fn(test_pred.reshape(-1), testlabeltensors)
            print("test loss %f"%testloss)
            if testloss < bestloss:
                print('saved')
                torch.save(model.state_dict(), 'entityfilter1.model')
                bestloss = testloss
