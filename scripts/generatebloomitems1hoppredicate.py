#!/usr/bin/python


import sys
from sets import Set
from pybloom import BloomFilter
import redis

reload(sys)
sys.setdefaultencoding('utf8')

red = redis.StrictRedis(host='localhost', port=6379, db=0)
red.set('linesread5',0)
bloom  = BloomFilter(capacity=200000000, error_rate=0.000001)
f = open(sys.argv[1])
count = 0
for line in f.readlines():
    if count == 0:
        count += 1
        continue
    line = line.strip()
    try:
        red.incr('linesread5')
        s,p,o = line.split(' ')
        struri1 = s+':'+p
        struri2 = o+':'+p
        bloom.add(struri1)
        bloom.add(struri2)
    except Exception,e:
        print e
f.close()

f = open('/data/debayan/blooms/bloom1hoppredicate.pickle','w')
bloom.tofile(f)
f.close()
