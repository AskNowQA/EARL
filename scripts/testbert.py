import urllib2 
import json

req = urllib2.Request('http://localhost:8887/bert')
req.add_header('Content-Type', 'application/json')
inputjson = {'sentences':["where is delhi", "who is the president of america"]}
response = urllib2.urlopen(req, json.dumps(inputjson))
print(response)
embedding = json.loads(response.read().decode('utf8'))
print(embedding)

