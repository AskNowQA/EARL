#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: rony
"""
import csv
import string
from langdetect import detect


ER_dictionary = {}

for i in ER_dictionary:
#Create a list


#Make the list iterable

#Get some output out of the the list


for line in open("entities.txt",'r',encoding="utf8"):
    ER_dictionary[line]='E'

for line in open("relationships.txt",'r',encoding="utf8"):
    ER_dictionary[line]='R'

with open('names.csv','w',encoding="utf8") as csvf:
    header=['labels','data']

    writer= csv.writer(csvf,delimiter=',')

    writer.writerow(i for i in header)

    for key,value in ER_dictionary.items():
       print(key,value)
       writer.writerow([value,key])
