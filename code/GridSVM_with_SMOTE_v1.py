import argparse
from collections import Counter
from numpy import mean
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.svm import SVC
from imblearn.over_sampling import RandomOverSampler, SVMSMOTE
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report
parser = argparse.ArgumentParser(description='Vulnerability discovery analysis and calculating results of analysis')
parser.add_argument('--input_path_x86_emb', help='filepath for x86 function embeddings')
parser.add_argument('--input_path_ARM_emb', help='filepath for ARM function embeddings')
args = parser.parse_args()
input_file = args.input_path_x86_emb
input_file_ARM = args.input_path_ARM_emb
VULNERABLE_FUNCTION_LIST = ['@ssl3_get_new_session_ticket.gdl', '@dtls1_process_heartbeat.gdl', '@OBJ_obj2txt.gdl']
print('')
for VULNERABLE_FUNCTION_NAME in VULNERABLE_FUNCTION_LIST:
    sampling_strategy_val = 0.002
    X = []
    y = []
    n_splits_val = 2
    n_repeats_val = 3
    random_state_val = 1
    # read function embedding file
    with open(input_file, "r", errors='ignore') as fp_in:
        for line in fp_in:
            function_name = line.split(' ', 1)[0]
            function_name = function_name.strip()
            function_embedding = line.split(' ', 1)[1]
            function_embedding = [float(s) for s in function_embedding.split(' ')]
            X.append(function_embedding)
            if function_name.endswith(VULNERABLE_FUNCTION_NAME):
                y.append(1)
            else:
                y.append(0)
    X_test = []
    y_test = []
    with open(input_file_ARM, "r", errors='ignore') as fp_in:
        for line in fp_in:
            function_name = line.split(' ', 1)[0]
            function_name = function_name.strip()
            function_embedding = line.split(' ', 1)[1]
            function_embedding = [float(s) for s in function_embedding.split(' ')]
            X_test.append(function_embedding)
            if function_name.endswith(VULNERABLE_FUNCTION_NAME):
                y_test.append(1)
            else:
                y_test.append(0)
    steps = [('ros', RandomOverSampler()), ('model', SVC(gamma='scale'))]
    pipeline = Pipeline(steps=steps)
    cv = RepeatedStratifiedKFold(n_splits=n_splits_val, n_repeats=n_repeats_val, random_state=random_state_val)
    print('Analysis of Minority-Data-Oversampling and Performance-Results of the Model for Vulnerable Function :', VULNERABLE_FUNCTION_NAME)
    counter = Counter(y)
    print('Size of Train dataset before oversampling:', counter)
    oversample = SVMSMOTE(k_neighbors=2, random_state = 2, sampling_strategy=sampling_strategy_val)
    # For train data
    X, y = oversample.fit_resample(X, y)
    scores = cross_val_score(pipeline, X, y, scoring='roc_auc', cv=cv, n_jobs=-1)
    counter = Counter(y)
    print('Size of Train dataset after oversampling:', counter)
    print('For Train data Mean ROC AUC: %.2f' % mean(scores))
    counter = Counter(y_test)
    print('Size of Test dataset before oversampling:', counter)
    oversample = SVMSMOTE(k_neighbors=2, random_state = 2, sampling_strategy=sampling_strategy_val)
    # For test data
    X_test, y_test = oversample.fit_resample(X_test, y_test)
    scores = cross_val_score(pipeline, X_test, y_test, scoring='roc_auc', cv=cv, n_jobs=-1)
    counter = Counter(y_test)
    print('Size of Test dataset after oversampling:', counter)
    print('For Test data Mean ROC AUC: %.2f' % mean(scores))
    X_Train_test = []
    for i in X:
        X_Train_test.append(i)
    for i in X_test:
        X_Train_test.append(i)
    y_Train_test = []
    for i in y:
        y_Train_test.append(i)
    for i in y_test:
        y_Train_test.append(i)
    y_pred = cross_val_predict(pipeline, X_Train_test, y_Train_test, cv=10)
    CM = confusion_matrix(y_Train_test, y_pred)
    TN = CM[0][0]
    FN = CM[1][0]
    TP = CM[1][1]
    FP = CM[0][1]
    print('Confusion Matrix:')
    print('True Negative = ', TN)
    print('False Negative = ', FN)
    print('True Positive = ', TP)
    print('False Positive = ', FP)
    classification_report_result = classification_report(y_Train_test, y_pred)
    print('Classification report : \n',classification_report_result)