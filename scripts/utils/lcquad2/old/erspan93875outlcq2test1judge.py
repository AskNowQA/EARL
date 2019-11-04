import sys,os,json,re


gold = []
f = open('/data/home/sda-srv05/debayan/LC-QuAD2.0/dataset/test.json')
d = json.loads(f.read())[:100]
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

f = open('erspan93875outlcq2test1.json')
d = json.loads(f.read())
found = 0
notfound = 0
for queryitems,golditem in zip(d,gold):
    relations = []
    entities = []
    for queryitem in queryitems[1][:1]:
        for queryite in queryitem:
            if queryite['class'] == 'relation':
                for topkmatch in queryite['topkmatches']:
                    for uri in topkmatch['uris']:
                        relations.append(uri)
            else:
                entities += queryite['topkmatches'][:30]
    print(entities)
    print(relations)
    for goldentity in golditem['entities']:
        if goldentity in entities:
            found += 1


print('ngram tile fail = %f'%((totalgoldentcount - found)/float(totalgoldentcount)))
            




