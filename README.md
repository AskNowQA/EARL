# EARL
Entity And Relation Linking

The objective of this package is to link or identify relation/predicate. Named
Entity Recognition tools are able to identify the named entites however the
relations is left unlinked. Eg.

Let's consider the sentence: Where was Barack Obama born?

If we pass this sentence into AskNow's NQS we can expect:

Where was [Barack Obama](http://dbpedia.org/resource/Barack_Obama) born?

However we aim to also link the relation like:

Where was [Barack Obama](http://dbpedia.org/resource/Barack_Obama)
[born](http://dbpedia.org/ontology/birthPlace)?

The hypothesis is that jointly linking relation and entity would help in
disambiguation. This might also help in bringing the context of entity at the
sentence level which can also in turn help in answering complex questions.

# INSTRUCTIONS

cd scripts/

python api.py 5000

This starts the api server. Install all dependencies required.

To consume the API

curl -XPOST 'localhost:5000/processQuery' -H 'Content-Type: application/json' -d"{\"nlquery\":\"Who is the president of USA?\"}"
