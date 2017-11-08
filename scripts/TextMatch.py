#!/usr/bin/python

import sys
from sets import Set
from elasticsearch import Elasticsearch

class TextMatch:
    def __init__(self):
        print "TextMatch initializing"
        try:
            self.es = Elasticsearch()
        except Exception,e:
            print e
            sys.exit(1)            
        print "TextMatch initialized"

    def textMatch(self, chunks):
        matchedChunks = []
        for chunk in chunks:
             if chunk['class'] == 'entity':
                 res = self.es.search(index="dbentityindex9", doc_type="records", body={"query":{"match":{"_all":{"query":chunk['chunk'], "fuzziness":"auto"}}},"size":200})
                 topkents = []
                 for record in res['hits']['hits']:
                     if len(topkents) > 50:
                         break
                     if record['_source']['uri'] not in topkents:
                         topkents.append(record['_source']['uri'])
                 matchedChunks.append({'chunk':chunk['chunk'], 'topkmatches': topkents})
                 
                     
             if chunk['class'] == 'relation':
                 res = self.es.search(index="dbpredicateindex14", doc_type="records", body={"query":{"match":{"_all":{"query":chunk['chunk'], "fuzziness":"auto"}}},"size":200})
                 topkrels = []
                 for record in res['hits']['hits']:
                     if len(topkrels) > 50:
                         break
                     if record['_source']['uri'] not in topkrels:
                         topkrels.append(record['_source']['uri'])
                 matchedChunks.append({'chunk':chunk['chunk'], 'topkmatches': topkrels})
        return matchedChunks 
                          
                     


if __name__ == '__main__':
    t = TextMatch()
    print t.textMatch([{'chunk':'obama', 'class':'entity'}, {'chunk':'mother', 'class':'relation'}])
