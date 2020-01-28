import sys,os,json,re


gold = []
f = open('input/webqsp.test.entities.with_classes.json')
d1 = json.loads(f.read())

d = sorted(d1, key=lambda x: x['question_id'])

for item in d:
    unit = {}
    unit['uid'] = item['question_id']
    unit['question'] = item['utterance']
    unit['entities'] = item['entities']
    gold.append(unit)

f = open('starsemgraphq1.json')
d1 = json.loads(f.read())

d = sorted(d1, key=lambda x: x[0])

tpentity = 0
fpentity = 0
fnentity = 0
tprelation = 0
fprelation = 0
fnrelation = 0
totalentchunks = 0
totalrelchunks = 0
mrrent = 0
mrrrel = 0
chunkingerror = 0
for queryitem,golditem in zip(d,gold):
    if len(queryitem[1]) == 0:
        continue
    if queryitem[0] != golditem['uid']:
        print(queryitem[0], golditem['uid'])
        print('uid mismatch')
        sys.exit(1)
    queryentities = []
    print(golditem['question'])
    for chunk in queryitem[1]:
        for entity in chunk['reranked']:
            queryentities.append(entity)
            break
    print(golditem['entities'])
    print(set(queryentities))
    for goldentity in golditem['entities']:
        totalentchunks += 1
        if goldentity in queryentities:
            tpentity += 1
        else:
            fnentity += 1
    for queryentity in set(queryentities):
        if queryentity not in golditem['entities']:
            fpentity += 1

precisionentity = tpentity/float(tpentity+fpentity)
recallentity = tpentity/float(tpentity+fnentity)
f1entity = 2*(precisionentity*recallentity)/(precisionentity+recallentity)
print("precision entity = ",precisionentity)
print("recall entity = ",recallentity)
print("f1 entity = ",f1entity)
