from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
import numpy as np
import xgboost as xgb
import sys
import json
"""
Script for getting MRR scores before and after re-ranking with 5-fold cross-validation
pass the name of the json file as a parameter to the script
"""
reranked_list = []
def create_k_folds(n_folds, data):
    """
    divide the data into n_folds
    :param n_folds:
    :param data:
    :return:
    """
    folds_idx = []
    intervals = int(len(data)/n_folds)
    #get test indexes
    for i in range(0, n_folds):
        test_idx = range(i * intervals, (i + 1) * intervals)
    	train_idx = [i for i in range(0, len(data)) if i not in test_idx]
    	folds_idx.append([train_idx, test_idx])

    return folds_idx

def get_vecs(data):
    """
    get features from individual json
    :param data: 
    :return: 
    """
    correct_labels = []
    incorrect_labels = []
    for dat in data:
        correct_vals = dat['correctnodestats']
        for v in correct_vals:
            correct_labels.append([v['connections'], v['sumofhops']])

        incorrect_vals = dat['incorrectnodestats']
        for v in incorrect_vals:
            incorrect_labels.append([v['connections'], v['sumofhops']])

    print np.array(correct_labels[0])
    return np.concatenate((np.array(correct_labels), np.array(incorrect_labels))), np.concatenate((np.ones(len(correct_labels)), np.zeros(len(incorrect_labels))))

def get_vecs_von_train(es_list):
    """
    get features for training data
    :param es_list:
    :return:
    """
    correct_labels = []
    incorrect_labels = []
    for l in range(0, len(es_list)):
    #print es_list
	dat = es_list[l]['ES_content']
        for k in range(len(dat)):
            list_dat = dat[k]['list'+str(k+1)]
            for lists in list_dat:
               if lists['correctlabel'] == 1:
                    correct_labels.append([lists['connections'], lists['sumofhops'], lists['elasticsearchrank']])
                    #correct_labels.append([lists['connections'], lists['sumofhops']])
               else:
                    incorrect_labels.append([lists['connections'], lists['sumofhops'], lists['elasticsearchrank']])
 		    #incorrect_labels.append([lists['connections'], lists['sumofhops']])

    print np.array(correct_labels[0])
    return np.concatenate((np.array(correct_labels), np.array(incorrect_labels))), np.concatenate((np.ones(len(correct_labels)), np.zeros(len(incorrect_labels))))
    
    
def get_vecs_von_test(test_list):
    """
    get feature vectors for test data
    :param test_list:
    :return:
    """
    vec = []
    for lists in test_list:
        vec.append([lists['connections'], lists['sumofhops'], lists['elasticsearchrank']])
	#vec.append([lists['connections'], lists['sumofhops']])
    return np.array(vec)
	
def get_mrr_test(dat, model):
    """
    get MRR metric for test_data
    :param dat:
    :param model:
    :return:
    """
    mrr_test = 0.0
    reranked_q = []
    for k in range(len(dat)):
        list_dat = dat[k]['list'+str(k+1)]
        if len(list_dat) == 0:
            break
        else:
            try:
                dtest = xgb.DMatrix(get_vecs_von_test(list_dat))
            except Exception:
                print list_dat
        predictions = model.predict(dtest)
        #print predictions
	for d in range(len(list_dat)):
        	list_dat[d]['prediction'.decode('utf-8')] = predictions[d].item()
	
	#print list_dat
	new_list = sorted(list_dat, key=lambda x: x['prediction'], reverse=True)
        reranked_q.append(new_list)
	mrr_test = mrr_test +  get_mrr(new_list)
    reranked_list.append(reranked_q)
    return mrr_test/ len(dat)


def get_mrr(lists):
    """
    get the MRR value
    :param lists:
    :return:
    """
    rank = 0.0
    if len(lists) == 0:
        print lists
    for i in range(0,len(lists)):
        #print lists[i]['correctlabel']
	#put elastic search == 0 while doing for not considering infused results
	    #if lists[i]['correctlabel'] == 1 and lists[i]['elasticsearchscore'] != 0:
	    if lists[i]['correctlabel'] == 1:
            #print i
  	        rank = i + 1
    #print rank
    if rank == 0.0:
        return 0.000001
    else:
        return np.divide(1.0, rank)

    
def get_mrr_combined(content):
    """
    get mrr for all the lists
    :param content:
    :return:
    """
    num_lists = len(content)
    tot_mrr = 0.0
    #print content
    for i in range(num_lists):
        
        tot_mrr = tot_mrr + get_mrr(content[i]['list'+str(i + 1)])
    
    return np.divide(tot_mrr, num_lists)

def mrr_scores(data):
    #get mrr ohne classifier
    idxs = create_k_folds(5, data)
    data = np.array(data)
    mrr_avg = 0.0
    for train, test in idxs:
        test_mrr = 0.0
        for dat in data[test]:
            test_mrr = test_mrr + get_mrr_combined(dat['ES_content'])
        print test_mrr / len(data[test])
        mrr_avg = mrr_avg + (test_mrr / len(data[test]))

    print "MRR average ohne classifier:"
    print len(idxs)
    print mrr_avg/len(idxs)
    #idxs = create_k_folds(5, data)
    #get mrr mit classifier
    from sklearn.metrics import accuracy_score, f1_score
    mrr_avg = 0.0
    for train, test in idxs:
        train_x, train_y = get_vecs_von_train(data[train])
        #test_x, test_y = get_vecs(data[test])
        #logistic = LogisticRegression()
        #logistic.fit(train_x,train_y)
        #clf = svm.LinearSVC()
        #clf.fit(train_x, train_y)
        print train_x.shape
        dtrain = xgb.DMatrix(train_x, label=train_y)
        #dtest = xgb.DMatrix(test_x, label=test_y)
        # set xgboost params
        param = {
        'max_depth': 4,  # the maximum depth of each tree
        'eta': 0.3,  # the training step for each iteration
        'silent': 1,  # logging mode - quiet
        'objective': 'binary:logistic',
        'eval_metric': 'logloss',  # error evaluation for multiclass training
        'lambda_bias': 0.02}  # the number of classes that exist in this datset
        num_round = 300  # the number of training iterations
        bst = xgb.train(param, dtrain, num_round)
        print "getting values for test sets:"
        """
        test_mrr = 0.0
        for dat in data[test]:
        test_mrr = test_mrr + get_mrr_combined(dat['ES_content'])
        print test_mrr / len(data[test])
        mrr_avg = mrr_avg + (test_mrr / len(data[test]))
        """
        test_mrr = 0.0
        len_test = len(data[test])

        for test_dat in data[test]:
            test_mrr = test_mrr + get_mrr_test(test_dat['ES_content'], bst)

        mrr_avg = mrr_avg + test_mrr/len_test
        print mrr_avg

    print "Average MRR on mit classifier:"
    print mrr_avg/len(idxs)

if __name__ == '__main__':
    data_file = sys.argv[1]
    with open(data_file) as data_f:
        data = json.load(data_f)
    #data = np.array(data)
    #mrr_scores(data)
    #np.save('re-ranked_f', reranked_list)
    
    train_x, train_y = get_vecs_von_train(data)
    print train_x.shape
    dtrain = xgb.DMatrix(train_x, label=train_y)
    # set xgboost params
    param = {
        'max_depth': 4,  # the maximum depth of each tree
        'eta': 0.3,  # the training step for each iteration
        'silent': 1,  # logging mode - quiet
        'objective': 'binary:logistic',
        'eval_metric': 'logloss',  # error evaluation for multiclass training
        'lambda_bias': 0.02}  # the number of classes that exist in this datset
    num_round = 300  # the number of training iterations
    bst = xgb.train(param, dtrain, num_round)

    bst.save_model('models/db_predia_reranker.model') 
