import sys,os,json,torch,re
import torch.optim as optim
from torch.nn import functional as F


torch.manual_seed(1)
d = json.loads(open('embedjointtrainvectors1.json').read())
inputs = []
outputs = []
ocount = 0
zcount = 0
_zcount = 0
for item in d:
    if item[2] == 1.0:
        vector = item[0] + item[1]
        inputs.append(vector)
        outputs.append(1.0)
        ocount += 1
    else:
        if zcount%2 == 0:
            vector = item[0] + item[1]
            inputs.append(vector)
            outputs.append(0.0)
            _zcount += 1
        zcount += 1

print(ocount,_zcount)

d = json.loads(open('embedjointtestvectors1.json').read())
testinputs = []
testoutputs = []
ocount = 0
_zcount = 0
for item in d:
    if item[2] == 1.0:
        vector = item[0] + item[1]
        testinputs.append(vector)
        testoutputs.append(1.0)
        ocount += 1
    else:
        vector = item[0] + item[1]
        testinputs.append(vector)
        testoutputs.append(0.0)
        _zcount += 1



device = torch.device('cuda')
batch_size = 10000
N, D_in, H1, H2, H3, H4,  D_out = batch_size, 501, 300, 100, 50, 10, 1

x = torch.FloatTensor(inputs).cuda()
y = torch.FloatTensor(outputs).cuda()
xtest = torch.FloatTensor(testinputs).cuda()
ytest = torch.FloatTensor(testoutputs).cuda()

model = torch.nn.Sequential(
          torch.nn.Linear(D_in, H1),
          torch.nn.ReLU(),
          torch.nn.Linear(H1, H2),
          torch.nn.ReLU(),
          torch.nn.Linear(H2, H3),
          torch.nn.ReLU(),
          torch.nn.Linear(H3, H4),
          torch.nn.ReLU(),
          torch.nn.Linear(H4, D_out)
        ).to(device)

loss_fn = torch.nn.MSELoss(reduction='mean')
#loss_fn = torch.nn.BCELoss(reduction='mean')
optimizer = optim.Adam(model.parameters(), lr=0.00001)#,nesterov=True, momentum=0.5)
iter = 0
besttrue = 0
urilabeldict = {}
bestloss = 999
while 1:
    iter += 1
    permutation = torch.randperm(x.size()[0])
    for i in range(0,x.size()[0],batch_size):
        indices = permutation[i:i+batch_size]
        _x,_y = x[indices],y[indices]
        y_pred = model(_x)
        loss = loss_fn(y_pred.reshape(-1), _y)
        model.zero_grad()
        loss.backward()
        optimizer.step()
    if iter%1000 == 0:
        print(iter,loss)
        with torch.no_grad():
            preds = model(xtest).cuda()
            testlossfn = torch.nn.MSELoss(reduction='mean')
            testloss = testlossfn(preds.reshape(-1),ytest)
            print("test set mseloss = %f bestloss = %f"%(testloss, bestloss))
            if testloss < bestloss:
                bestloss = testloss
                torch.save(model.state_dict(), 'jointembedentreranker.model')
                 
                
