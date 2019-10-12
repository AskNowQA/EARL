import sys,os,json,re


gold = []
f = open('/data/home/sda-srv05/debayan/LC-QuAD2.0/dataset/train.json')
d = json.loads(f.read())

for item in d:
    wikisparql = item['sparql_wikidata']
    unit = {}
    unit['uid'] = item['uid']
    unit['question'] = item['question']
    _ents = re.findall( r'wd:(.*?) ', wikisparql)
    _rels = re.findall( r'wdt:(.*?) ',wikisparql)
    unit['entities'] = ['http://wikidata.dbpedia.org/resource/'+ent for ent in _ents]
    unit['relations'] = ['http://www.wikidata.org/entity/'+rel for rel in _rels]
    gold.append(unit)

f = open('ngramtraintile1.json')
d = json.loads(f.read())

traindata = []

for queryitem,golditem in zip(d,gold):
    try:
    #print(queryitem[0],queryitem[1].keys())
        uridict = {}
        for entity in queryitem[1]['entities']:
            uri = entity['uri']
            found = 0
            if uri in golditem['entities']:
                print(uri,golditem['entities'])
                found = 1
            vec = entity['vector'] + [entity['uricounter'], found]
            if uri not in uridict:
                uridict[uri] = vec
            else:
                if entity['uricounter'] > uridict[uri][8]: #uricount = index 8
                    vec = entity['vector'] + [entity['uricounter'], found]
                    uridict[uri] = vec
        for uri,vec in uridict.items():
            traindata.append(vec)
    except Exception as e:
        print(e)
        continue

f = open('ngramtraindata1.json','w')
f.write(json.dumps(traindata)) 
f.close()
#    for item in queryitem:
#        print(item)
#        sys.exit(1)
#        for entity in item[1]['entities']:
#            print(entity)
#            sys.exit(1)




