import sys,os,json,torch,re
import torch.optim as optim
from torch.nn import functional as F


torch.manual_seed(1)
d = json.loads(open('reranktrain2.json').read())
inputs = []
outputs = []
ocount = 0
zcount = 0
_zcount = 0
for item in d:
    if item['trueentity'] == 1:
        inputs.append([item['connections'],item['esrank'],item['sumofhops']])
        outputs.append(1.0)
        ocount += 1
    if item['trueentity'] == 0 and item['truerelation'] == -1:
        if zcount%50 == 0:
            inputs.append([item['connections'],item['esrank'],item['sumofhops']])
            outputs.append(0.0)
            _zcount += 1
        zcount += 1

print(ocount,zcount,_zcount)

f = open('../LC-QuAD2.0/dataset/test.json')
s = f.read()
d1 = json.loads(s)
f.close()
lcqgold = []
earltest = []
lcqgoldquestions = []

for item in d1:
    itarr = []
    lcqgoldquestions.append(item['question'])
    _ents = re.findall( r'wd:(.*?) ', item['sparql_wikidata'])
    for ent in _ents:
        itarr.append( ent )
    lcqgold.append(itarr)

f = open('../with2hoppreds1.json')
s = f.read()
d2 = json.loads(s)
f.close()



device = torch.device('cuda')
batch_size = 10000
N, D_in, H, D_out = batch_size, 3, 3, 1

x = torch.FloatTensor(inputs).cuda()
y = torch.FloatTensor(outputs).cuda()

model = torch.nn.Sequential(
          torch.nn.Linear(D_in, H),
          torch.nn.ReLU(),
          torch.nn.Linear(D_in, H),
          torch.nn.ReLU(),
          torch.nn.Linear(H, D_out)#,
#          torch.nn.Sigmoid()
        ).to(device)

loss_fn = torch.nn.MSELoss(reduction='mean')
#loss_fn = torch.nn.BCELoss(reduction='mean')
optimizer = optim.Adam(model.parameters(), lr=0.001)#,nesterov=True, momentum=0.5)
iter = 0
besttrue = 0
urilabeldict = {}
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
        print(iter,loss)
    true = 0
    false = 0
    total = 0
    tlqi = 0
    with torch.no_grad():
        for lcqitem,item in zip(lcqgold[:100],d2[:100]):
            for lcquri in lcqitem:
                if len(item[1]) == 0:
                    continue
                for _k,_v in item[1]['rerankedlists'].iteritems():
                    reranked = []
                    uris = []
                    featurevectors = []
                    if 'P' in _v[0][1][0]:
                        continue
                    for uridict in _v:
                        uris.append(uridict[1][0])
                        featurevectors.append([uridict[1][1]['connections'],uridict[1][1]['esrank'],uridict[1][1]['sumofhops']])
                    preds = model(torch.FloatTensor(featurevectors).cuda()).cuda()
                    preds = preds.reshape(-1).cpu().numpy()
                    reranked = [(float(pred),uri) for pred,uri in zip(preds,uris)]
                    sortedreranked = sorted(reranked,key=lambda item: item[0], reverse=True)
                    if lcquri == sortedreranked[0][1]:
                        true += 1
                    else:
                        false += 1

    print(iter,true,besttrue,"epoch/true/besttrue")
    if true > besttrue:
        print('saved')
        torch.save(model.state_dict(), 'wikirerankerentity.model')
        besttrue = true


