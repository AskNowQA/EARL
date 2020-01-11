import sys,os,json,re


gold = []
f = open('annotated_wd_data_test.txt')
for line in f.readlines():
    line = line.strip()
    s,p,o,q = line.split('\t')
    gold.append(s)


f = open('simplequestiionsout.json')
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
#    if queryitem[0] != golditem['uid']:
#        print('uid mismatch')
#        sys.exit(1)
    queryentities = []
    for chunk in queryitem[1]:
        if 'reranked' in chunk:
            for entid in chunk['reranked']:
                queryentities.append(entid)
                break
    #print(golditem['entities'],queryentities, golditem['question'], chunk['chunk']['chunk'])
    print(golditem,queryentities)
    totalentchunks += 1
    if golditem in queryentities:
        tpentity += 1
    else:
        fnentity += 1
    for queryentity in queryentities:
        if queryentity != golditem:
            fpentity += 1

precisionentity = tpentity/float(tpentity+fpentity)
recallentity = tpentity/float(tpentity+fnentity)
f1entity = 2*(precisionentity*recallentity)/(precisionentity+recallentity)
print("precision entity = ",precisionentity)
print("recall entity = ",recallentity)
print("f1 entity = ",f1entity)
