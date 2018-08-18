# Entity Relation Predictor
Predicting Entitiy and Relationship using Bidirectional-LSTM.

## Data
Before Running BiLSTM_ER_Predictor.py and BiLSTM_ER_predictor_with_kfold.py download 'names.csv' from https://drive.google.com/open?id=1kfHaP7KkustBwLE3FDPa8cR7JR9_TFU4 and put the csv file inside 'Data' folder.

## Data Processing
Download 'entities.txt', 'relationship_from_fasttext.txt','relationship.txt','wiki-news-300d-M.vec' files from the following links:
https://drive.google.com/open?id=1NNvljJfeAHZPWUH7cZl9H1B4XzQiTRbr ,
https://drive.google.com/open?id=1blY-T86NGnLgdx8gOoOLa2J2-N2-EIFu ,
https://drive.google.com/open?id=1JdZYWuoKyA6ev-QcAsd3woL8RI2wrN90 ,
https://fasttext.cc/docs/en/english-vectors.html .

After downloading put them inside 'Data_Processing' folder. Now create a folder 'stanford-ner-2015-04-20' inside 'Data_Processing' folder and download the stanford-ner-2015-04-20 from the following link https://nlp.stanford.edu/software/CRF-NER.shtml. and put them inside 'stanford-ner-2015-20' folder.

## Results
To get the result run BiLSTM_ER_Predictor.py or BiLSTM_ER_predictor_with_kfold.py file.



