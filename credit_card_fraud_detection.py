# -*- coding: utf-8 -*-
"""Credit Card Fraud Detection.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1sU1vgdvXhDmGDTttGVglNm2x9NWxZyXe

CREDIT CARD FRAUD DETECTION PROJECT

1. Exploratory Data Analysis
2. Feature Engineering
3. Machine learning models such as logistic regression, XGboost, SVC, KNN, AdaBoost, Naive Bayes and Random Forest.
4. Deep learning model
5. Validate and compare the results
6. Detection

1. EXPLORATORY DATA ANALYSIS (EDA)
"""

# Commented out IPython magic to ensure Python compatibility.
# Importing libraries
from sklearn import preprocessing
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn import svm, tree
import xgboost
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.neural_network import MLPClassifier
from sklearn import metrics
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import GridSearchCV
import pickle
# %matplotlib inline
import datetime 
import time 
import tensorflow as tf

from google.colab import drive
drive.mount('/content/drive')

# Loading the dataset
train  = pd.read_csv('/content/drive/My Drive/Credit Card Fraud Detection Dataset/train.csv')
test  = pd.read_csv('/content/drive/My Drive/Credit Card Fraud Detection Dataset/test.csv')
submission = test[['ID']]

# Information about the data
train.info()
test.info()

# Checking for null values
train.isnull().sum()

# First 5 entries
train.head()

# Last 5 entries
train.tail()

# Datatype of each column
train.dtypes

# Basic description - statistics
train.describe()

# Data dimension
print("Data dimension     :",test.shape)
print("Data size          :",test.size)
print("Number of Row          :",len(test.index))
print("Number of Columns      :",len(test.columns))

class_values=train['Class'].value_counts()
print(class_values)

non_fraud_share=class_values[0]/train['Class'].count()*100
fraud_share=class_values[1]/train['Class'].count()*100
print(non_fraud_share)
print(fraud_share)

# Create a bar plot for the number and percentage of fraud vs non-fraud transcations
plt.figure(figsize=(15,6))

plt.subplot(121)
plt.title('Fraud BarPlot-Class Histogram', fontweight='bold',fontsize=14)
count_of_classes = pd.value_counts(train['Class'], sort = True).sort_index()
ax = count_of_classes.plot(kind = 'bar')
plt.xlabel("Class")
plt.ylabel("Frequency")
plt.xticks([0,1],["Non-Fraud","Fraud"])

total = float(len(train))
for p in ax.patches:
    height = p.get_height()
    ax.text(p.get_x()+p.get_width()/2.,
            height + 3,
            '{:1.2f}%'.format(height*100/total),
            ha="center") 


plt.subplot(122)
labels = 'Non-Fraud', 'Fraud'
train["Class"].value_counts().plot.pie(autopct = "%1.2f%%", labels=labels, startangle=90)
plt.show()

"""Conclusion : As you can observe data is imbalanced."""

# Time Distribution plot for transactions 
plt.figure(figsize=(15,7))

plt.title('Distribution of Transaction Time')
sns.distplot(train['Time'].values/(60*60))

"""Conclusion : Transaction data looks high between 10 and 20, after that it decreases to go lowest at 30 and increases again.

"""

# Storing both of them seperately
train_non_fraud = train[train.Class==0]
train_fraud = train[train.Class==1]

# Scatter plot between Amount and Time
fig = plt.figure(figsize = (8,8))
plt.scatter(train_non_fraud.Amount, train_non_fraud.Time.values/(60*60),alpha=0.5,label='Non Fraud')
plt.scatter(train_fraud.Amount, train_fraud.Time.values/(60*60),alpha=1,label='Fraud')
plt.xlabel('Amount')
plt.ylabel('Time')
plt.title('Scatter plot between Amount and Time ')
plt.legend()
plt.show()

"""Conclusion : Most of the fraud transactions involve less amount"""

f, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(12,4))

bins = 50

ax1.hist(train.Time[train.Class == 1], bins = bins)
ax1.set_title('Fraud')

ax2.hist(train.Time[train.Class == 0], bins = bins)
ax2.set_title('Non Fraud')

plt.xlabel('Time (in Seconds)')
plt.ylabel('Number of Transactions')
plt.show()

"""Conclusion : Many fraud transactions have taken place in between time of 40000 seconds and 1000000 seconds"""

# Visualizing amount distribution
# Box Plot of amount for both classes
plt.figure(figsize = (15, 6))
plt.subplot(121)
a = sns.boxplot(x = 'Class', y = 'Amount',hue='Class', data = train, showfliers=False) 
plt.setp(a.get_xticklabels(), rotation=45)

"""Conclusion : Distribution of amount for Fraud transactions is much higher than non-fraud transactions."""

# Heatmap for visualizing correlation

plt.figure(figsize=(24, 12))
sns.heatmap(train.corr(), cmap="YlGnBu", annot=True)
plt.show()

# Understanding more on the correlation in data:
print("Significant features relative to target variable Class")

corr1 = train.corr()['Class']
# convert series to dataframe so it can be sorted
corr1 = pd.DataFrame(corr1)

corr1.columns = ["Correlation"]
# sort correlation
corr2 = corr1.sort_values(by=['Correlation'], ascending=False)
corr2.head(10)

# Heatmap for relatively strong correlation (i.e. > 0.09) with the target variable:

significant_feature = corr2.index[abs(train.corr()['Class']>0.09)]
plt.subplots(figsize=(8, 5))
significant_corr = train[significant_feature].corr()
sns.heatmap(significant_corr, annot=True, cmap="YlGnBu")
plt.show()

train.isnull().sum()

"""Conclusion : No null values"""

# As we can see there are no null values

# so let take a look at the spread of each column
# Visulizing the distibution of the data for every feature
train.hist(linewidth=1, histtype='stepfilled', facecolor='g', figsize=(20, 20));

"""2. FEATURE ENGINEERING"""

# Convert time column in bank of hours in a day
# By observing the dataset, we can see there are transaction records of 2days - 48hrs time period
# Hour of transaction is generated in such a way that 1st second of the day is 0 and 86399 is the last second of the day

train['HourBank'] = ((np.where(train['Time'] > 86399 , train['Time'] - 86399 , train['Time'])) % (24 *3600) // 3600).astype(int)
test['HourBank'] = ((np.where(test['Time'] > 86399 , test['Time'] - 86399 , test['Time'])) % (24 *3600) // 3600).astype(int)
train

# Hot encoding of the hour banks

# Getting dummies
train_dummies = pd.get_dummies(train['HourBank'])

# Merging it
train = pd.concat([train, train_dummies], axis = 1)

# Dropping redundant columns
train = train.drop(['HourBank','ID','Time'], axis = 1)

train

# Similarly for test data
test_dummies = pd.get_dummies(test['HourBank'])
a = list(test_dummies.columns.values)
b = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22, 23]
c = [x for x in b if x not in a]
test_dummies = pd.concat([test_dummies, pd.DataFrame(columns = c)]).fillna(0)  
#lets merge it
test = pd.concat([test, test_dummies], axis = 1)
# then drop the redundant column
test = test.drop(['HourBank','ID','Time'], axis = 1)
test

# Shuffle dataset
# Balance the data based on column class
g = train.groupby('Class')
g = pd.DataFrame(g.apply(lambda x: x.sample(g.size().min()).reset_index(drop=True)))
g = g.reset_index(drop=True)

# shuffle dataset
g = g.sample(frac=1).reset_index(drop=True)

# Balancing and standardizing the inputs

# The inputs are all columns in the csv, except for the first one [:,0]
# (which is just the arbitrary customer IDs that bear no useful information),
# and the last one [:,-1] (which is our targets)
balanced_inputs = g.drop(['Class'],axis=1)
# The targets are in the last column. That's how datasets are conventionally organized.
balanced_targets = g['Class'].astype(np.int)
unbalanced_inputs = train.drop(['Class'],axis=1)
# The targets are in the last column. That's how datasets are conventionally organized.
unbalanced_targets = train['Class'].astype(np.int)

balanced_inputs = preprocessing.scale(balanced_inputs)
scaled_unbalanced_inputs = preprocessing.scale(unbalanced_inputs)

test_inputsx = preprocessing.scale(test)

shuffled_inputs = balanced_inputs
shuffled_targets = balanced_targets

# Count the total number of samples
samples_count = shuffled_inputs.shape[0]

# Count the samples in each subset, assuming we want 80-10-10 distribution of training, validation, and test.
# Naturally, the numbers are integers.
train_samples_count = int(0.8 * samples_count)
validation_samples_count = int(0.1 * samples_count)

# The 'test' dataset contains all remaining data.
test_samples_count = samples_count - train_samples_count - validation_samples_count

# Create variables that record the inputs and targets for training
# In our shuffled dataset, they are the first "train_samples_count" observations
train_inputs = shuffled_inputs[:train_samples_count]
train_targets = shuffled_targets[:train_samples_count]

# Create variables that record the inputs and targets for validation.
# They are the next "validation_samples_count" observations, folllowing the "train_samples_count" we already assigned
validation_inputs = shuffled_inputs[train_samples_count:train_samples_count+validation_samples_count]
validation_targets = shuffled_targets[train_samples_count:train_samples_count+validation_samples_count]

# Create variables that record the inputs and targets for test.
# They are everything that is remaining.
test_inputs = shuffled_inputs[train_samples_count+validation_samples_count:]
test_targets = shuffled_targets[train_samples_count+validation_samples_count:]

# We balanced our dataset to be 50-50 (for targets 0 and 1), but the training, validation, and test were 
# taken from a shuffled dataset. Check if they are balanced, too. Note that each time you rerun this code, 
# you will get different values, as each time they are shuffled randomly.
# Normally you preprocess ONCE, so you need not rerun this code once it is done.
# If you rerun this whole sheet, the npzs will be overwritten with your newly preprocessed data.

# Print the number of targets that are 1s, the total number of samples, and the proportion for training, validation, and test.
print(np.sum(train_targets), train_samples_count, np.sum(train_targets) / train_samples_count)
print(np.sum(validation_targets), validation_samples_count, np.sum(validation_targets) / validation_samples_count)
print(np.sum(test_targets), test_samples_count, np.sum(test_targets) / test_samples_count)

# Splitting the unbalanced into train and test

#Unbalanced datset
train_test_split(scaled_unbalanced_inputs, unbalanced_targets)
# declare 4 variables for the split
x_train1, x_test1, y_train1, y_test1 = train_test_split(scaled_unbalanced_inputs, unbalanced_targets, test_size = 0.25, random_state = 20)

"""3. Machine Learning models"""

# Quick modelling using default parameters

# A list of classifiers will be created and different classification models will be appended to it
classifiers = [] 

model1 = xgboost.XGBClassifier()
classifiers.append(model1)
model2 = svm.SVC()
classifiers.append(model2)
model3 = RandomForestClassifier()
classifiers.append(model3)
model4 = LogisticRegression()
classifiers.append(model4)
model5 = KNeighborsClassifier(3)
classifiers.append(model5)
model6 = AdaBoostClassifier()
classifiers.append(model6)
model7= GaussianNB()
classifiers.append(model7)

# Fitting the models into an array

for clf in classifiers:
    clf.fit(train_inputs,train_targets)
    y_pred= clf.predict(test_inputs)
    y_tr = clf.predict(train_inputs)
    acc_tr = accuracy_score(train_targets, y_tr)
    acc = accuracy_score(test_targets, y_pred)
    mn = type(clf).__name__
    
    print(clf)
    print("Accuracy of trainset %s is %s"%(mn, acc_tr))
    print("Accuracy of testset %s is %s"%(mn, acc))
    cm = confusion_matrix(test_targets, y_pred)
    print("Confusion Matrix of testset %s is %s"%(mn, cm))

"""4. Deep Learning"""

# Modelling

# Converting values into an array
validation_inputs = np.array(validation_inputs)
validation_targets = np.array(validation_targets)
train_targets = np.array(train_targets)
train_inputs = np.array(train_inputs)

# Set the input and output sizes
input_size = 53
output_size = 2
# Use same hidden layer size for both hidden layers. Not a necessity.
hidden_layer_size = 6
    
# define how the model will look like
model = tf.keras.Sequential([
    # tf.keras.layers.Dense is basically implementing: output = activation(dot(input, weight) + bias)
    # it takes several arguments, but the most important ones for us are the hidden_layer_size and the activation function
    tf.keras.layers.Dense(hidden_layer_size, activation='relu'), # 1st hidden layer
    tf.keras.layers.Dense(hidden_layer_size, activation='relu'), # 2nd hidden layer
    tf.keras.layers.Dense(hidden_layer_size, activation='relu'), # 2nd hidden layer
    tf.keras.layers.Dense(hidden_layer_size, activation='relu'), # 2nd hidden layer
    tf.keras.layers.Dense(hidden_layer_size, activation='relu'), # 2nd hidden layer
    # the final layer is no different, we just make sure to activate it with softmax
    tf.keras.layers.Dense(output_size, activation='softmax') # output layer
])


### Choose the optimizer and the loss function

# we define the optimizer we'd like to use, 
# the loss function, 
# and the metrics we are interested in obtaining at each iteration
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

### Training
# That's where we train the model we have built.

# set the batch size
batch_size = 100

# set a maximum number of training epochs
max_epochs = 100

# set an early stopping mechanism
# let's set patience=2, to be a bit tolerant against random validation loss increases
early_stopping = tf.keras.callbacks.EarlyStopping(patience=2)

# fit the model
# note that this time the train, validation and test data are not iterable
history = model.fit(train_inputs, # train inputs
          train_targets, # train targets
          batch_size=batch_size, # batch size
          epochs=max_epochs, # epochs that we will train for (assuming early stopping doesn't kick in)
          # callbacks are functions called by a task when a task is completed
          # task here is to check if val_loss is increasing
          callbacks=[early_stopping], # early stopping
          validation_data=(validation_inputs, validation_targets), # validation data
          verbose = 2 # making sure we get enough information about the training process
          )

# Plot the train/validation loss values
plt.figure(figsize=(15,10))
_loss = history.history['loss'][1:]
_val_loss = history.history['val_loss'][1:]

train_loss_plot, = plt.plot(range(1, len(_loss)+1), _loss, label='Train Loss')
val_loss_plot, = plt.plot(range(1, len(_val_loss)+1), _val_loss, label='Validation Loss')

_ = plt.legend(handles=[train_loss_plot, val_loss_plot])

"""5. Validation

After training on the train data and validating on the validation data, we test the final prediction power of our model by running it on the test dataset that the algorithm has NEVER seen before.
"""

test_loss, test_accuracy = model.evaluate(test_inputs, test_targets)

# Applying deep learning model to the unbalanced dataset

#firstly convert the inputs to array
y_train1 = np.array(y_train1)
y_test1 = np.array(y_test1)

# Set the input and output sizes
input_size = 53
output_size = 2
# Use same hidden layer size for both hidden layers. Not a necessity.
hidden_layer_size = 2
    
# define how the model will look like
tfk = tf.keras.Sequential([
    # tf.keras.layers.Dense is basically implementing: output = activation(dot(input, weight) + bias)
    # it takes several arguments, but the most important ones for us are the hidden_layer_size and the activation function
    tf.keras.layers.Dense(hidden_layer_size, activation='relu'), # 1st hidden layer
    tf.keras.layers.Dense(hidden_layer_size, activation='relu'), # 2nd hidden layer
    tf.keras.layers.Dense(hidden_layer_size, activation='relu'), # 2nd hidden layer
    tf.keras.layers.Dense(hidden_layer_size, activation='relu'), # 2nd hidden layer
    tf.keras.layers.Dense(hidden_layer_size, activation='relu'), # 2nd hidden layer
    # the final layer is no different, we just make sure to activate it with softmax
    tf.keras.layers.Dense(output_size, activation='softmax') # output layer
])


### Choose the optimizer and the loss function

# we define the optimizer we'd like to use, 
# the loss function, 
# and the metrics we are interested in obtaining at each iteration
tfk.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

### Training
# That's where we train the model we have built.

# set the batch size
batch_size = 100

# set a maximum number of training epochs
max_epochs = 100

# set an early stopping mechanism
# let's set patience=2, to be a bit tolerant against random validation loss increases
early_stopping = tf.keras.callbacks.EarlyStopping(patience=2)

# fit the model
# note that this time the train, validation and test data are not iterable
history = tfk.fit(x_train1, # train inputs
          y_train1, # train targets
          batch_size=batch_size, # batch size
          epochs=max_epochs, # epochs that we will train for (assuming early stopping doesn't kick in)
          # callbacks are functions called by a task when a task is completed
          # task here is to check if val_loss is increasing
          callbacks=[early_stopping], # early stopping
          validation_data=(x_test1, y_test1), # validation data
          verbose = 2 # making sure we get enough information about the training process
          )

# Plot the train/validation loss values
plt.figure(figsize=(20,10))
_loss = history.history['loss'][1:]
_val_loss = history.history['val_loss'][1:]

train_loss_plot, = plt.plot(range(1, len(_loss)+1), _loss, label='Train Loss')
val_loss_plot, = plt.plot(range(1, len(_val_loss)+1), _val_loss, label='Validation Loss')

_ = plt.legend(handles=[train_loss_plot, val_loss_plot])

"""6. Detection"""

# Predictions on test data

tfbalanced = model.predict_classes(test_inputsx)   # Deep learning with balanced data
tfunbalanced = tfk.predict_classes(test_inputsx)   # Deep Learning with unbalanced data
xgb = model1.predict(test_inputsx)                 # XGBoost with balanced data
svm = model2.predict(test_inputsx)                 # SVM with balanced data
rf = model3.predict(test_inputsx)                  # Random forest with balanced data
logreg = model4.predict(test_inputsx)              # Logistic regression with balanced data
knn = model5.predict(test_inputsx)                 # KNearest Neighbors with balanced data
ada = model6.predict(test_inputsx)                 # Adaboost with balanced data
nb = model7.predict(test_inputsx)                  # Naive Bayes with balanced data

submission['tfb'] = tfbalanced          
submission['tfu'] = tfunbalanced
submission['xgb'] = xgb
submission['svm'] = svm
submission['rfc'] = rf        
submission['logr'] = logreg
submission['knn'] = knn             
submission['ada'] = ada
submission['nbc'] = nb
submission

