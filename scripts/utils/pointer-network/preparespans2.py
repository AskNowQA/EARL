import sys,json
from itertools import groupby

d = json.loads(open('lcquad.json').read())

items = []

for item in d:
    q = item['question']
    qspan = [0]*len(q)
    for entity in item['entity mapping']:
        if entity['matchedBy'] == 'byLabel':
            span = entity["seq"]
            beg = q.find(span)
            print(beg)
            if beg == -1:
                continue
            end = beg + len(span) - 1
            qspan[beg:end] = [1] * len(span) #entity
    for pred in item['predicate mapping']:
        if pred['mappedBy'] == 'byLabelMatch':
            span = pred["seq"]
            beg = q.find(span)
            if beg == -1:
                continue
            end = beg + len(span) - 1
            qspan[beg:end] = [2] * len(span) #predicate
    count = 0
    for char in q:
        if char == ' ':
            qspan[count] = -1 #space
        count += 1
    qspantokens = [x[0] for x in groupby(qspan)]
    #print(qspantokens)
    qspantokens = filter(lambda a: a != -1, qspantokens)
    if 1 in qspantokens and 2 in qspantokens:
        print(q)
        print(qspan)
        print(qspantokens)
        sys.exit(1)
        items.append({'question':q, 'erspan':qspantokens})

f = open('erspans.json','w')
f.write(json.dumps(items))
f.close()
