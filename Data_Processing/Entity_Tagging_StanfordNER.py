from nltk.tag import StanfordNERTagger

jar = 'stanford-ner-2015-04-20/stanford-ner.jar'

model ='stanford-ner-2015-04-20/classifiers/english.all.3class.distsim.crf.ser.gz'

st = StanfordNERTagger(model,jar,encoding="utf8")

f = open("entities.txt","r",encoding="utf8")


for line in f:

    sts = line.split()
    lst = []
    lst.append(line)
    print(st.tag(lst))
