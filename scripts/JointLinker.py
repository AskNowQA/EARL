#!/usr/bin/python

import json,sys
import itertools
from operator import itemgetter
from pybloom import BloomFilter


class JointLinker:
    def __init__(self):
        print("Joint Linker initializing")
        try:
            f = open('../data/blooms/bloom1hoppredicate.pickle','rb')
            self.bloom1hoppred = BloomFilter.fromfile(f)
            f.close()
            f = open('../data/blooms/bloom1hopentity.pickle','rb')
            self.bloom1hopentity = BloomFilter.fromfile(f)
            f.close()
            f = open('../data/blooms/bloom2hoppredicate.pickle','rb')
            self.bloom2hoppredicate = BloomFilter.fromfile(f)
            f.close()
            f = open('../data/blooms/bloom2hoptypeofentity.pickle','rb')
            self.bloom2hoptypeofentity = BloomFilter.fromfile(f)
            f.close()
        except Exception as e:
            print(e)
            sys.exit(1)
        print("Joint Linker initialized")

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
        for k1,v1 in nodestats.items():
            for k2,v2 in v1.items():
                nodestats[k1][k2]['connections'] /= float(len(lists))
                nodestats[k1][k2]['sumofhops'] /= float(len(lists))
            
        return {'nodefeatures': nodestats, 'chunktext': chunktexts, 'ertypes': ertypes}
    

if __name__ == '__main__':
    j = JointLinker()
    print(j.jointLinker([{'chunk': {'chunk': 'Who', 'surfacelength': 3, 'class': 'entity', 'surfacestart': 0}, 'topkmatches': [u'http://dbpedia.org/resource/Who', u'http://dbpedia.org/resource/Who%3F_Who%3F_Ministry', u'http://dbpedia.org/resource/WHO-DT', u'http://dbpedia.org/resource/Who%3F_(novel)', u'http://dbpedia.org/resource/Who,_Me', u'http://dbpedia.org/resource/Who,_What,_Wear', u'http://dbpedia.org/resource/WHO/PES', u'http://dbpedia.org/resource/Chi_(Who)', u'http://dbpedia.org/resource/Who%3F_(song)', u'http://dbpedia.org/resource/Who,_whom%3F', u'http://dbpedia.org/resource/Who%3F_(album)', u'http://dbpedia.org/resource/Yara-ma-yha-who', u'http://dbpedia.org/resource/Who_Covers_Who%3F', u'http://dbpedia.org/resource/Who_Made_Who_World_Tour', u"http://dbpedia.org/resource/Who_I_Am_Hates_Who_I've_Been", u'http://dbpedia.org/resource/Who_Is_Dr_Who', u'http://dbpedia.org/resource/Who_Killed_Who%3F', u'http://dbpedia.org/resource/Who_Made_Who_(song)', u'http://dbpedia.org/resource/Who_Shall_Live_and_Who_Shall_Die', u'http://dbpedia.org/resource/Who_Made_Who', u'http://dbpedia.org/resource/Who_Knows_Who', u'http://dbpedia.org/resource/Girls_Who_Like_Boys_Who_Like_Boys', u'http://dbpedia.org/resource/Vem_\xe4r_det', u'http://dbpedia.org/resource/Girls_Who_Like_Boys_Who_Like_Boys_(book)', u'http://dbpedia.org/resource/Who_Booty', u'http://dbpedia.org/resource/Doctor_Who', u'http://dbpedia.org/resource/Ledipasvir', u'http://dbpedia.org/resource/Vinnie_Who', u'http://dbpedia.org/resource/Who_Cares', u'http://dbpedia.org/resource/Who_Dunnit', u'http://dbpedia.org/resource/The_Who'], 'class': 'entity'}, {'chunk': {'chunk': 'the parent organisation', 'surfacelength': 23, 'class': 'relation', 'surfacestart': 7}, 'topkmatches': [u'http://dbpedia.org/ontology/parentOrganisation', u'http://dbpedia.org/property/parentOrganisation', u'http://dbpedia.org/property/parentOrganization', u'http://dbpedia.org/property/parentOraganisation', u'http://dbpedia.org/ontology/parent', u'http://dbpedia.org/ontology/organisation', u'http://dbpedia.org/ontology/Organisation', u'http://dbpedia.org/property/organisation', u'http://dbpedia.org/property/parantOrganization', u'http://dbpedia.org/property/agent', u'http://dbpedia.org/property/parentCo.', u'http://dbpedia.org/property/parent', u'http://dbpedia.org/property/organisations', u'http://dbpedia.org/property/organization', u'http://dbpedia.org/property/urbanisation', u'http://dbpedia.org/property/organizations', u'http://dbpedia.org/property/organiztion', u'http://www.telegraph.co.uk/finance/property/renting/11908002/Generation-rent-the-reluctant-rise-of-the-older-tenant.html', u'http://dbpedia.org/property/theN', u'http://dbpedia.org/property/theE', u'http://dbpedia.org/property/theA', u'http://dbpedia.org/property/theW', u'http://dbpedia.org/property/prarent', u'http://dbpedia.org/property/parents', u'http://dbpedia.org/property/perent', u'http://dbpedia.org/property/parnet'], 'class': 'relation'}, {'chunk': {'chunk': 'Barack Obama', 'surfacelength': 12, 'class': 'entity', 'surfacestart': 34}, 'topkmatches': [u'http://dbpedia.org/resource/Barack_Obama', u'http://dbpedia.org/resource/List_of_topics_related_to_Barack_Obama', u'http://dbpedia.org/resource/Barack_Obama_%22Joker%22_poster', u'http://dbpedia.org/resource/Assassination_threats_against_Barack_Obama', u'http://dbpedia.org/resource/List_of_books_and_films_about_Barack_Obama', u'http://dbpedia.org/resource/Presidential_transition_of_Barack_Obama', u'http://dbpedia.org/resource/Public_image_of_Barack_Obama', u'http://dbpedia.org/resource/Economic_policy_of_Barack_Obama', u'http://dbpedia.org/resource/Invitations_to_the_first_inauguration_of_Barack_Obama', u'http://dbpedia.org/resource/Barack_Obama_College_Preparatory_High_School', u'http://dbpedia.org/resource/Space_policy_of_the_Barack_Obama_administration', u'http://dbpedia.org/resource/Efforts_to_impeach_Barack_Obama', u'http://dbpedia.org/resource/Barack_Obama_Selma_50th_anniversary_speech', u'http://dbpedia.org/resource/Foreign_policy_of_the_Barack_Obama', u'http://dbpedia.org/resource/Illinois_Senate_career_of_Barack_Obama', u'http://dbpedia.org/resource/Second_inauguration_of_Barack_Obama', u'http://dbpedia.org/resource/Barack_Obama_Tucson_memorial_speech', u'http://dbpedia.org/resource/List_of_things_named_after_Barack_Obama', u'http://dbpedia.org/resource/First_inauguration_of_Barack_Obama', u'http://dbpedia.org/resource/Barack_Obama_presidential_campaign,_2008', u'http://dbpedia.org/resource/United_States_Senate_career_of_Barack_Obama', u'http://dbpedia.org/resource/Barack_Obama,_Sr.', u'http://dbpedia.org/resource/Barack_Obama_on_social_media', u'http://dbpedia.org/resource/Barack_Obama_in_comics', u'http://dbpedia.org/resource/Barack_Obama_presidential_campaign_endorsements', u'http://dbpedia.org/resource/Barack_Obama_%22Hope%22_poster', u'http://dbpedia.org/resource/Barack_Obama_Male_Leadership_Academy', u'http://dbpedia.org/resource/Barack_Obama_Democratic_Club_of_Upper_Manhattan', u'http://dbpedia.org/resource/Native_American_Policy_of_the_Barack_Obama_Administration', u'http://dbpedia.org/resource/Timeline_of_the_presidency_of_Barack_Obama', u'http://dbpedia.org/resource/Barack_Obama_Green_Charter_High_School'], 'class': 'entity'}, {'chunk': {'chunk': 'is', 'surfacelength': 2, 'class': 'relation', 'surfacestart': 4}, 'topkmatches': [u'http://dbpedia.org/property/is', u'http://dbpedia.org/property/10,000IsADiceGameThatIsPlayedWithFiveDiceA', u'http://dbpedia.org/property/isArtillery', u'http://dbpedia.org/property/isSeries', u'http://dbpedia.org/property/isUk', u'http://dbpedia.org/property/isRanged', u'http://dbpedia.org/property/isBladed', u'http://dbpedia.org/property/isMissile', u'http://dbpedia.org/property/isBomb', u'http://dbpedia.org/property/isOn', u'http://dbpedia.org/property/causeIs', u'http://dbpedia.org/property/isMulti', u'http://dbpedia.org/property/isVehicle', u'http://dbpedia.org/property/isStack', u'http://dbpedia.org/property/isRangedl', u'http://dbpedia.org/property/isSeason', u'http://dbpedia.org/property/featIs', u'http://dbpedia.org/property/isThermal', u'http://dbpedia.org/property/isShip', u'http://dbpedia.org/property/isExplosive', u'http://dbpedia.org/property/isTube', u'http://www.independent.co.uk/property/house-and-home/is-elmbridge-britains-beverly-hills-2190344.html', u'http://www.telegraph.co.uk/finance/property/3293690/When-an-Englishmans-home-is-his-business.html', u'http://www.smh.com.au/business/property/old-is-new-at-refashioned-amp-square-20110522-1eytn.html', u'http://www.telegraph.co.uk/property/overseasproperty/3360841/Caribbean-property-Rio-Ferdinand-is-ahead-of-the-game.html', u'http://www.telegraph.co.uk/property/9285761/Hovis-Hill-is-this-the-greatest-street-since-sliced-bread.html', u'http://www.timeslive.co.za/sundaytimes/decor/property/2015/11/13/Real-estate-crowdfunding-is-unchartered-territory-in-SA', u'http://www.news.com.au/money/property/mining-boom-is-strangling-heart-of-gunnedah/story-e6frfmd0-1226298825863', u'http://dbpedia.org/property/theGovernorIs412YearsOfAgeAndHerNameIsEthelWinkleberryTimezone', u'http://dbpedia.org/property/isSiSpecs', u'http://dbpedia.org/property/remains'], 'class': 'relation'}]))
        
