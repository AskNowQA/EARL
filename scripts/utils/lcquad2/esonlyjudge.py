import sys,os,json,re


gold = []
f = open('lcquad2.0.json')
d = json.loads(f.read())

for item in d:
    wikisparql = item['sparql_wikidata']
    unit = {}
    unit['uid'] = item['uid']
    _ents = re.findall( r'wd:(.*?) ', wikisparql)
    _rels = re.findall( r'wdt:(.*?) ',wikisparql)
    unit['entities'] = ['http://wikidata.dbpedia.org/resource/'+ent for ent in _ents]
    unit['relations'] = ['http://www.wikidata.org/entity/'+rel for rel in _rels]
    gold.append(unit)

f = open('esonlyout1.json')
d = json.loads(f.read())

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
    queryentities = []
    queryrelations = []
    for chunk in queryitem:
        if chunk['chunk']['class'] == 'entity':
            for queryentity in chunk['topkmatches']: 
                queryentities.append(queryentity)
                break
        if chunk['chunk']['class'] == 'relation':
            for queryrelation in chunk['topkmatches']: 
                queryrelations.append(queryrelation)
                break
    for goldentity in golditem['entities']:
        totalentchunks += 1
        if goldentity in queryentities:
            tpentity += 1
        else:
            fnentity += 1
    for goldrelation in golditem['relations']:
        totalrelchunks += 1
        if goldrelation in queryrelations:
            tprelation += 1
        else:
            fnrelation += 1
    for queryentity in queryentities:
        if queryentity not in golditem['entities']:
            fpentity += 1
    for queryrelation in queryrelations:
        if queryrelation not in golditem['relations']:
            fprelation += 1

precisionentity = tpentity/float(tpentity+fpentity)
recallentity = tpentity/float(tpentity+fnentity)
f1entity = 2*(precisionentity*recallentity)/(precisionentity+recallentity)
print("precision entity = ",precisionentity)
print("recall entity = ",recallentity)
print("f1 entity = ",f1entity)

precisionrelation = tprelation/float(tprelation+fprelation)
recallrelation = tprelation/float(tprelation+fnrelation)
f1relation = 2*(precisionrelation*recallrelation)/(precisionrelation+recallrelation)
print("precision relation = ",precisionrelation)
print("recall relation = ",recallrelation)
print("f1 relation = ",f1relation)

mrrent = 0
mrrrel = 0
chunkingerror = 0
for queryitem,golditem in zip(d,gold):
    for chunk in queryitem:
        if chunk['chunk']['class'] == 'entity':
            for goldentity in golditem['entities']:
                if goldentity in chunk['topkmatches']:
                    mrrent += 1.0/float(chunk['topkmatches'].index(goldentity)+1)
        if chunk['chunk']['class'] == 'relation':
             for goldrelation in golditem['relations']:
                if goldrelation in chunk['topkmatches']:
                    mrrrel += 1.0/float(chunk['topkmatches'].index(goldrelation)+1)

totmrrent = mrrent/totalentchunks
totmrrrel = mrrrel/totalrelchunks
print('ent mrr = %f'%totmrrent)
print('rel mrr = %f'%totmrrrel)
