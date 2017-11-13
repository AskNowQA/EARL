#!/usr/bin/python

import json,sys
import itertools
from operator import itemgetter
from pybloom import BloomFilter


class JointLinker:
    def __init__(self):
        print "Joint Linker initializing"
        try:
            f = open('../data/blooms/bloom1hoppredicate.pickle')
            self.bloom1hoppred = BloomFilter.fromfile(f)
            f.close()
            f = open('../data/blooms/bloom1hopentity.pickle')
            self.bloom1hopentity = BloomFilter.fromfile(f)
            f.close()
            f = open('../data/blooms/bloom2hoppredicate.pickle')
            self.bloom2hoppredicate = BloomFilter.fromfile(f)
            f.close()
            f = open('../data/blooms/bloom2hoptypeofentity.pickle')
            self.bloom2hoptypeofentity = BloomFilter.fromfile(f)
            f.close()
        except Exception,e:
            print e
            sys.exit(1)
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
            for uri in listt:
                rank += 1
                if count not in nodestats:
                    nodestats[count] = {}
                if uri not in nodestats[count]:
                    nodestats[count][uri] = {'connections':0, 'sumofhops':0, 'esrank': rank}
            count += 1
        for permutation in itertools.permutations(sequence, 2):
            for uri1 in lists[permutation[0]]:
                for uri2 in lists[permutation[1]]:
                    bloomstring = uri1+':'+uri2
                    if bloomstring in self.bloom1hoppred:
                        nodestats[permutation[0]][uri1]['connections'] += 1
                        nodestats[permutation[0]][uri1]['sumofhops'] += 0.5
                        nodestats[permutation[1]][uri2]['connections'] += 1
                        nodestats[permutation[1]][uri2]['sumofhops'] += 0.5
                    elif bloomstring in self.bloom1hopentity:
                        nodestats[permutation[0]][uri1]['connections'] += 1
                        nodestats[permutation[0]][uri1]['sumofhops'] += 1
                        nodestats[permutation[1]][uri2]['connections'] += 1
                        nodestats[permutation[1]][uri2]['sumofhops'] += 1
                    elif bloomstring in self.bloom2hoppredicate:
                        nodestats[permutation[0]][uri1]['connections'] += 1
                        nodestats[permutation[0]][uri1]['sumofhops'] += 1.5
                        nodestats[permutation[1]][uri2]['connections'] += 1
                        nodestats[permutation[1]][uri2]['sumofhops'] += 1.5
                    elif bloomstring in self.bloom2hoptypeofentity:
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
    print j.jointLinker([{'chunk': 'obama', 'class': 'entity', 'topkmatches': [u'http://dbpedia.org/resource/Mr._Obama', u'http://dbpedia.org/resource/Al-Haramain_v._Obama', u'http://dbpedia.org/resource/Obama_(disambiguation)', u'http://dbpedia.org/resource/Obama_(surname)', u'http://dbpedia.org/resource/Klayman_v._Obama', u'http://dbpedia.org/resource/Shut_up_your_mouse,_Obama', u'http://dbpedia.org/resource/Hedges_v._Obama', u'http://dbpedia.org/resource/Obama_(genus)', u'http://dbpedia.org/resource/Obama,_Nagasaki', u'http://dbpedia.org/resource/Obama\u2013Medvedev_Commission', u'http://dbpedia.org/resource/Obama-mania', u'http://dbpedia.org/resource/Obama,_Fukui', u'http://dbpedia.org/resource/Obama:_From_Promise_to_Power', u'http://dbpedia.org/resource/Obama,_Sarah', u'http://dbpedia.org/resource/President_Obama_on_Death_of_Osama_bin_Laden_(SPOOF)', u'http://dbpedia.org/resource/Oyama', u'http://dbpedia.org/resource/Ohama', u'http://dbpedia.org/resource/Obara', u'http://dbpedia.org/resource/Odama', u'http://dbpedia.org/resource/Otama', u'http://dbpedia.org/resource/Obava', u'http://dbpedia.org/resource/Okama', u'http://dbpedia.org/resource/Obata', u'http://dbpedia.org/resource/Felicidad_(Margherita)', u'http://dbpedia.org/resource/Mbama', u'http://dbpedia.org/resource/Obala', u'http://dbpedia.org/resource/Obaba', u'http://dbpedia.org/resource/Oboama', u'http://dbpedia.org/resource/Bama', u'http://dbpedia.org/resource/Pan-orama', u'http://dbpedia.org/resource/Oyama,_Shizuoka', u'http://dbpedia.org/resource/Tropical_Cyclone_Nisha-Orama', u'http://dbpedia.org/resource/Obara,_Aichi', u'http://dbpedia.org/resource/Oyama,_British_Columbia', u'http://dbpedia.org/resource/Omama,_Gunma', u'http://dbpedia.org/resource/Obata,_Mie', u'http://dbpedia.org/resource/Oyama,_Tochigi', u'http://dbpedia.org/resource/Flora-Bama', u'http://dbpedia.org/resource/Bama,_Burkina_Faso', u"http://dbpedia.org/resource/Osama\u2014Yo'_Mama:_The_Album", u'http://dbpedia.org/resource/Bama,_Nigeria', u'http://dbpedia.org/resource/Obama_Domain', u'http://dbpedia.org/resource/Obama_logo', u'http://dbpedia.org/resource/Obama_Mama', u'http://dbpedia.org/resource/Obama_Academy', u'http://dbpedia.org/resource/Obama_Doctrine', u'http://dbpedia.org/resource/Barack_Obama', u'http://dbpedia.org/resource/Obama_chmo', u'http://dbpedia.org/resource/Back_Obama', u'http://dbpedia.org/resource/Mount_Obama', u'http://dbpedia.org/resource/Obama_BasedGod']}, {'chunk': 'mother', 'class': 'relation', 'topkmatches': [u'http://dbpedia.org/property/mother/father', u'http://dbpedia.org/property/father,Mother', u'http://dbpedia.org/property/father', u'http://dbpedia.org/property/mother', u'http://dbpedia.org/property/%5Dother', u'http://dbpedia.org/property/mmaOther', u'http://dbpedia.org/property/mother%60sName', u'http://dbpedia.org/property/mothert', u'http://dbpedia.org/property/mather', u'http://dbpedia.org/property/other', u'http://dbpedia.org/ontology/other']}])
     
        
