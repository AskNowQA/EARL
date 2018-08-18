
"""
@author: rony
"""
import numpy
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout, Embedding,Bidirectional
from keras.preprocessing.text import Tokenizer
from keras.preprocessing import sequence
from sklearn.model_selection import StratifiedKFold


df = pd.read_csv('Data/names.csv',delimiter=',',encoding='latin-1')
df.head()


df.info()


sns.countplot(df.labels)
plt.xlabel('Label')
plt.title('Number of Entity and Relationships')


X = df.data
Y = df.labels
le = LabelEncoder()
Y = le.fit_transform(Y)
Y = Y.reshape(-1,1)

def BiLSTM():

    model = Sequential()
    model.add(Embedding((max_words+1), 10, input_length=max_len))
    model.add(Bidirectional(LSTM(12)))
    model.add(Dropout(0.5))
    model.add(Dense(1, activation='sigmoid'))
    model.compile('adam', 'binary_crossentropy', metrics=['accuracy'])
    return model


max_words = 100
max_len = 100


seed = 11
# define 10-fold cross validation test harness
kfold = StratifiedKFold(n_splits=10, shuffle=False, random_state=seed)
results = []
for train, test in kfold.split(X, Y):
    model = BiLSTM()

    tok = Tokenizer(num_words=max_words)
    print(X[train])
    tok.fit_on_texts(X[train])
    sequences = tok.texts_to_sequences(X[train])
    sequences_matrix = sequence.pad_sequences(sequences,maxlen=max_len)
    model.fit(sequences_matrix, Y[train], epochs=1, batch_size=500, verbose=0)

    tok = Tokenizer(num_words=max_words)
    tok.fit_on_texts(X[test])
    sequences = tok.texts_to_sequences(X[test])
    sequences_matrix = sequence.pad_sequences(sequences,maxlen=max_len)
    scores = model.evaluate(sequences_matrix, Y[test], verbose=0)
    print("%s: %.2f%%" % (model.metrics_names[1], scores[1]*100))
    results.append(scores[1] * 100)
print("%.2f%% (+/- %.2f%%)" % (numpy.mean(results), numpy.std(results)))
