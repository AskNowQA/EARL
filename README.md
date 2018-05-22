# EARL 
## Joint Entity and Relation Linking for Question Answering

EARL (Entity and Relation Linker), a system for jointly linking entities and relations in a question to a knowledge graph. EARL treats entity linking and relation linking as a single task and thus aims to reduce the error caused by the dependent steps. To realise this, EARL uses the knowledge graph to jointly disambiguate entity and relations. EARL obtains the context for entity disambiguation by observing the relations surrounding the entity. Similarly, it obtains the context for relation disambiguation by looking at the surrounding entities. We support multiple entities and relations occurring in complex questions by modelling the joint entity and relation linking task as an instance of the Generalised Travelling Salesman Problem (GTSP).

Check out EARL's system paper (under review) https://arxiv.org/abs/1801.03825

# INSTRUCTIONS

    $cd scripts/
    $python api.py 4999

This starts the api server at port 4999. Install all dependencies required that are mentioned in dependencies.txt. Download bloom files from https://drive.google.com/drive/folders/1lKu0tVA5APhZVOZqRQK2tCk0FDj82lvo?usp=sharing and store them at data/blooms/. Download the archived elastic search dumps from the same google drive link and import them into a local running elasticsearch 5.x instance. The mappings can be found in data/elasticsearchdump/ folder.

To import elasticsearch data one could install elasticdump https://www.npmjs.com/package/elasticdump

    npm install elasticdump -g

Then import the two mappings:

    elasticdump --input=dbontologyindex1mapping.json  --output=http://localhost:9200/dbontologyindex1 --type=mapping
    elasticdump --input=dbentityindex9mapping.json  --output=http://localhost:9200/dbentityindex9 --type=mapping
    
Then import the actual data:

    elasticdump --input=dbontologyindex1.json  --output=http://localhost:9200/dbontologyindex1 --type=data
    elasticdump --limit=10000 --input=dbentityindex9.json  --output=http://localhost:9200/dbentityindex9 --type=data

You may need to add the following to the above elasticdump commands to make it work on some setups:

    --headers='{"Content-Type": "application/json"}'
    
    
To consume the API

    curl -XPOST 'localhost:4999/processQuery' -H 'Content-Type: application/json' -d"{\"nlquery\":\"Who is the president of USA?\"}"

