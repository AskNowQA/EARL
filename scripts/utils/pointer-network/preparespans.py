import sys,json,re
from itertools import groupby

d = json.loads(open('unifieddatasets/unifiedtrainbestspans1.json').read())

items = []
seen = {}

for item in d:
    if item['uid'] in seen:
        continue
    seen[item['uid']] = None
    q = item['question']
    #print(q)
    q = re.sub("\s*\?", "", q.strip())
    #print(q)
    qspan = [0]*len(q)
    for entity,span in item['spanmatch'].items():
        beg = q.find(span['ngram'])
        if beg == -1:
            continue
        end = beg + len(span["ngram"])
        qspan[beg:end] = [1] * len(span["ngram"]) #entity
    count = 0
    for char in q:
        if char == ' ':
            qspan[count] = -1 #space
        count += 1
    qspantokens = [x[0] for x in groupby(qspan)]
    qspantokens = filter(lambda a: a != -1, qspantokens)
    if 1 in qspantokens:
        #print(q)
        #print(item)
        #print(qspan)
        #print(qspantokens)
        items.append({'question':q, 'erspan':list(qspantokens)})

seen = {}

for item in d:
    if item['uid'] in seen:
        continue 
    seen[item['uid']] = None
    q = item['question'].lower()
    #print(q)
    q = re.sub("\s*\?", "", q.strip())
    #print(q)
    qspan = [0]*len(q)
    for entity,span in item['spanmatch'].items():
        beg = q.find(span['ngram'].lower())
        if beg == -1:
            continue
        end = beg + len(span["ngram"])
        qspan[beg:end] = [1] * len(span["ngram"]) #entity
    count = 0
    for char in q:
        if char == ' ':
            qspan[count] = -1 #space
        count += 1
    qspantokens = [x[0] for x in groupby(qspan)]
    qspantokens = filter(lambda a: a != -1, qspantokens)
    if 1 in qspantokens:
        #print(q)
        #print(item)
        #print(qspan)
        #print(qspantokens)
        items.append({'question':q, 'erspan':list(qspantokens)})

print(len(items))
f = open('unifieddatasets/erspans.json','w')
f.write(json.dumps(items,indent=4))
f.close()
