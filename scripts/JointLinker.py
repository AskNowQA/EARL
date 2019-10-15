#!/usr/bin/python

import json,sys
import itertools
from operator import itemgetter
from pybloom import ScalableBloomFilter
import glob

class JointLinker:
    def __init__(self):
        print "Joint Linker initializing"
        self.bloom2hoppreds = []
        try:
            f = open('../data/blooms/wikidatabloom1hoppredicate.pickle')
            self.bloom1hoppred = ScalableBloomFilter.fromfile(f)
            f.close()
            f = open('../data/blooms/wikidatabloom1.5hopqualifiers.pickle')
            self.bloomqualifier = ScalableBloomFilter.fromfile(f) # ihoppred_qualifier
            f.close()
            f = open('../data/blooms/wikidatabloom1hopentity.pickle')
            self.bloom1hopentity = ScalableBloomFilter.fromfile(f)
            f.close()
            f = open('../data/blooms/bloom1hoptypeofentity.pickle')
            self.bloom1hoptypeofentity = ScalableBloomFilter.fromfile(f)
            f.close()
#            f = open('../data/blooms/bloom2hoptypeofentity.pickle')
#            self.bloom2hoptypeofentity = BloomFilter.fromfile(f)
#            f.close()
#            twohoppredpaths = glob.glob('../data/blooms/bloom2hoppredicate*.pickle')
#            for twohoppredpath in twohoppredpaths:
#                f = open(twohoppredpath)
#                self.bloom2hoppreds.append(BloomFilter.fromfile(f))
#                f.close()
        except Exception,e:
            print e
            sys.exit(1)
        print "Joint Linker initialized"

    def filter(self, entities, relations):
        filteredrelations = []
        added = {}
        for entity in entities:
            for relation in relations:
                if relation['uri'] in added:
                    continue
                bloomstring = entity['uri'] + ':' + relation['uri']
                if bloomstring in self.bloom1hoppred or bloomstring in self.bloomqualifier or bloomstring in self.bloom1hoptypeofentity:
                    filteredrelations.append(relation)
                    added[relation['uri']] = None
        return filteredrelations
                

    def jointLinker(self, entitiesandrelations):
        entities = entitiesandrelations['entities']
        relations = entitiesandrelations['relations']
        nodestats = {}
        rank = 1
        for entity in entities:
            nodestats[entity['uri']] = {'connections':0, 'entrelconnections': 0, 'ententconnections':0, 'sumofhops': 0, 'rank': rank}
            rank += 1
        connectedrelations = self.filter(entities, relations) #reject any relations that are not connected to the entities
        print(len(entities))
        print(len(relations),len(connectedrelations))
        for entity1 in entities:
            for entity2 in entities:
                if entity1 == entity2:
                    continue
                bloomstring = entity1['uri'] + ':' + entity2['uri']
                if bloomstring in self.bloom1hopentity:
                    nodestats[entity1['uri']]['connections'] += 1
                    nodestats[entity1['uri']]['ententconnections'] += 1
                    nodestats[entity1['uri']]['sumofhops'] += 1
                    nodestats[entity2['uri']]['connections'] += 1
                    nodestats[entity2['uri']]['ententconnections'] += 1
                    nodestats[entity2['uri']]['sumofhops'] += 1
                if bloomstring in self.bloom1hoptypeofentity:
                    nodestats[entity1['uri']]['connections'] += 1
                    nodestats[entity1['uri']]['entrelconnections'] += 1
                    nodestats[entity1['uri']]['sumofhops'] += 1
                    nodestats[entity2['uri']]['connections'] += 1
                    nodestats[entity2['uri']]['entrelconnections'] += 1
                    nodestats[entity2['uri']]['sumofhops'] += 1 
            for relation in connectedrelations:
                bloomstring = entity1['uri'] + ':' + relation['uri']
                if bloomstring in self.bloom1hoppred:
                    nodestats[entity1['uri']]['connections'] += 1
                    nodestats[entity1['uri']]['entrelconnections'] += 1
                    nodestats[entity1['uri']]['sumofhops'] += 0.5
                if bloomstring in self.bloomqualifier:
                    nodestats[entity1['uri']]['connections'] += 1
                    nodestats[entity1['uri']]['entrelconnections'] += 1
                    nodestats[entity1['uri']]['sumofhops'] += 1.5
                if bloomstring in self.bloom1hoptypeofentity:
                    nodestats[entity1['uri']]['connections'] += 1
                    nodestats[entity1['uri']]['entrelconnections'] += 1
                    nodestats[entity1['uri']]['sumofhops'] += 1
        #Normalisation
        maxrank = max([v['rank'] for k,v in nodestats.iteritems()])
        maxconnections = max([v['connections'] for k,v in nodestats.iteritems()]) 
        maxententconnections = max([v['ententconnections'] for k,v in nodestats.iteritems()])
        maxsumofhops = max([v['sumofhops'] for k,v in nodestats.iteritems()])
        maxentrelconnections =  max([v['entrelconnections'] for k,v in nodestats.iteritems()])
        for k,v in nodestats.iteritems():
            nodestats[k]['rank'] /= float(maxrank)
            nodestats[k]['connections'] /= float(maxconnections)
            nodestats[k]['ententconnections'] /= float(maxententconnections)
            nodestats[k]['sumofhops'] /= float(maxsumofhops)
            nodestats[k]['entrelconnections'] /= float(maxentrelconnections)
        return nodestats
#        for k1,v1 in nodestats.iteritems():
#            for k2,v2 in v1.iteritems():
#                nodestats[k1][k2]['connections'] /= float(len(lists))
#                nodestats[k1][k2]['sumofhops'] /= float(len(lists))
#            
#        return {'nodefeatures': nodestats, 'chunktext': chunktexts, 'ertypes': ertypes}
    

if __name__ == '__main__':
    j = JointLinker()
    print(json.dumps(j.jointLinker({"entities": [{"ngram": "the president", "uri": "http://wikidata.dbpedia.org/resource/Q313383"}, {"ngram": "president of India", "uri": "http://wikidata.dbpedia.org/resource/Q313383"}, {"ngram": "is the president", "uri": "http://wikidata.dbpedia.org/resource/Q313383"}, {"ngram": "is the president", "uri": "http://wikidata.dbpedia.org/resource/Q11335839"}, {"ngram": "the president of", "uri": "http://wikidata.dbpedia.org/resource/Q11335839"}, {"ngram": "is the president", "uri": "http://wikidata.dbpedia.org/resource/Q30461"}, {"ngram": "president of India", "uri": "http://wikidata.dbpedia.org/resource/Q7758087"}, {"ngram": "the president of", "uri": "http://wikidata.dbpedia.org/resource/Q30461"}, {"ngram": "president of India", "uri": "http://wikidata.dbpedia.org/resource/Q7758077"}, {"ngram": "of India ?", "uri": "http://wikidata.dbpedia.org/resource/Q1488929"}, {"ngram": "president of India", "uri": "http://wikidata.dbpedia.org/resource/Q7758079"}, {"ngram": "the president of", "uri": "http://wikidata.dbpedia.org/resource/Q313383"}, {"ngram": "president of India", "uri": "http://wikidata.dbpedia.org/resource/Q3795258"}, {"ngram": "president of India", "uri": "http://wikidata.dbpedia.org/resource/Q17021600"}, {"ngram": "president of India", "uri": "http://wikidata.dbpedia.org/resource/Q41819799"}, {"ngram": "Who is the", "uri": "http://wikidata.dbpedia.org/resource/Q2733064"}, {"ngram": "president of India", "uri": "http://wikidata.dbpedia.org/resource/Q2980956"}, {"ngram": "the president of", "uri": "http://wikidata.dbpedia.org/resource/Q1255921"}, {"ngram": "president of India", "uri": "http://wikidata.dbpedia.org/resource/Q17141344"}, {"ngram": "is the president", "uri": "http://wikidata.dbpedia.org/resource/Q1255921"}, {"ngram": "president of India", "uri": "http://wikidata.dbpedia.org/resource/Q52419014"}, {"ngram": "president of India", "uri": "http://wikidata.dbpedia.org/resource/Q7758085"}, {"ngram": "the president", "uri": "http://wikidata.dbpedia.org/resource/Q11335839"}, {"ngram": "president of India", "uri": "http://wikidata.dbpedia.org/resource/Q24043569"}, {"ngram": "president of India", "uri": "http://wikidata.dbpedia.org/resource/Q18393664"}, {"ngram": "president of", "uri": "http://wikidata.dbpedia.org/resource/Q3226054"}, {"ngram": "president of", "uri": "http://wikidata.dbpedia.org/resource/Q11335839"}, {"ngram": "the president of", "uri": "http://wikidata.dbpedia.org/resource/Q3226054"}, {"ngram": "president of India", "uri": "http://wikidata.dbpedia.org/resource/Q3226054"}, {"ngram": "Who is the", "uri": "http://wikidata.dbpedia.org/resource/Q733532"}, {"ngram": "Who is", "uri": "http://wikidata.dbpedia.org/resource/Q2733064"}, {"ngram": "president of India", "uri": "http://wikidata.dbpedia.org/resource/Q7758086"}, {"ngram": "of India ?", "uri": "http://wikidata.dbpedia.org/resource/Q17055962"}, {"ngram": "Who is", "uri": "http://wikidata.dbpedia.org/resource/Q733532"}, {"ngram": "is the president", "uri": "http://wikidata.dbpedia.org/resource/Q3226054"}, {"ngram": "the president of", "uri": "http://wikidata.dbpedia.org/resource/Q7758087"}, {"ngram": "president of", "uri": "http://wikidata.dbpedia.org/resource/Q7758077"}, {"ngram": "president of", "uri": "http://wikidata.dbpedia.org/resource/Q7758079"}, {"ngram": "president of", "uri": "http://wikidata.dbpedia.org/resource/Q3795258"}, {"ngram": "president of", "uri": "http://wikidata.dbpedia.org/resource/Q18393664"}, {"ngram": "the president of", "uri": "http://wikidata.dbpedia.org/resource/Q52419014"}, {"ngram": "president of", "uri": "http://wikidata.dbpedia.org/resource/Q2980956"}, {"ngram": "president of", "uri": "http://wikidata.dbpedia.org/resource/Q24043569"}, {"ngram": "president of", "uri": "http://wikidata.dbpedia.org/resource/Q17141344"}, {"ngram": "president", "uri": "http://wikidata.dbpedia.org/resource/Q11335839"}, {"ngram": "of India ?", "uri": "http://wikidata.dbpedia.org/resource/Q22043425"}, {"ngram": "is the president", "uri": "http://wikidata.dbpedia.org/resource/Q7758087"}, {"ngram": "India ?", "uri": "http://wikidata.dbpedia.org/resource/Q1488929"}, {"ngram": "the president of", "uri": "http://wikidata.dbpedia.org/resource/Q17021600"}, {"ngram": "the president", "uri": "http://wikidata.dbpedia.org/resource/Q30461"}, {"ngram": "the president", "uri": "http://wikidata.dbpedia.org/resource/Q3226054"}, {"ngram": "president of", "uri": "http://wikidata.dbpedia.org/resource/Q30461"}, {"ngram": "is the president", "uri": "http://wikidata.dbpedia.org/resource/Q52419014"}, {"ngram": "of India ?", "uri": "http://wikidata.dbpedia.org/resource/Q11157534"}, {"ngram": "of India", "uri": "http://wikidata.dbpedia.org/resource/Q1488929"}, {"ngram": "the president of", "uri": "http://wikidata.dbpedia.org/resource/Q7241206"}, {"ngram": "is the president", "uri": "http://wikidata.dbpedia.org/resource/Q7241206"}, {"ngram": "the president", "uri": "http://wikidata.dbpedia.org/resource/Q1255921"}, {"ngram": "president of", "uri": "http://wikidata.dbpedia.org/resource/Q1255921"}, {"ngram": "president of", "uri": "http://wikidata.dbpedia.org/resource/Q313383"}, {"ngram": "the president of", "uri": "http://wikidata.dbpedia.org/resource/Q41819799"}, {"ngram": "is the president", "uri": "http://wikidata.dbpedia.org/resource/Q18344422"}, {"ngram": "is the president", "uri": "http://wikidata.dbpedia.org/resource/Q18615398"}, {"ngram": "is the president", "uri": "http://wikidata.dbpedia.org/resource/Q19886321"}, {"ngram": "is the president", "uri": "http://wikidata.dbpedia.org/resource/Q493203"}, {"ngram": "the president of", "uri": "http://wikidata.dbpedia.org/resource/Q18393664"}, {"ngram": "is the president", "uri": "http://wikidata.dbpedia.org/resource/Q7241203"}, {"ngram": "president", "uri": "http://wikidata.dbpedia.org/resource/Q30461"}, {"ngram": "is the president", "uri": "http://wikidata.dbpedia.org/resource/Q7241204"}, {"ngram": "is the president", "uri": "http://wikidata.dbpedia.org/resource/Q7241205"}, {"ngram": "of India", "uri": "http://wikidata.dbpedia.org/resource/Q17055962"}, {"ngram": "is the president", "uri": "http://wikidata.dbpedia.org/resource/Q37504420"}, {"ngram": "is the president", "uri": "http://wikidata.dbpedia.org/resource/Q1175634"}, {"ngram": "the president", "uri": "http://wikidata.dbpedia.org/resource/Q7241206"}, {"ngram": "the president of", "uri": "http://wikidata.dbpedia.org/resource/Q18344422"}, {"ngram": "is the president", "uri": "http://wikidata.dbpedia.org/resource/Q7241202"}, {"ngram": "the president of", "uri": "http://wikidata.dbpedia.org/resource/Q18615398"}, {"ngram": "the president of", "uri": "http://wikidata.dbpedia.org/resource/Q19886321"}, {"ngram": "the president of", "uri": "http://wikidata.dbpedia.org/resource/Q493203"}, {"ngram": "is the president", "uri": "http://wikidata.dbpedia.org/resource/Q18393664"}, {"ngram": "the president of", "uri": "http://wikidata.dbpedia.org/resource/Q7241203"}, {"ngram": "the president of", "uri": "http://wikidata.dbpedia.org/resource/Q7241204"}, {"ngram": "the president of", "uri": "http://wikidata.dbpedia.org/resource/Q7241205"}, {"ngram": "the president of", "uri": "http://wikidata.dbpedia.org/resource/Q37504420"}, {"ngram": "president of India", "uri": "http://wikidata.dbpedia.org/resource/Q11335839"}, {"ngram": "the president of", "uri": "http://wikidata.dbpedia.org/resource/Q1175634"}, {"ngram": "the president of", "uri": "http://wikidata.dbpedia.org/resource/Q7241202"}, {"ngram": "is the president", "uri": "http://wikidata.dbpedia.org/resource/Q3046471"}, {"ngram": "president of India", "uri": "http://wikidata.dbpedia.org/resource/Q7241206"}, {"ngram": "the president of", "uri": "http://wikidata.dbpedia.org/resource/Q24043569"}, {"ngram": "the president of", "uri": "http://wikidata.dbpedia.org/resource/Q7758085"}, {"ngram": "the president of", "uri": "http://wikidata.dbpedia.org/resource/Q3046471"}, {"ngram": "president of", "uri": "http://wikidata.dbpedia.org/resource/Q7241206"}, {"ngram": "is the president", "uri": "http://wikidata.dbpedia.org/resource/Q24043569"}, {"ngram": "is the president", "uri": "http://wikidata.dbpedia.org/resource/Q16980517"}, {"ngram": "India ?", "uri": "http://wikidata.dbpedia.org/resource/Q17055962"}, {"ngram": "president of India", "uri": "http://wikidata.dbpedia.org/resource/Q18344422"}, {"ngram": "president of India", "uri": "http://wikidata.dbpedia.org/resource/Q30461"}, {"ngram": "president of India", "uri": "http://wikidata.dbpedia.org/resource/Q1255921"}, {"ngram": "of India ?", "uri": "http://wikidata.dbpedia.org/resource/Q17055987"}], "question": "Who is the president of India ?", "relations": [{"ngram": "president of", "uri": "http://www.wikidata.org/entity/P1037_P642"}, {"ngram": "president of", "uri": "http://www.wikidata.org/entity/P57_P642"}, {"ngram": "is the", "uri": "http://www.wikidata.org/entity/P3450_P156"}, {"ngram": "the president of", "uri": "http://www.wikidata.org/entity/P1344_P3320"}, {"ngram": "president", "uri": "http://www.wikidata.org/entity/P6_P805"}, {"ngram": "president", "uri": "http://www.wikidata.org/entity/P488_P805"}, {"ngram": "president", "uri": "http://www.wikidata.org/entity/P35_P805"}, {"ngram": "is the president", "uri": "http://www.wikidata.org/entity/P460_P582"}, {"ngram": "the president of", "uri": "http://www.wikidata.org/entity/P485_P361"}, {"ngram": "president of", "uri": "http://www.wikidata.org/entity/P488_P27"}, {"ngram": "the president of", "uri": "http://www.wikidata.org/entity/P485_P527"}]}),  indent=4, sort_keys=True))
