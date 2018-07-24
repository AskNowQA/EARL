# Scripts for training ER predictor and the re-ranker

## ER-predictor

Use the script ent_rel_predictor.py for training. It uses the entitiy and relation names and also the RDF2VEC vectors present in the file DB2Vec_sg_500_5_5_15_4_500

Install all the requirements and run python ./ent_rel_predictor.py

It will save the model in the path specified in the script.

## XGB re-ranker

Use the script train_xgb_model.py

Run the script as :

python ./train_xgb_model.py <json file>(as input)
It will get the mrr scores and save the best model.
