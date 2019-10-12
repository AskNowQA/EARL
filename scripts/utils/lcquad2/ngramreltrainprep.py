import sys,os,json,re


gold = []
f = open('/data/home/sda-srv05/debayan/LC-QuAD2.0/dataset/train.json')
d1 = json.loads(f.read())
totalgoldrelcount = 0
for item in d1:
    wikisparql = item['sparql_wikidata']
    unit = {}
    unit['uid'] = item['uid']
    unit['question'] = item['question']
    _rels = re.findall( r'wdt:(.*?) ',wikisparql)
    totalgoldrelcount += len(_rels)
    unit['relations'] =  _rels
    gold.append(unit)


pos = []
neg = []
f = open('ngramtesttilerelations1.json')
d2 = json.loads(f.read())
found = 0
for queryitem,golditem in zip(d2,gold):
    queryrelations = []
    if len(queryitem) == 0:
        continue
    if 'relations' not in queryitem[1]:
        continue
    for chunk in queryitem[1]['relations'][:10]:
        for topkmatch in chunk['topkmatches']:
           queryrelations.append((topkmatch[0], topkmatch[1],chunk['ngramsize']))
    queryrelations = list(set(queryrelations))
    for goldrel in golditem['relations']:
        for queryrel in queryrelations:
            if goldrel == queryrel[0]:
                pos.append(queryrel)
            else:
                neg.append(queryrel)
          
print("pos length ",len(pos))
print("neg length ",len(neg))
f = open('reltrainpos1.json','w')
f.write(json.dumps(pos))
f.close()
f = open('reltrainneg1.json','w')
f.write(json.dumps(neg))
f.close()
            
