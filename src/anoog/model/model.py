import os
from enum import Enum

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import VotingClassifier

from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import cross_val_score, cross_val_predict


MODELS = Enum('MODELS', 'RANDOM_FOREST SVM LOGISTIC_REGRESSION ADA_BOOST VOTING_CLASSIFIER NAIVE_BAYES KNN')


def train_random_forest(X_train, y_train, auto_params=False, normalize=False):
    # Classifier Randomforest
    if normalize:
        scaler = MinMaxScaler()
        X_train = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)

    if auto_params:
        param_grid = {'n_estimators':[10, 25, 50, 75, 100, 125, 150],
              'criterion':['gini', 'entropy'], 'min_samples_split':[2,3,4,5]}
        model = GridSearchCV(RandomForestClassifier(), param_grid)
    else:
        model = RandomForestClassifier(n_estimators=100, 
                                bootstrap = True,
                                max_features = 'sqrt')
    return model.fit(X_train, y_train)


def train_svc(X_train, y_train, auto_params=False, normalize=True):
    # Classifier Support Vector Machines
    if normalize:
        scaler = MinMaxScaler()
        X_train = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)

    if auto_params:
        param_grid = {'kernel':['linear', 'poly', 'rbf', 'sigmoid'],
              'probability':[True, False], 'decision_function_shape':['ovo', 'ovr'],
              'C':[0.001,0.1,0.2,0.5,1.0,1.5,2.0,2.5,3.0]  }
        model = GridSearchCV(SVC(), param_grid)
    else:
        model = SVC(C= 0.1, decision_function_shape='ovo', kernel='poly', probability=True)
    return model.fit(X_train, y_train)


def train_knn(X_train, y_train, auto_params=False, normalize=True):
    # Classifier K-Nearest Neighbors
    if normalize:
        scaler = MinMaxScaler()
        X_train = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)

    if auto_params:
        param_grid = {'n_neighbors':[1,2,3,4,5,6,7,8,9],
              'weights':['uniform', 'distance'], 'algorithm':['auto', 'ball_tree', 'kd_tree', 'brute'],
              'metric':['minkowski', 'euclidean', 'manhattan', 'chebyshev']  }
        model = GridSearchCV(KNN(), param_grid)
    else:
        model = KNeighborsClassifier(algorithm='auto', metric='chebyshev', n_neighbors=6, weights='uniform')
    return model.fit(X_train, y_train)


def predict(model, predict_data):
    return model.predict_proba(predict_data)


def predict_proba(model, predict_data):
    return model.predict_proba(predict_data)


def evaluate_model(model, X_test, y_test):
    #accuracy
    y_pred = model.predict(X_test)
    #print(f"Accuracy: ", accuracy_score(y_test, y_pred)*100)

    #confusion_matrix
    #print("--------\nConfusion Matrix:")
    #print(confusion_matrix(y_test, y_pred), "\n")
    #print("--------")
    return accuracy_score(y_test, y_pred)*100, confusion_matrix(y_test, y_pred)


# give Enum or sklearn model in
def evaluate_model_with_cross_validation(X, y, model=MODELS.RANDOM_FOREST, cv=5):
    if model == MODELS.RANDOM_FOREST:
        estimator = RandomForestClassifier(n_estimators=100, criterion='entropy', min_samples_split=5)
    elif model == MODELS.SVM:
        estimator = SVC(C= 0.1, decision_function_shape='ovo', kernel='poly', probability=True)
    elif model == MODELS.KNN:
        estimator = KNeighborsClassifier(algorithm='auto', metric='chebyshev', n_neighbors=6, weights='uniform')
    elif model == MODELS.NAIVE_BAYES:
        estimator = GaussianNB()
    elif model == MODELS.LOGISTIC_REGRESSION:
        estimator = LogisticRegression()
    elif model == MODELS.ADA_BOOST:
        estimator = AdaBoostClassifier()
    elif model == MODELS.VOTING_CLASSIFIER:
        estimators = [('SVC', SVC(C= 0.1, decision_function_shape='ovo', kernel='poly', probability=True)), 
                      ('RandomForest', RandomForestClassifier(n_estimators=100, criterion='entropy', min_samples_split=5))]
        estimator = VotingClassifier(estimators=estimators, voting='hard')
    else:
        estimator = model
    return cross_val_score(estimator, X, y, cv=cv)


def get_most_important_features(model, X, n=5):
    importance_list = np.hstack((X.columns.to_numpy().reshape(-1, 1), model.feature_importances_.reshape(-1, 1)))
    sorted_feature_importance = importance_list[importance_list[:, 1].argsort()][::-1, :] 
    for i in range(n):
        print(f"{i+1}. {sorted_feature_importance[i, 0]} ({sorted_feature_importance[i, 1]})")


def get_most_important_features_as_list(model, X, n=5):
    importance_list = np.hstack((X.columns.to_numpy().reshape(-1, 1), model.feature_importances_.reshape(-1, 1)))
    sorted_feature_importance = importance_list[importance_list[:, 1].argsort()][::-1, :] 
    result = []
    for i in range(n):
        result += [sorted_feature_importance[i, 0]]
    return result


def visualize_importance(rf_model, features):
    # Importance of Features
    figure = plt.figure()
    ax = plt.axes()

    # train_df.drop(columns=['y']).columns.to_numpy()
    ax.bar(features, np.array(rf_model.feature_importances_))

    plt.show()
