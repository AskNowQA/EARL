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
    unit['relations'] = ['http://www.wikidata.org/entity/'+rel for rel in _rels]
    gold.append(unit)

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
            if '_' in topkmatch[0]:
               queryrelations.append(topkmatch[0].split('_')[0])
               queryrelations.append('http://www.wikidata.org/entity/'+topkmatch[0].split('_')[1])
            else:
                queryrelations.append(topkmatch[0])
    queryrelations = list(set(queryrelations))
    for goldrel in golditem['relations']:
        if goldrel in queryrelations:
            found += 1

print('ngram rel tile fail top 200 = %f'%((totalgoldrelcount - found)/float(totalgoldrelcount)))
            
