import sys,os,json,re


gold = []
f = open('/home/sda-srv05/debayan/LC-QuAD2.0/dataset/test.json')
d1 = json.loads(f.read())

d = sorted(d1, key=lambda x: int(x['uid']))

for item in d:
    wikisparql = item['sparql_wikidata']
    unit = {}
    unit['uid'] = item['uid']
    unit['question'] = item['question']
    _ents = re.findall( r'wd:([Q][0-9]*)', wikisparql)
    _rels = re.findall( r'wdt:(.*?) ',wikisparql)
    unit['entities'] = [ent for ent in _ents]
    unit['relations'] = [rel for rel in _rels]
    unit['full'] = item
    gold.append(unit)

f = open('simpleentembed1.json')
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
templatedict = {}
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
    #            break
    print(golditem['entities'],queryentities, golditem['question'], chunk['chunk']['chunk'])
    for goldentity in golditem['entities']:
        totalentchunks += 1
        if goldentity in queryentities:
            tpentity += 1
        else:
            fnentity += 1
    for queryentity in queryentities:
        if queryentity not in golditem['entities']:
            fpentity += 1

precisionentity = tpentity/float(tpentity+fpentity)
recallentity = tpentity/float(tpentity+fnentity)
f1entity = 2*(precisionentity*recallentity)/(precisionentity+recallentity)
print("precision entity = ",precisionentity)
print("recall entity = ",recallentity)
print("f1 entity = ",f1entity)
