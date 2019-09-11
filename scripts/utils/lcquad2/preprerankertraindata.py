import sys,os,json,re,copy

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


trainindata = []


d = json.loads(open('jointonlyparse1.json').read())

for item,golditem in zip(d,gold):
    if len(item) == 0:
        continue
    for chunknum,urldict in item['nodefeatures'].iteritems():
        for url,features in urldict.iteritems():
            if 'www.wikidata.org' in url: 
                if '_' in url:
                    relid = url.split('http://www.wikidata.org/entity/')[1].split('_')[0]
                    qualid = url.split('http://www.wikidata.org/entity/')[1].split('_')[1]
                    rel = 'http://www.wikidata.org/entity/'+relid
                    qual = 'http://www.wikidata.org/entity/'+qualid
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
    for chunknum,urldict in item['nodefeatures'].iteritems():
        for url,features in urldict.iteritems():
            if 'www.wikidata.org' in url:
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

f = open('reranktrain1.json','w')
f.write(json.dumps(trainindata,  indent=4, sort_keys=True))
f.close()


