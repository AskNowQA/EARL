#!/usr/bin/python


import sys
from sets import Set
from pybloom import BloomFilter
import redis

reload(sys)
sys.setdefaultencoding('utf8')

d = {}
red = redis.StrictRedis(host='localhost', port=6379, db=0)
bloom  = BloomFilter(capacity=200000000, error_rate=0.000001)
f = open(sys.argv[1])
count = 0
red.set('linesread3',0)
for line in f.readlines():
    if count == 0:
        count += 1
        continue
    line = line.strip()
    red.incr('linesread3')
    try:
        s,p,o = line.split(' ')
        if p == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
            if s not in d:
                d[s] = Set()
                d[s].add(o)
            else:
                d[s].add(o)
    except Exception,e:
        print line,e
    count += 1
f.close()
f = open(sys.argv[1])

red.set('linesread3',0)
for line in f.readlines():
    if count == 0:
        count += 1
        continue
    line = line.strip()
    try:
        red.incr('linesread3')
        s,p,o = line.split(' ')
        if s in d:
            for sub in d[s]:
                bloom.add(o+':'+sub)
        if o in d:
            for sub in d[o]:
                bloom.add(s+':'+sub)
    except Exception,e:
        print line,e

f.close()

print "Testing bloom"

if "http://dbpedia.org/resource/Bill_Finger:http://dbpedia.org/ontology/ComicsCharacter" in bloom:
    print "Test passed"



f = open('/data/debayan/blooms/bloom2hoptypeofentity.pickle','w')
bloom.tofile(f)
f.close()
