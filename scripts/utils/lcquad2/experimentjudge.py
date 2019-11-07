import sys,os,json,re,itertools
from elasticsearch import Elasticsearch

es = Elasticsearch()

gold = []
f = open('/home/sda-srv05/debayan/LC-QuAD2.0/dataset/test.json')
d1 = json.loads(f.read())

d = sorted(d1, key=lambda x: int(x['uid']))

for item in d:
    wikisparql = item['sparql_wikidata']
    unit = {}
    unit['question'] = item['question']
    unit['uid'] = item['uid']
    _ents = re.findall( r'wd:(.*?) ', wikisparql)
    _rels = re.findall( r'wdt:(.*?) ',wikisparql)
    unit['entities'] = ['http://wikidata.dbpedia.org/resource/'+ent for ent in _ents]
    unit['relations'] = ['http://www.wikidata.org/entity/'+rel for rel in _rels]
    gold.append(unit)

f = open('erspan3.json')
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

wikiurilabeldict = json.loads(open('../../../data/wikiurilabeldict1.json').read())


def getlabels(urls):
    labels = []
    for url in urls:
         if 'entity' in url:
             if url in wikiurilabeldict:
                 labels.append([url,wikiurilabeldict[url]])
             else:
                 labels.append([url,[]])
         else:
             res = es.search(index="wikidataentitylabelindex01", body={"query":{"term":{"uri":url}},"size":100})
             for idx,hit in enumerate(res['hits']['hits']):
                labels.append([url,hit['_source']['wikidataLabel']])
    return labels

def seqconfrerank(queryitems):
    urlcombinations = []
    for queryitem in queryitems:
        freshurlslist = []
        if 'rerankedlists' in queryitem:
            for num,urltuples in queryitem['rerankedlists'].iteritems():
                if queryitem['chunktext'][int(num)]['class'] == 'entity':
                    querye = []
                    for urltuple in urltuples[:3]:
                        querye.append([urltuple[0],urltuple[1][0]])
                    freshurlslist.append(querye)
                if  queryitem['chunktext'][int(num)]['class'] == 'relation':
                    queryr = []
                    for urltuple in urltuples[:3]:
                        if '_' in urltuple[1][0]:
                            relid = urltuple[1][0].split('http://www.wikidata.org/entity/')[1].split('_')[0]
                            qualid = urltuple[1][0].split('http://www.wikidata.org/entity/')[1].split('_')[1]
                            queryr.append([urltuple[0],'http://www.wikidata.org/entity/'+relid])
                            queryr.append([urltuple[0],'http://www.wikidata.org/entity/'+qualid])
                        else:
                            queryr.append([urltuple[0],urltuple[1][0]])
                    freshurlslist.append(queryr)
        urlcombinations += list(itertools.product(*freshurlslist))
    besttup = []
    bestcon = 0
    for urls in urlcombinations:
        con = 0
        for url in urls:
            con += url[0]
        if len(urls) == 0:
            continue
        con /= float(len(urls))
        if con > bestcon:
            bestcon = con
            besttup = urls 
    return [x[1] for x in besttup]
        
        

for _queryitem,golditem in zip(d,gold):
    if len(_queryitem[1]) == 0:
        continue
    if _queryitem[0] != golditem['uid']:
        print('uid mismatch')
        sys.exit(1)
    bestqueryentities = []
    allqueryentities = []
    bestqueryrelations = []
    allqueryrelations = []
    bestconfidence = 0
    #siamqueryitems = siameserefine(_queryitem[1])
    seqreranked = seqconfrerank(_queryitem[1])
    for url in seqreranked:
        if 'entity' in url:
            allqueryrelations.append(url)
        else:
            allqueryentities.append(url)
    print("goldent: ",getlabels(golditem['entities']))
    print("goldrel: ",getlabels(golditem['relations']))
    print("queryent: ", getlabels(allqueryentities))
    print("queryrel: ", getlabels(allqueryrelations))
    print("question: ",golditem['question'])
    for goldentity in golditem['entities']:
        totalentchunks += 1
        if goldentity in allqueryentities:#bestqueryentities:
            tpentity += 1
        else:
            fnentity += 1
    for goldrelation in golditem['relations']:
        totalrelchunks += 1
        if goldrelation in allqueryrelations:#bestqueryrelations:
            tprelation += 1
        else:
            fnrelation += 1
    for queryentity in allqueryentities:
        if queryentity not in golditem['entities']:
            fpentity += 1
    for queryrelation in allqueryrelations:
        if queryrelation not in golditem['relations']:
            fprelation += 1

    try:
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
    except Exception as e:
        print(e)
sys.exit(1)
mrrent = 0
mrrrel = 0
faketotent = 0
faketotrel = 0

chunkingerror = 0
for queryitem,golditem in zip(d,gold):
    if len(queryitem[1]) == 0:
        continue
    if 'rerankedlists' in queryitem[1][0]:
        for num,urltuples in queryitem[1][0]['rerankedlists'].iteritems():
            if queryitem[1][0]['chunktext'][int(num)]['class'] == 'entity':
                for goldentity in golditem['entities']:
                    if goldentity in [urltuple[1][0] for urltuple in urltuples]:
                        mrrent += 1.0/float([urltuple[1][0] for urltuple in urltuples].index(goldentity)+1)
                        faketotent += 1
            if queryitem[1][0]['chunktext'][int(num)]['class'] == 'relation':
                queryrelations = []
                for urltuple in urltuples:
                    if '_' in urltuple[1][0]:
                        relid = urltuple[1][0].split('http://www.wikidata.org/entity/')[1].split('_')[0]
                        qualid = urltuple[1][0].split('http://www.wikidata.org/entity/')[1].split('_')[1]
                        queryrelations.append('http://www.wikidata.org/entity/'+relid)
                        queryrelations.append('http://www.wikidata.org/entity/'+qualid)
                    else: 
                        queryrelations.append(urltuple[1][0])
                for goldrelation in golditem['relations']:
                    if goldrelation in queryrelations:
                        mrrrel += 1.0/float(queryrelations.index(goldrelation)+1)
                        faketotrel += 1

totmrrent = mrrent/totalentchunks
totmrrrel = mrrrel/totalrelchunks
print('ent mrr = %f'%totmrrent)
print('rel mrr = %f'%totmrrrel)
faketotmrrent = mrrent/faketotent
faketotmrrrel = mrrrel/faketotrel
print('fake ent mrr = %f'%faketotmrrent)
print('fake rel mrr = %f'%faketotmrrrel)

presentent = 0
presentrel = 0
chunkingerror = 0
for queryitem,golditem in zip(d,gold):
    if len(queryitem[1]) == 0:
        continue
    for num,urltuples in queryitem[1][0]['rerankedlists'].iteritems():
        if queryitem[1][0]['chunktext'][int(num)]['class'] == 'entity':
            for goldentity in golditem['entities']:
                for urltuple in urltuples:
                    if urltuple[1][0] == goldentity:
                        presentent += 1
#        if queryitem[0]['chunktext'][int(num)]['class'] == 'relation':
#             queryrelations = []
#             for queryrelation in chunk['topkmatches']:
#                if '_' in queryrelation:
#                    relid = queryrelation.split('http://www.wikidata.org/entity/')[1].split('_')[0]
#                    qualid = queryrelation.split('http://www.wikidata.org/entity/')[1].split('_')[1]
#                    queryrelations.append('http://www.wikidata.org/entity/'+relid)
#                    queryrelations.append('http://www.wikidata.org/entity/'+qualid)
#                else:
#                    queryrelations.append(queryrelation)
#             for goldrelation in golditem['relations']:
#                if goldrelation in queryrelations:
#                    presentrel += 1


print('entity pipeline failure = %f'%((totalentchunks-presentent)/float(totalentchunks)))
#print('relation pipeline failure = %f'%((totalrelchunks-presentrel)/float(totalrelchunks)))




