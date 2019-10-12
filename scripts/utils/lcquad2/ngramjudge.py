import sys,os,json,re


gold = []
f = open('/data/home/sda-srv05/debayan/LC-QuAD2.0/dataset/test.json')
d = json.loads(f.read())
totalgoldentcount = 0
for item in d:
    wikisparql = item['sparql_wikidata']
    unit = {}
    unit['uid'] = item['uid']
    unit['question'] = item['question']
    _ents = re.findall( r'wd:(.*?) ', wikisparql)
    totalgoldentcount += len(_ents)
    _rels = re.findall( r'wdt:(.*?) ',wikisparql)
    unit['entities'] = ['http://wikidata.dbpedia.org/resource/'+ent for ent in _ents]
    unit['relations'] = ['http://www.wikidata.org/entity/'+rel for rel in _rels]
    gold.append(unit)

f = open('ngramtesttilelcq21.json')
d = json.loads(f.read())
found = 0
notfound = 0
for queryitem,golditem in zip(d,gold):
    for goldentity in golditem['entities']:
        if 'entities' in queryitem[1]:
            if goldentity in queryitem[1]['entities']:
                found += 1
        else:
           print(goldentity, queryitem)

print('ngram tile fail = %f'%((totalgoldentcount - found)/float(totalgoldentcount)))
            




