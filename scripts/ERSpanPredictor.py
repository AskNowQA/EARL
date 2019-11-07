import sys
import json
import urllib2


class ERSpanDetector():
    def __init__(self):
       print("Initialising ER span detector")
       print("Initialised ER span detector")

    def erspan(self,nlquery):
        req = urllib2.Request('http://131.220.9.219/mdp/api/link')
        req.add_header('Content-Type', 'application/json')
        inputjson = {'question': nlquery, 'connecting_relation':False}
        response = urllib2.urlopen(req, json.dumps(inputjson))
        response = json.loads(response.read())
        erpredictions = []
        for entity in response['entities']:
            for uri in entity['uris']:
                chunk = nlquery[entity['surface'][0]:entity['surface'][0]+entity['surface'][1]]
                erpredictions.append({'chunk': chunk , 'surfacestart': entity['surface'][0], 'surfacelength':entity['surface'][1], 'class':'entity'})
                break
        for relation in response['relations']:
            for uri in relation['uris']:
                chunk = nlquery[relation['surface'][0]:relation['surface'][0]+relation['surface'][1]]
                erpredictions.append({'chunk': chunk, 'surfacestart': relation['surface'][0], 'surfacelength': relation['surface'][1], 'class':'relation'})
                break
        return erpredictions

if __name__ == '__main__':
    e = ERSpanDetector()
#    print(e.erspan("name the place of qaqun"))
#    print(e.erspan("who is the president of india?"))
#    print(e.erspan("Who is the president of India?"))
#    print(e.erspan("Who is the father of the mother of Barack Obama"))
#    print(e.erspan("who is the father of the mother of barack obama"))
#    print(e.erspan("How many rivers flow through Bonn?"))
#    print(e.erspan("how many rivers flow through bonn?"))
    print(e.erspan("List all the musicals with music by Elton John."))
    print(e.erspan("Give me the names of professional skateboarders of India"))
