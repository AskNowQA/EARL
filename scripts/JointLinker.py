#!/usr/bin/python

import json,sys
import itertools
from operator import itemgetter
import sparql

class JointLinker:
    def __init__(self):
        print "Joint Linker initializing"
        self.sparql = sparql.Service("https://query.wikidata.org/sparql", "utf-8", "GET")
        result = self.sparql.query("SELECT ?item ?itemLabel WHERE {  ?item wdt:P31 wd:Q146} LIMIT 1")
        print(result)
        print "Joint Linker initialized"

    

    def jointLinker(self, topklists):
        lists = []
        chunktexts = []
        ertypes = []
        for chunk in topklists:
            lists.append(chunk['topkmatches'])
            chunktexts.append(chunk['chunk']) 
            ertypes.append(chunk['class'])
        sequence = range(len(lists))
        nodestats = {}
        count = 0
        for listt in lists:
            rank = 0
            if count not in nodestats:
                nodestats[count] = {}
            for uri in listt:
                rank += 1
                if uri not in nodestats[count]:
                    nodestats[count][uri] = {'connections':0, 'sumofhops':0, 'esrank': rank}
            if len(nodestats[count]) == 0:
                nodestats[count]['null'] = {'connections':0, 'sumofhops':0, 'esrank': 100}
            count += 1
        for permutation in itertools.permutations(sequence, 2):
            for uri1 in lists[permutation[0]]:
                for uri2 in lists[permutation[1]]:
                    bloomstring = uri1+':'+uri2
                    if onehop(bloomstring):
                        nodestats[permutation[0]][uri1]['connections'] += 1
                        nodestats[permutation[0]][uri1]['sumofhops'] += 1
                        nodestats[permutation[1]][uri2]['connections'] += 1
                        nodestats[permutation[1]][uri2]['sumofhops'] += 1
                    elif twohop(bloomstring):
                        nodestats[permutation[0]][uri1]['connections'] += 1
                        nodestats[permutation[0]][uri1]['sumofhops'] += 2
                        nodestats[permutation[1]][uri2]['connections'] += 1
                        nodestats[permutation[1]][uri2]['sumofhops'] += 2
        for k1,v1 in nodestats.iteritems():
            for k2,v2 in v1.iteritems():
                nodestats[k1][k2]['connections'] /= float(len(lists))
                nodestats[k1][k2]['sumofhops'] /= float(len(lists))
            
        return {'nodefeatures': nodestats, 'chunktext': chunktexts, 'ertypes': ertypes}
    

if __name__ == '__main__':
    j = JointLinker()
#    print(json.dumps(j.jointLinker([{"chunk": {"chunk": "Who", "surfacelength": 3, "class": "entity", "surfacestart": 0}, "topkmatches": ["Q2733064", "Q733532", "Q16977164", "Q27813899", "Q53124717", "Q1195513", "Q3414362", "Q20656443", "Q6167261", "Q7997260", "Q7950337", "Q25105975", "Q226503", "Q311681", "Q398491", "Q7997129", "Q7997134", "Q39075948", "Q51152836", "Q93346", "Q53463028", "Q17162845", "Q16973457", "Q7950342", "Q7997130", "Q1164729", "Q1141238", "Q66683", "Q653011", "Q978993"], "class": "entity"}, {"chunk": {"chunk": "the parent organisation", "surfacelength": 23, "class": "relation", "surfacestart": 7}, "topkmatches": [], "class": "relation"}, {"chunk": {"chunk": "Barack Obama", "surfacelength": 12, "class": "entity", "surfacestart": 34}, "topkmatches": ["Q76", "Q47513588", "Q643049", "Q18562436", "Q8914982", "Q10352106", "Q50303833", "Q45111861", "Q4115068", "Q15982167", "Q1379733", "Q4858106", "Q21829530", "Q25957707", "Q7110357", "Q45112016", "Q18562442", "Q7838978", "Q31385", "Q649593", "Q4858104", "Q4858115", "Q21153049", "Q18562434", "Q8790887", "Q8532759", "Q39052299", "Q45112112", "Q8068634", "Q1305386"], "class": "entity"}, {"chunk": {"chunk": "is", "surfacelength": 2, "class": "relation", "surfacestart": 4}, "topkmatches": ["P155", "P921"], "class": "relation"}])))
