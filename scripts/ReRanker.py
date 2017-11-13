#!/usr/bin/python

import numpy as np
import xgboost as xgb
import sys

class ReRanker:
    def __init__(self):
        print "ReRanker initializing"
        try:
            self.model = xgb.Booster({'nthread': 4})
            self.model.load_model('../models/db_predia_reranker.model')            
        except Exception,e:
            print e
            sys.exit(1)
        print "ReRanker initialized"


    def reRank(self, topklists):
        rerankedlists = {}
        for k1,v1 in topklists['nodefeatures'].iteritems():
            if k1 == 'chunktext' or k1 == 'ertypes':
                continue
            uris = []
            featurevectors = []
            for k2,v2 in v1.iteritems():
                uris.append(k2)
                featurevectors.append([v2['connections'],v2['sumofhops'],v2['esrank']])
            featurevectors = np.array(featurevectors)
            dtest = xgb.DMatrix(featurevectors)
            predictions = self.model.predict(dtest)
            l = [(float(p),u) for p,u in zip(predictions,uris)]
            rerankedlists[k1] = sorted(l, key=lambda x: x[0], reverse=True)
        return {'rerankedlists': rerankedlists, 'chunktext':topklists['chunktext'], 'ertypes': topklists['ertypes']}
                
if __name__ == '__main__':
    r = ReRanker()
    print r.reRank({'chunktext': ['obama', 'mother'], 'nodefeatures': {0: {u'http://dbpedia.org/resource/Odama': {'connections': 0.0, 'esrank': 19, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Okama': {'connections': 0.0, 'esrank': 22, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Obama:_From_Promise_to_Power': {'connections': 0.0, 'esrank': 13, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Bama,_Nigeria': {'connections': 0.0, 'esrank': 41, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Mr._Obama': {'connections': 0.0, 'esrank': 1, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Tropical_Cyclone_Nisha-Orama': {'connections': 0.0, 'esrank': 32, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Obama_(surname)': {'connections': 0.0, 'esrank': 4, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Obama_Doctrine': {'connections': 0.0, 'esrank': 46, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Ohama': {'connections': 0.0, 'esrank': 17, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Obala': {'connections': 0.0, 'esrank': 26, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Oyama,_Shizuoka': {'connections': 0.0, 'esrank': 31, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Oyama,_British_Columbia': {'connections': 0.0, 'esrank': 34, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Obama-mania': {'connections': 0.0, 'esrank': 11, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Obata,_Mie': {'connections': 0.0, 'esrank': 36, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Shut_up_your_mouse,_Obama': {'connections': 0.0, 'esrank': 6, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Pan-orama': {'connections': 0.0, 'esrank': 30, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Obama,_Fukui': {'connections': 0.0, 'esrank': 12, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/President_Obama_on_Death_of_Osama_bin_Laden_(SPOOF)': {'connections': 0.0, 'esrank': 15, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Mount_Obama': {'connections': 0.0, 'esrank': 50, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Obara,_Aichi': {'connections': 0.0, 'esrank': 33, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Omama,_Gunma': {'connections': 0.0, 'esrank': 35, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Barack_Obama': {'connections': 0.5, 'esrank': 47, 'sumofhops': 0.75}, u'http://dbpedia.org/resource/Oboama': {'connections': 0.0, 'esrank': 28, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Obama_Academy': {'connections': 0.0, 'esrank': 45, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Obara': {'connections': 0.0, 'esrank': 18, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Mbama': {'connections': 0.0, 'esrank': 25, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Obama,_Nagasaki': {'connections': 0.0, 'esrank': 9, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Hedges_v._Obama': {'connections': 0.0, 'esrank': 7, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Obata': {'connections': 0.0, 'esrank': 23, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Otama': {'connections': 0.0, 'esrank': 20, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Bama,_Burkina_Faso': {'connections': 0.0, 'esrank': 39, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Obava': {'connections': 0.0, 'esrank': 21, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Obama,_Sarah': {'connections': 0.0, 'esrank': 14, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Obama_(disambiguation)': {'connections': 0.0, 'esrank': 3, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Klayman_v._Obama': {'connections': 0.0, 'esrank': 5, 'sumofhops': 0.0}, u"http://dbpedia.org/resource/Osama\u2014Yo'_Mama:_The_Album": {'connections': 0.0, 'esrank': 40, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Obama_chmo': {'connections': 0.0, 'esrank': 48, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Obama_BasedGod': {'connections': 0.0, 'esrank': 51, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Obama\u2013Medvedev_Commission': {'connections': 0.0, 'esrank': 10, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Obama_(genus)': {'connections': 0.0, 'esrank': 8, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Al-Haramain_v._Obama': {'connections': 0.0, 'esrank': 2, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Oyama': {'connections': 0.0, 'esrank': 16, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Felicidad_(Margherita)': {'connections': 0.0, 'esrank': 24, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Bama': {'connections': 0.0, 'esrank': 29, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Obaba': {'connections': 0.0, 'esrank': 27, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Obama_Mama': {'connections': 0.0, 'esrank': 44, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Obama_logo': {'connections': 0.0, 'esrank': 43, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Oyama,_Tochigi': {'connections': 0.0, 'esrank': 37, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Flora-Bama': {'connections': 0.0, 'esrank': 38, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Obama_Domain': {'connections': 0.0, 'esrank': 42, 'sumofhops': 0.0}, u'http://dbpedia.org/resource/Back_Obama': {'connections': 0.0, 'esrank': 49, 'sumofhops': 0.0}}, 1: {u'http://dbpedia.org/property/father': {'connections': 0.0, 'esrank': 3, 'sumofhops': 0.0}, u'http://dbpedia.org/property/mothert': {'connections': 0.0, 'esrank': 8, 'sumofhops': 0.0}, u'http://dbpedia.org/property/mather': {'connections': 0.0, 'esrank': 9, 'sumofhops': 0.0}, u'http://dbpedia.org/property/father,Mother': {'connections': 0.0, 'esrank': 2, 'sumofhops': 0.0}, u'http://dbpedia.org/property/mmaOther': {'connections': 0.0, 'esrank': 6, 'sumofhops': 0.0}, u'http://dbpedia.org/property/mother/father': {'connections': 0.0, 'esrank': 1, 'sumofhops': 0.0}, u'http://dbpedia.org/property/mother': {'connections': 0.0, 'esrank': 4, 'sumofhops': 0.0}, u'http://dbpedia.org/property/mother%60sName': {'connections': 0.0, 'esrank': 7, 'sumofhops': 0.0}, u'http://dbpedia.org/property/other': {'connections': 0.5, 'esrank': 10, 'sumofhops': 0.75}, u'http://dbpedia.org/property/%5Dother': {'connections': 0.0, 'esrank': 5, 'sumofhops': 0.0}, u'http://dbpedia.org/ontology/other': {'connections': 0.0, 'esrank': 11, 'sumofhops': 0.0}}}})
