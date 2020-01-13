import sys,os,json,re


gold = []
d = json.loads(open('input/graph.test.entities.json').read())
for item in d:
    gold.append({'entities':item['entities'], 'uid':item['question_id']})


f = open('gqsout.json')
d1 = json.loads(f.read())

d = sorted(d1, key=lambda x: int(x[0]))

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
        print('uid mismatch')
        sys.exit(1)
    queryentities = []
    for chunk in queryitem[1]:
        if 'reranked' in chunk:
            for entid in chunk['reranked']:
                queryentities.append(entid)
                break
    print(golditem,queryentities)
    for goldent in set(golditem['entities']):
        if goldent in queryentities:
            tpentity += 1
        else:
            fnentity += 1
    for queryentity in set(queryentities):
        if queryentity != golditem['entities']:
            fpentity += 1

precisionentity = tpentity/float(tpentity+fpentity)
recallentity = tpentity/float(tpentity+fnentity)
f1entity = 2*(precisionentity*recallentity)/(precisionentity+recallentity)
print("precision entity = ",precisionentity)
print("recall entity = ",recallentity)
print("f1 entity = ",f1entity)
