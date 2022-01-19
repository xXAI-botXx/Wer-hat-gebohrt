"""
This module is used to applie machine-learning algorithm.

Contains functions for train, predict and evaluate ai-model.

Author: Tobia Ippolito
"""

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

from sklearn.model_selection import GridSearchCV

from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import cross_val_score, cross_val_predict


MODELS = Enum('MODELS', 'RANDOM_FOREST SVM LOGISTIC_REGRESSION ADA_BOOST VOTING_CLASSIFIER NAIVE_BAYES KNN')


def train_random_forest(X_train, y_train, auto_params=False, normalize=False, cv=3):
    """
    Trains a RandomForrest with the given data.

    Hyperparameters are configured by Tobia Ippolito. Alternativly GridSearch can be used. But there have to be enough data.

    The traindata can be normalize.

    :param X_train: Features which will be used for training.
    :type X_train: pd.DataFrame
    :param y_train: Target-feature which will be used for training.
    :type y_train: pd.Series
    :param auto_params: Defines whether or not using preconfigured hyperparameter or lets GridSearch tunes the model.
    :type auto_params: bool, optional
    :param normalize: Defines if the data should be normalized.
    :type normalize: bool, optional
    :param cv: Defines the number of cross-validation-datasets by auto variable = True.
    :type cv: int, optional

    :return: Returns the trained classifier.
    :rtype: sklearn.ensemble.RandomForestClassifier
    """
    # Classifier Randomforest
    if normalize:
        scaler = MinMaxScaler()
        X_train = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)

    if auto_params:
        param_grid = {'n_estimators':[10, 25, 50, 75, 100, 125, 150],
              'criterion':['gini', 'entropy'], 'min_samples_split':[2,3,4,5]}
        model = GridSearchCV(RandomForestClassifier(), param_grid, cv=cv)
    else:
        model = RandomForestClassifier(n_estimators=100, 
                                criterion = 'gini',
                                min_samples_split = 2)
    return model.fit(X_train, y_train)


def train_svc(X_train, y_train, auto_params=False, normalize=True, cv=3):
    """
    Trains a SupportVectorMachine with the given data.

    Hyperparameters are configured by Tobia Ippolito. Alternativly GridSearch can be used. But there have to be enough data.

    The traindata can be normalize.

    :param X_train: Features which will be used for training.
    :type X_train: pd.DataFrame
    :param y_train: Target-feature which will be used for training.
    :type y_train: pd.Series
    :param auto_params: Defines whether or not using preconfigured hyperparameter or lets GridSearch tunes the model.
    :type auto_params: bool, optional
    :param normalize: Defines if the data should be normalized.
    :type normalize: bool, optional
    :param cv: Defines the number of cross-validation-datasets by auto variable = True.
    :type cv: int, optional

    :return: Returns the trained classifier.
    :rtype: sklearn.svm.SVC
    """
    # Classifier Support Vector Machines
    #print(X_train)
    #print("nan:", np.isnan(X_train.any()))
    #print("inf:", np.isfinite(X_train.all()))
    #print(X_train.columns)
    if normalize:
        scaler = MinMaxScaler()
        X_train = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)

    if auto_params:
        param_grid = {'kernel':['linear', 'poly', 'rbf', 'sigmoid'],
              'probability':[True, False], 'decision_function_shape':['ovo', 'ovr'],
              'C':[0.001,0.1,0.2,0.5,1.0,1.5,2.0,2.5,3.0]  }
        model = GridSearchCV(SVC(), param_grid, cv=cv)
    else:
        model = SVC(C= 2.0, decision_function_shape='ovo', kernel='rbf', probability=True)
    return model.fit(X_train, y_train)


def train_knn(X_train, y_train, auto_params=False, normalize=True, cv=3):
    """
    Trains a K-Nearest Neighbors with the given data.

    Hyperparameters are configured by Tobia Ippolito. Alternativly GridSearch can be used. But there have to be enough data.

    The traindata can be normalize.

    :param X_train: Features which will be used for training.
    :type X_train: pd.DataFrame
    :param y_train: Target-feature which will be used for training.
    :type y_train: pd.Series
    :param auto_params: Defines whether or not using preconfigured hyperparameter or lets GridSearch tunes the model.
    :type auto_params: bool, optional
    :param normalize: Defines if the data should be normalized.
    :type normalize: bool, optional
    :param cv: Defines the number of cross-validation-datasets by auto variable = True.
    :type cv: int, optional

    :return: Returns the trained classifier.
    :rtype: sklearn.neighbors.KNeighborsClassifier
    """
    # Classifier K-Nearest Neighbors
    if normalize:
        scaler = MinMaxScaler()
        X_train = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)

    if auto_params:
        param_grid = {'n_neighbors':[1,2,3,4,5,6,7,8,9],
              'weights':['uniform', 'distance'], 'algorithm':['auto', 'ball_tree', 'kd_tree', 'brute'],
              'metric':['minkowski', 'euclidean', 'manhattan', 'chebyshev']  }
        model = GridSearchCV(KNeighborsClassifier(), param_grid, cv=cv)
    else:
        model = KNeighborsClassifier(algorithm='auto', metric='manhattan', n_neighbors=len(X_train)//2, weights='distance')
    return model.fit(X_train, y_train)

def train_adaboost(X_train, y_train, auto_params=False, normalize=True, cv=3):
    """
    Trains a AdaBoost with the given data.

    Hyperparameters are configured by Tobia Ippolito. Alternativly GridSearch can be used. But there have to be enough data.

    The traindata can be normalize.

    :param X_train: Features which will be used for training.
    :type X_train: pd.DataFrame
    :param y_train: Target-feature which will be used for training.
    :type y_train: pd.Series
    :param auto_params: Defines whether or not using preconfigured hyperparameter or lets GridSearch tunes the model.
    :type auto_params: bool, optional
    :param normalize: Defines if the data should be normalized.
    :type normalize: bool, optional
    :param cv: Defines the number of cross-validation-datasets by auto variable = True.
    :type cv: int, optional

    :return: Returns the trained classifier.
    :rtype: sklearn.ensemble.AdaBoostClassifier
    """
    # Classifier Ada-Boost with SVC
    if normalize:
        scaler = MinMaxScaler()
        X_train = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)

    if auto_params:
        model_1 = SVC(C= 0.1, decision_function_shape='ovo', kernel='rbf', probability=True)
        model_2 = RandomForestClassifier()
        model_3 = KNeighborsClassifier(algorithm='auto', metric='manhattan', n_neighbors=len(X_train)//2, weights='distance')
        param_grid = {'base_estimator':[model_1, model_2, model_3],
                    'n_estimators':[20, 40, 50], 'learning_rate':[0.5, 1.0, 1.5, 2.0],
                    'algorithm':["SAMME", "SAMME.R"]  }
        model = GridSearchCV(AdaBoostClassifier(), param_grid, cv=cv)
    else:
        model = AdaBoostClassifier(base_estimator=SVC(C=2.0, decision_function_shape='ovo', kernel='rbf', probability=True), 
                            learning_rate=0.5, n_estimators=20, algorithm='SAMME')
    return model.fit(X_train, y_train)

def train_naive_bayes(X_train, y_train, auto_params=False, normalize=True, cv=3):
    """
    Trains a Naive Bayes with the given data.

    Hyperparameters are configured by Tobia Ippolito. Alternativly GridSearch can be used. But there have to be enough data.

    The traindata can be normalize.

    :param X_train: Features which will be used for training.
    :type X_train: pd.DataFrame
    :param y_train: Target-feature which will be used for training.
    :type y_train: pd.Series
    :param auto_params: Defines whether or not using preconfigured hyperparameter or lets GridSearch tunes the model.
    :type auto_params: bool, optional
    :param normalize: Defines if the data should be normalized.
    :type normalize: bool, optional
    :param cv: Defines the number of cross-validation-datasets by auto variable = True.
    :type cv: int, optional

    :return: Returns the trained classifier.
    :rtype: sklearn.naive_bayes.GaussianNB
    """
    # Classifier Naive Bayes
    if normalize:
        scaler = MinMaxScaler()
        X_train = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)

    if auto_params:
        model = GaussianNB()
    else:
        model = GaussianNB()
    return model.fit(X_train, y_train)

def train_logistic_regression(X_train, y_train, auto_params=False, normalize=True, cv=3):
    """
    Trains a Logistic Regression with the given data.

    Hyperparameters are configured by Tobia Ippolito. Alternativly GridSearch can be used. But there have to be enough data.

    The traindata can be normalize.

    :param X_train: Features which will be used for training.
    :type X_train: pd.DataFrame
    :param y_train: Target-feature which will be used for training.
    :type y_train: pd.Series
    :param auto_params: Defines whether or not using preconfigured hyperparameter or lets GridSearch tunes the model.
    :type auto_params: bool, optional
    :param normalize: Defines if the data should be normalized.
    :type normalize: bool, optional
    :param cv: Defines the number of cross-validation-datasets by auto variable = True.
    :type cv: int, optional

    :return: Returns the trained classifier.
    :rtype: sklearn.linear_model.LogisticRegression
    """
    # Classifier Logistic Regression
    if normalize:
        scaler = MinMaxScaler()
        X_train = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)

    if auto_params:
        param_grid = {'penalty':['l1', 'l2', 'none', 'elasticnet'],
              'solver':['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga'],
              'C':[0.001,0.1,0.2,0.5,1.0,1.5,2.0,2.5,3.0]  }
        model = GridSearchCV(LogisticRegression(), param_grid, cv=cv)
    else:
        model = LogisticRegression(penalty='none', solver='newton-cg')    #C=0.001, 
    return model.fit(X_train, y_train)

def train_voting_classifier(X_train, y_train, auto_params=False, normalize=True, cv=3):
    """
    Trains a Voting Classifier with the given data.

    Hyperparameters are configured by Tobia Ippolito. Alternativly GridSearch can be used. But there have to be enough data.

    The traindata can be normalize.

    :param X_train: Features which will be used for training.
    :type X_train: pd.DataFrame
    :param y_train: Target-feature which will be used for training.
    :type y_train: pd.Series
    :param auto_params: Defines whether or not using preconfigured hyperparameter or lets GridSearch tunes the model.
    :type auto_params: bool, optional
    :param normalize: Defines if the data should be normalized.
    :type normalize: bool, optional
    :param cv: Defines the number of cross-validation-datasets by auto variable = True.
    :type cv: int, optional

    :return: Returns the trained classifier.
    :rtype: sklearn.ensemble.VotingClassifier
    """
    # Classifier Logistic Regression
    if normalize:
        scaler = MinMaxScaler()
        X_train = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)

    estimators = [('SVC', SVC(C= 2.0, decision_function_shape='ovo', kernel='rbf', probability=True)), 
                ('RandomForest', RandomForestClassifier(n_estimators=100, criterion = 'gini', min_samples_split = 2)),
                ('KNN', KNeighborsClassifier(algorithm='auto', metric='manhattan', n_neighbors=len(X_train)//2, weights='distance')),
                ('AdaBoost_SVC', AdaBoostClassifier(base_estimator=SVC(C=2.0, decision_function_shape='ovo', kernel='rbf', probability=True), learning_rate=0.5, n_estimators=20, algorithm='SAMME')),
                ('AdaBoost_RF', AdaBoostClassifier(base_estimator=RandomForestClassifier(n_estimators=100, criterion = 'gini', min_samples_split = 2), learning_rate=0.5, n_estimators=20, algorithm='SAMME')),
                ('NaiveBayes',  GaussianNB())]
    model = VotingClassifier(estimators=estimators, voting='hard')
    return model.fit(X_train, y_train)

def predict(model, predict_data, X_train, normalize=False):
    """
    Predicts new data with a model. 
    Can normalize the data.

    :param model: Model used for prediction.
    :type model: sklearn.base.BaseEstimator
    :param predict_data: Data which will be predict.
    :type predict_data: pd.DataFrame
    :param X_train: Data which will be used for normalization.
    :type X_train: pd.DataFrame
    :param normalize: Defines if the data should be normalize (if True, uses X_train for normalization).
    :type normalize: bool, optional

    :return: A list of predicted classes.
    :rtype: numpy.ndarray
    """
    if normalize:
        scaler = MinMaxScaler().fit(X_train)
        predict_data = pd.DataFrame(scaler.transform(predict_data), columns=predict_data.columns)
    return model.predict(predict_data)


def predict_proba(model, predict_data, X_train, normalize=False):
    """
    Predicts new data with a model in percent. 
    Can normalize the data.

    :param model: Model used for prediction.
    :type model: sklearn.base.BaseEstimator
    :param predict_data: Data which will be predict.
    :type predict_data: pd.DataFrame
    :param X_train: Data which will be used for normalization.
    :type X_train: pd.DataFrame
    :param normalize: Defines if the data should be normalize (if True, uses X_train for normalization).
    :type normalize: bool, optional

    :return: A list of predicted classes with the 2 probabilities.
    :rtype: numpy.ndarray
    """
    if normalize:
        scaler = MinMaxScaler().fit(X_train)
        predict_data = pd.DataFrame(scaler.transform(predict_data), columns=predict_data.columns)
    return model.predict_proba(predict_data)


def evaluate_model(model, X_test, y_test, X_train, normalize=False):
    """
    Evaluats a model. 
    Means predict new data and returns the accuracy and confusion-matrix. 
    Can normalize the data.

    :param model: Model used for evaluation.
    :type model: sklearn.base.BaseEstimator
    :param X_test: Data which will be predict.
    :type X_test: pd.DataFrame
    :param y_test: Target value of the test-data.
    :type y_test: pd.Series
    :param X_train: Data which will be used for normalization.
    :type X_train: pd.DataFrame
    :param normalize: Defines if the data should be normalize (if True, uses X_train for normalization).
    :type normalize: bool, optional

    :return: A list of predicted classes with the 2 probabilities.
    :rtype: tuple of accuracy and confusion matrix.
    """
    # normalize
    if normalize:
        scaler = MinMaxScaler().fit(X_train)
        X_test = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns)

    # accuracy
    y_pred = model.predict(X_test)
    #print(f"Accuracy: ", accuracy_score(y_test, y_pred)*100)

    # confusion_matrix
    #print("--------\nConfusion Matrix:")
    #print(confusion_matrix(y_test, y_pred), "\n")
    #print("--------")
    return accuracy_score(y_test, y_pred)*100, confusion_matrix(y_test, y_pred)


# give Enum or sklearn model in
def evaluate_model_with_cross_validation(X, y, model=MODELS.RANDOM_FOREST, cv=5):
    """
    Evaluats a model with cross-validation. 
    

    :param X: Features which will be splittet in train and validation datasets.
    :type X: pd.DataFrame
    :param y: Target value of the data (which will be splittet in train and validation datasets).
    :type y: pd.Series
    :param model: Model used for evaluation.
    :type model: :class:`~anoog.model.model.MODELS`
    :param cv: Defines the number of cross-validation-datasets.
    :type cv: int, optional

    :return: A list of predicted classes with the 2 probabilities.
    :rtype: tuple of accuracy and confusion matrix.
    """
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
    """
    Calculates the n most important features of a RandomForestClassifier.
    Prints the result. See :func:`~anoog.model.model.get_most_important_features_as_list` for getting a result returned.

    :param model: Model used for feature-selection.
    :type model: sklearn.base.BaseEstimator
    :param X: Features which will be used for information-source by columns specifications.
    :type X: pd.DataFrame
    :param n: Number of Features to select.
    :type n: int
    """
    importance_list = np.hstack((X.columns.to_numpy().reshape(-1, 1), model.feature_importances_.reshape(-1, 1)))
    sorted_feature_importance = importance_list[importance_list[:, 1].argsort()][::-1, :] 
    for i in range(n):
        print(f"{i+1}. {sorted_feature_importance[i, 0]} ({sorted_feature_importance[i, 1]})")


def get_most_important_features_as_list(model, X, n=5):
    """
    Calculates the n most important features of a RandomForestClassifier.
    
    :param model: Model used for feature-selection.
    :type model: sklearn.base.BaseEstimator
    :param X: Features which will be used for information-source by columns specifications.
    :type X: pd.DataFrame
    :param n: Number of Features to select.
    :type n: int

    :return: Most important features.
    :rtype: list of names of selected-features.
    """
    importance_list = np.hstack((X.columns.to_numpy().reshape(-1, 1), model.feature_importances_.reshape(-1, 1)))
    sorted_feature_importance = importance_list[importance_list[:, 1].argsort()][::-1, :] 
    result = []
    for i in range(n):
        result += [sorted_feature_importance[i, 0]]
    return result
