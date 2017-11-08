#!/usr/bin/python

from practnlptools.tools import Annotator
from stop_words import get_stop_words


class ShallowParser:
    def __init__(self):
        print "Shallow Parser Initializing"
        self.annotator=Annotator()
        self.stop_words = get_stop_words('en')
        print "Shallow Parser Initialized"

    def shallowParse(self, text):
        filterednpchunks = []
        result = self.annotator.getAnnotations(text)
        for chunk in result['chunk']:
            if '-NP' in chunk[1]:
                filteredchunk = []
                filteredchunkstring = ''
                for word in chunk[0].split(' '):
                    if word not in self.stop_words:
                        filteredchunk.append(word)
                if len(filteredchunk) > 0:
                    filteredchunkstring = ' '.join(filteredchunk)
                    filterednpchunks.append(filteredchunkstring)
        return filterednpchunks
                 

if __name__=='__main__':
    s = ShallowParser()
    print s.shallowParse("There are people dying make this world a better place for you and for me.")

    
        
 
