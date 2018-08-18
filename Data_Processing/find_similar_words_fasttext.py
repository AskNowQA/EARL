 
import gensim



model = gensim.models.KeyedVectors.load_word2vec_format('Data_Processing/wiki-news-300d-1M.vec')
word_vectors = model.wv
print("Fetched Model")

relationship = []
i=0
filename = "relationship_from_fasttext.txt"
f = open(filename,"w")

for line in open("relationships.txt","r"):
    if i%2==1:
        
        rel = line.rstrip('\n')
        if rel not in word_vectors.vocab:
            continue
        
        f.write(rel+"\n")
        temp =[]
        temp.append(rel)
        similar_words = model.most_similar(positive=temp,topn=44)
        
        for words in similar_words:
            
            f.write(words[0]+"\n")
            print(words[0])
    i+=1

f.close()