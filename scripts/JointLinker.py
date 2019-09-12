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
                    if bloomstring in self.bloom1hoppred:
                        nodestats[permutation[0]][uri1]['connections'] += 1
                        nodestats[permutation[0]][uri1]['sumofhops'] += 0.5
                        nodestats[permutation[1]][uri2]['connections'] += 1
                        nodestats[permutation[1]][uri2]['sumofhops'] += 0.5
                    if bloomstring in self.bloomqualifier:
                        nodestats[permutation[0]][uri1]['connections'] += 1
                        nodestats[permutation[0]][uri1]['sumofhops'] += 1.5
                        nodestats[permutation[1]][uri2]['connections'] += 1
                        nodestats[permutation[1]][uri2]['sumofhops'] += 1.5
                    elif bloomstring in self.bloom1hopentity:
                        nodestats[permutation[0]][uri1]['connections'] += 1
                        nodestats[permutation[0]][uri1]['sumofhops'] += 1
                        nodestats[permutation[1]][uri2]['connections'] += 1
                        nodestats[permutation[1]][uri2]['sumofhops'] += 1
#                    elif bloomstring in self.bloom2hoppredicate:
#                        nodestats[permutation[0]][uri1]['connections'] += 1
#                        nodestats[permutation[0]][uri1]['sumofhops'] += 1.5
#                        nodestats[permutation[1]][uri2]['connections'] += 1
#                        nodestats[permutation[1]][uri2]['sumofhops'] += 1.5
                    elif bloomstring in self.bloom1hoptypeofentity:
                        nodestats[permutation[0]][uri1]['connections'] += 1
                        nodestats[permutation[0]][uri1]['sumofhops'] += 1
                        nodestats[permutation[1]][uri2]['connections'] += 1
                        nodestats[permutation[1]][uri2]['sumofhops'] += 1
#                    elif bloomstring in self.bloom2hoptypeofentity:
#                        nodestats[permutation[0]][uri1]['connections'] += 1
#                        nodestats[permutation[0]][uri1]['sumofhops'] += 2
#                        nodestats[permutation[1]][uri2]['connections'] += 1
#                        nodestats[permutation[1]][uri2]['sumofhops'] += 2
        for k1,v1 in nodestats.iteritems():
            for k2,v2 in v1.iteritems():
                nodestats[k1][k2]['connections'] /= float(len(lists))
                nodestats[k1][k2]['sumofhops'] /= float(len(lists))
            
        return {'nodefeatures': nodestats, 'chunktext': chunktexts, 'ertypes': ertypes}
    

if __name__ == '__main__':
    j = JointLinker()
#    print j.jointLinker([{'chunk': {'chunk': 'Who', 'surfacelength': 3, 'class': 'entity', 'surfacestart': 0}, 'topkmatches': [u'http://dbpedia.org/resource/Who', u'http://dbpedia.org/resource/Who%3F_Who%3F_Ministry', u'http://dbpedia.org/resource/WHO-DT', u'http://dbpedia.org/resource/Who%3F_(novel)', u'http://dbpedia.org/resource/Who,_Me', u'http://dbpedia.org/resource/Who,_What,_Wear', u'http://dbpedia.org/resource/WHO/PES', u'http://dbpedia.org/resource/Chi_(Who)', u'http://dbpedia.org/resource/Who%3F_(song)', u'http://dbpedia.org/resource/Who,_whom%3F', u'http://dbpedia.org/resource/Who%3F_(album)', u'http://dbpedia.org/resource/Yara-ma-yha-who', u'http://dbpedia.org/resource/Who_Covers_Who%3F', u'http://dbpedia.org/resource/Who_Made_Who_World_Tour', u"http://dbpedia.org/resource/Who_I_Am_Hates_Who_I've_Been", u'http://dbpedia.org/resource/Who_Is_Dr_Who', u'http://dbpedia.org/resource/Who_Killed_Who%3F', u'http://dbpedia.org/resource/Who_Made_Who_(song)', u'http://dbpedia.org/resource/Who_Shall_Live_and_Who_Shall_Die', u'http://dbpedia.org/resource/Who_Made_Who', u'http://dbpedia.org/resource/Who_Knows_Who', u'http://dbpedia.org/resource/Girls_Who_Like_Boys_Who_Like_Boys', u'http://dbpedia.org/resource/Vem_\xe4r_det', u'http://dbpedia.org/resource/Girls_Who_Like_Boys_Who_Like_Boys_(book)', u'http://dbpedia.org/resource/Who_Booty', u'http://dbpedia.org/resource/Doctor_Who', u'http://dbpedia.org/resource/Ledipasvir', u'http://dbpedia.org/resource/Vinnie_Who', u'http://dbpedia.org/resource/Who_Cares', u'http://dbpedia.org/resource/Who_Dunnit', u'http://dbpedia.org/resource/The_Who'], 'class': 'entity'}, {'chunk': {'chunk': 'the parent organisation', 'surfacelength': 23, 'class': 'relation', 'surfacestart': 7}, 'topkmatches': [u'http://dbpedia.org/ontology/parentOrganisation', u'http://dbpedia.org/property/parentOrganisation', u'http://dbpedia.org/property/parentOrganization', u'http://dbpedia.org/property/parentOraganisation', u'http://dbpedia.org/ontology/parent', u'http://dbpedia.org/ontology/organisation', u'http://dbpedia.org/ontology/Organisation', u'http://dbpedia.org/property/organisation', u'http://dbpedia.org/property/parantOrganization', u'http://dbpedia.org/property/agent', u'http://dbpedia.org/property/parentCo.', u'http://dbpedia.org/property/parent', u'http://dbpedia.org/property/organisations', u'http://dbpedia.org/property/organization', u'http://dbpedia.org/property/urbanisation', u'http://dbpedia.org/property/organizations', u'http://dbpedia.org/property/organiztion', u'http://www.telegraph.co.uk/finance/property/renting/11908002/Generation-rent-the-reluctant-rise-of-the-older-tenant.html', u'http://dbpedia.org/property/theN', u'http://dbpedia.org/property/theE', u'http://dbpedia.org/property/theA', u'http://dbpedia.org/property/theW', u'http://dbpedia.org/property/prarent', u'http://dbpedia.org/property/parents', u'http://dbpedia.org/property/perent', u'http://dbpedia.org/property/parnet'], 'class': 'relation'}, {'chunk': {'chunk': 'Barack Obama', 'surfacelength': 12, 'class': 'entity', 'surfacestart': 34}, 'topkmatches': [u'http://dbpedia.org/resource/Barack_Obama', u'http://dbpedia.org/resource/List_of_topics_related_to_Barack_Obama', u'http://dbpedia.org/resource/Barack_Obama_%22Joker%22_poster', u'http://dbpedia.org/resource/Assassination_threats_against_Barack_Obama', u'http://dbpedia.org/resource/List_of_books_and_films_about_Barack_Obama', u'http://dbpedia.org/resource/Presidential_transition_of_Barack_Obama', u'http://dbpedia.org/resource/Public_image_of_Barack_Obama', u'http://dbpedia.org/resource/Economic_policy_of_Barack_Obama', u'http://dbpedia.org/resource/Invitations_to_the_first_inauguration_of_Barack_Obama', u'http://dbpedia.org/resource/Barack_Obama_College_Preparatory_High_School', u'http://dbpedia.org/resource/Space_policy_of_the_Barack_Obama_administration', u'http://dbpedia.org/resource/Efforts_to_impeach_Barack_Obama', u'http://dbpedia.org/resource/Barack_Obama_Selma_50th_anniversary_speech', u'http://dbpedia.org/resource/Foreign_policy_of_the_Barack_Obama', u'http://dbpedia.org/resource/Illinois_Senate_career_of_Barack_Obama', u'http://dbpedia.org/resource/Second_inauguration_of_Barack_Obama', u'http://dbpedia.org/resource/Barack_Obama_Tucson_memorial_speech', u'http://dbpedia.org/resource/List_of_things_named_after_Barack_Obama', u'http://dbpedia.org/resource/First_inauguration_of_Barack_Obama', u'http://dbpedia.org/resource/Barack_Obama_presidential_campaign,_2008', u'http://dbpedia.org/resource/United_States_Senate_career_of_Barack_Obama', u'http://dbpedia.org/resource/Barack_Obama,_Sr.', u'http://dbpedia.org/resource/Barack_Obama_on_social_media', u'http://dbpedia.org/resource/Barack_Obama_in_comics', u'http://dbpedia.org/resource/Barack_Obama_presidential_campaign_endorsements', u'http://dbpedia.org/resource/Barack_Obama_%22Hope%22_poster', u'http://dbpedia.org/resource/Barack_Obama_Male_Leadership_Academy', u'http://dbpedia.org/resource/Barack_Obama_Democratic_Club_of_Upper_Manhattan', u'http://dbpedia.org/resource/Native_American_Policy_of_the_Barack_Obama_Administration', u'http://dbpedia.org/resource/Timeline_of_the_presidency_of_Barack_Obama', u'http://dbpedia.org/resource/Barack_Obama_Green_Charter_High_School'], 'class': 'entity'}, {'chunk': {'chunk': 'is', 'surfacelength': 2, 'class': 'relation', 'surfacestart': 4}, 'topkmatches': [u'http://dbpedia.org/property/is', u'http://dbpedia.org/property/10,000IsADiceGameThatIsPlayedWithFiveDiceA', u'http://dbpedia.org/property/isArtillery', u'http://dbpedia.org/property/isSeries', u'http://dbpedia.org/property/isUk', u'http://dbpedia.org/property/isRanged', u'http://dbpedia.org/property/isBladed', u'http://dbpedia.org/property/isMissile', u'http://dbpedia.org/property/isBomb', u'http://dbpedia.org/property/isOn', u'http://dbpedia.org/property/causeIs', u'http://dbpedia.org/property/isMulti', u'http://dbpedia.org/property/isVehicle', u'http://dbpedia.org/property/isStack', u'http://dbpedia.org/property/isRangedl', u'http://dbpedia.org/property/isSeason', u'http://dbpedia.org/property/featIs', u'http://dbpedia.org/property/isThermal', u'http://dbpedia.org/property/isShip', u'http://dbpedia.org/property/isExplosive', u'http://dbpedia.org/property/isTube', u'http://www.independent.co.uk/property/house-and-home/is-elmbridge-britains-beverly-hills-2190344.html', u'http://www.telegraph.co.uk/finance/property/3293690/When-an-Englishmans-home-is-his-business.html', u'http://www.smh.com.au/business/property/old-is-new-at-refashioned-amp-square-20110522-1eytn.html', u'http://www.telegraph.co.uk/property/overseasproperty/3360841/Caribbean-property-Rio-Ferdinand-is-ahead-of-the-game.html', u'http://www.telegraph.co.uk/property/9285761/Hovis-Hill-is-this-the-greatest-street-since-sliced-bread.html', u'http://www.timeslive.co.za/sundaytimes/decor/property/2015/11/13/Real-estate-crowdfunding-is-unchartered-territory-in-SA', u'http://www.news.com.au/money/property/mining-boom-is-strangling-heart-of-gunnedah/story-e6frfmd0-1226298825863', u'http://dbpedia.org/property/theGovernorIs412YearsOfAgeAndHerNameIsEthelWinkleberryTimezone', u'http://dbpedia.org/property/isSiSpecs', u'http://dbpedia.org/property/remains'], 'class': 'relation'}]) 
    print j.jointLinker([{"chunk": {"chunk": "president", "surfacelength": -1, "class": "relation", "surfacestart": -1}, "topkmatches": ["http://www.wikidata.org/entity/P6_P805", "http://www.wikidata.org/entity/P488_P805", "http://www.wikidata.org/entity/P35_P805", "http://www.wikidata.org/entity/P6_P35", "http://www.wikidata.org/entity/P6_P6", "http://www.wikidata.org/entity/P488_P488", "http://www.wikidata.org/entity/P488_P2032", "http://www.wikidata.org/entity/P6_P2032", "http://www.wikidata.org/entity/P488_P304", "http://www.wikidata.org/entity/P488_P2031", "http://www.wikidata.org/entity/P6_P2031", "http://www.wikidata.org/entity/P31_P6", "http://www.wikidata.org/entity/P31_P488", "http://www.wikidata.org/entity/P31_P35", "http://www.wikidata.org/entity/P6", "http://www.wikidata.org/entity/P488", "http://www.wikidata.org/entity/P35", "http://www.wikidata.org/entity/P6_P828", "http://www.wikidata.org/entity/P488_P828", "http://www.wikidata.org/entity/P488_P585", "http://www.wikidata.org/entity/P35_P585", "http://www.wikidata.org/entity/P6_P585", "http://www.wikidata.org/entity/P35_P122", "http://www.wikidata.org/entity/P710_P488", "http://www.wikidata.org/entity/P488_P1365", "http://www.wikidata.org/entity/P35_P1365", "http://www.wikidata.org/entity/P35_P155", "http://www.wikidata.org/entity/P6_P155", "http://www.wikidata.org/entity/P488_P155", "http://www.wikidata.org/entity/P6_P1365"], "class": "relation"}, {"chunk": {"chunk": "Russia", "surfacelength": -1, "class": "entity", "surfacestart": -1}, "topkmatches": [["http://dbpedia.org/resource/Russia", 99214,
32, 100, 33, 100], ["http://dbpedia.org/resource/Russia-K", 263, 31, 80, 37, 86], ["http://dbpedia.org/resource/Women_of_Russia", 38, 61, 80, 53, 75], ["http://dbpedia.org/resource/Song_of_Russia", 204, 53, 79, 50, 78], ["http://dbpedia.org/resource/Law_of_Russia", 157, 45, 77, 47, 82], ["http://dbpedia.org/resource/Soto,_Russia", 86, 47, 75, 44, 71], ["http://dbpedia.org/resource/Peno,_Russia", 114, 47, 75, 49, 71], ["http://dbpedia.org/resource/Log,_Russia", 44, 38, 73, 40, 75], ["http://dbpedia.org/resource/Music_of_Russia", 534, 52, 73, 49, 75], ["http://dbpedia.org/resource/Serbs_of_Russia", 10, 57, 73, 49, 75], ["http://dbpedia.org/resource/Climate_of_Russia", 1005, 54, 71, 47, 69], ["http://dbpedia.org/resource/Borders_of_Russia", 292, 58, 71, 47, 69], ["http://dbpedia.org/resource/232_Russia", 182, 34, 70, 35, 75], ["http://dbpedia.org/resource/MTV_Russia", 294, 34, 70, 40, 75], ["http://dbpedia.org/resource/Government_of_Russia", 860, 63, 70, 48, 62], ["http://dbpedia.org/resource/Etoko,_Russia", 67, 41, 69, 43, 67], ["http://dbpedia.org/resource/Alexis_of_Russia", 771, 51, 69, 52, 72], ["http://dbpedia.org/resource/Tosu,_Russia", 90, 42, 67, 44, 71], ["http://dbpedia.org/resource/Lazo,_Russia", 35, 37,
67, 39, 71], ["http://dbpedia.org/resource/Zyuzino,_Russia", 39, 43, 67, 36, 60], ["http://dbpedia.org/resource/Kola,_Russia", 249, 37, 67, 39, 71], ["http://dbpedia.org/resource/Lena,_Russia", 42, 42, 67, 44, 71], ["http://dbpedia.org/resource/Sberbank_of_Russia", 458, 53, 67, 46, 67], ["http://dbpedia.org/resource/Folklore_of_Russia", 203, 53, 67,
42, 67], ["http://dbpedia.org/resource/White_Russia", 275, 56, 67, 43, 67], ["http://dbpedia.org/resource/Aban,_Russia", 131, 37, 67, 39, 71], ["http://dbpedia.org/resource/South_Russia", 23, 47, 67, 43, 67], ["http://dbpedia.org/resource/Young_Russia", 32, 42, 67, 38, 67], ["http://dbpedia.org/resource/Russia_88", 83, 30, 67, 36, 80], ["http://dbpedia.org/resource/Studeny,_Russia", 69, 48, 67, 41, 60]], "class": "entity"}])       
