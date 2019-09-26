import sys,os,json,re
from elasticsearch import Elasticsearch


es = Elasticsearch() 
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
    unit['question'] = item['question']
    gold.append(unit)

f = open('erspanjointrerankerparseout2.json')
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
    unit = {}
    if len(queryitem) == 0:
        continue
    unit['question'] = golditem['question']
    unit['goldentitynotfound'] = []
    unit['chunks'] = []
    queryentities = []
    queryrelations = []
    if 'rerankedlists' in queryitem[0]:
        found = False
        for goldent in golditem['entities']:
            for num,urltuples in queryitem[0]['rerankedlists'].iteritems():
                if queryitem[0]['chunktext'][int(num)]['chunk'] not in unit['chunks']:
                    unit['chunks'].append((queryitem[0]['chunktext'][int(num)]['chunk'],queryitem[0]['rerankedlists'][num][0][1][0]))
                if queryitem[0]['chunktext'][int(num)]['class'] == 'entity':
                    if goldent in [urltuple[1][0] for urltuple in urltuples]:
                       found = True
            if not found:
                unit['goldentitynotfound'].append((goldent, [rec['_source']['wikidataLabel'] for rec in es.search(index="wikidataentitylabelindex01", body={"query":{"term":{"uri":goldent}}})['hits']['hits']]))
                print(json.dumps(unit,indent=4, sort_keys=True))
              
#                urllabels = []
#                for urltuple in urltuples:
#                    res = es.search(index="wikidataentitylabelindex01", body={"query":{"term":{"uri":urltuple[1][0]}}})
#                    for rec in res['hits']['hits']:
#                        urllabels.append((urltuple[1][0],rec['_source']['wikidataLabel']))
#                print(golditem['question'],queryitem[0]['chunktext'][int(num)]['chunk'],urllabels,golditem['entities'],'entity')
#            if  queryitem[0]['chunktext'][int(num)]['class'] == 'relation':
#                print(golditem['question'],queryitem[0]['chunktext'][int(num)]['chunk'],[urltuple[1][0] for urltuple in urltuples],golditem['relations'],'relation')
#                for urltuple in urltuples:
#                    if '_' in urltuple[1][0]:
#                        relid = urltuple[1][0].split('http://www.wikidata.org/entity/')[1].split('_')[0]
#                        qualid = urltuple[1][0].split('http://www.wikidata.org/entity/')[1].split('_')[1]
#                        queryrelations.append('http://www.wikidata.org/entity/'+relid)
#                        queryrelations.append('http://www.wikidata.org/entity/'+qualid)
#                    else:
#                        queryrelations.append(urltuple[1][0])
#                    break

