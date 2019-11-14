import sys,os,json,re,copy

gold = []
f = open('../LC-QuAD2.0/dataset/train.json')
d = json.loads(f.read())

for item in d:
    wikisparql = item['sparql_wikidata']
    unit = {}
    unit['uid'] = item['uid']
    _ents = re.findall( r'wd:(.*?) ', wikisparql)
    _rels = re.findall( r'wdt:(.*?) ',wikisparql)
    unit['entities'] = [ent for ent in _ents]
    unit['relations'] = [rel for rel in _rels]
    gold.append(unit)


trainindata = []


d = json.loads(open('../with2hoppredstrain1.json').read())

for item,golditem in zip(d,gold):
    if len(item) == 0:
        continue
    if item[0] != golditem['uid']: 
        print('uid mismatch')
        sys.exit(1)
    item = item[1]
    print(item)
    if len(item) == 0:
        continue
    for chunknum,urldicts in item['rerankedlists'].iteritems():
        for urldict in urldicts:
            features = urldict[1][1]
            url = urldict[1][0]
            if 'P' in url: 
                if '_' in url:
                    relid = url.split('_')[0]
                    qualid = url.split('_')[1]
                    rel = relid
                    qual = qualid
                    for relation in golditem['relations']:
                        if relation == rel or relation == qual:
                            c = copy.deepcopy(features)
                            c['truerelation'] = 1
                            c['trueentity'] = -1
                            trainindata.append(c)
                else:
                    for relation in golditem['relations']:
                        if relation == url:
                            c = copy.deepcopy(features)
                            c['truerelation'] = 1
                            c['trueentity'] = -1
                            c['url'] = url
                            trainindata.append(c) 
             
            else:
                for entity in golditem['entities']:
                    if entity == url:
                        c = copy.deepcopy(features)
                        c['truerelation'] = -1
                        c['trueentity'] = 1
                        c['url'] = url
                        trainindata.append(c)

for item,golditem in zip(d,gold):
    if len(item) == 0:
        continue
    item = item[1]
    if len(item) == 0:
        continue
    for chunknum,urldicts in item['rerankedlists'].iteritems():
        for urldict in urldicts:
            features = urldict[1][1]
            url = urldict[1][0]
            if 'P' in url:
                for relation in golditem['relations']:
                    if relation != url:
                        c = copy.deepcopy(features)
                        c['truerelation'] = 0
                        c['trueentity'] = -1
                        c['url'] = url
                        trainindata.append(c) 
                        break

            else:
                for entity in golditem['entities']:
                    if entity != url:
                        c = copy.deepcopy(features)
                        c['truerelation'] = -1
                        c['trueentity'] = 0
                        c['url'] = url
                        trainindata.append(c)
                        break


f = open('reranktrain2.json','w')
f.write(json.dumps(trainindata,  indent=4, sort_keys=True))
f.close()


