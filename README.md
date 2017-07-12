# EARL
Entity And Relation mapping

The objective of this package is to link or identify relation/predicate. Named
Entity Recognition tools are able to identify the named entites however the
relations is left unlinked. Eg.

Let's consider the sentence: Where was Barack Obama born?

If we pass this sentence into AskNow's NQS we can expect:

Where was [Barack Obama](dbpedia.org/resource/Barack_obama) born?

However we aim to also link the relation like:

Where was [Barack Obama](dbpedia.org/resource/Barack_obama)
[born](http://dbpedia.org/ontology/birthPlace)?

The hypothesis is that jointly linking relation and entity would help in
disambiguation. This might also help in bringing the context of entity at the
sentence level which can also in turn help in answering complex questions.
