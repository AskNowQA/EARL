# EARL 
## Joint Entity and Relation Linking for Question Answering

EARL (Entity and Relation Linker), a system for jointly linking entities and relations in a question to a knowledge graph. EARL treats entity linking and relation linking as a single task and thus aims to reduce the error caused by the dependent steps. To realise this, EARL uses the knowledge graph to jointly disambiguate entity and relations. EARL obtains the context for entity disambiguation by observing the relations surrounding the entity. Similarly, it obtains the context for relation disambiguation by looking at the surrounding entities. We support multiple entities and relations occurring in complex questions by modelling the joint entity and relation linking task as an instance of the Generalised Travelling Salesman Problem (GTSP).

Check out EARL's system paper (under review) https://arxiv.org/abs/1801.03825

# INSTRUCTIONS

    $cd scripts/
    $python api.py 5000

This starts the api server at port 5000. Install all dependencies required that are mentioned in dependencies.txt. Download bloom files from https://drive.google.com/drive/folders/1lKu0tVA5APhZVOZqRQK2tCk0FDj82lvo?usp=sharing and store them at data/blooms/. Download the archived elastic search dumps from the same google drive link and import them into a local running elasticsearch instance.

To consume the API

    curl -XPOST 'localhost:5000/processQuery' -H 'Content-Type: application/json' -d"{\"nlquery\":\"Who is the president of USA?\"}"

