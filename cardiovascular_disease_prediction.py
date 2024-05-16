# -*- coding: utf-8 -*-
"""Cardiovascular Disease Predictor.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/12pMvLZ1tmUaBB3TzCt54NMU_jffoPKCi

# **Cardiovascular Disease Predictor**
*Rohan Shah*

# Part 1: Introduction

I chose to discover the various health factors that most evidently are correlated with a positive case of Cardiovascular Disease. Going into the project, I intended to see how factors such as diet, exercise, health history, and even demographics can all be potential predictors of heart disease, which led me to want to build a model that would predict whether or not the person is at risk for heart disease with reasonable levels of sensitivity and specificity.

I used a dataset with a preselected set of variables specifically relevant to heart disease, and all of the data used has been taken from the Behavioral Risk Factor Surveillance System from 2021. Using the data presented, I sought to specifically view the data in comparison to the diagnosis of heart disease per patient, and then draw conclusions from there. I also utilized a dataset with additional numerical variables relevant from heart disease taken from the Behavioral Risk Factor Surveillance System from 2015.

The results are below, along with various takeaways, methodologies used to gather my findings, and conclusions after each section. Enjoy!

# Part 2: Data Loading
"""

# imports necessary for project
!pip install kaggle
!pip install pandasql
!pip install sqlalchemy==1.4.46
!pip install imbalanced-learn
!pip install plotly

import pandas as pd
import pandasql as psql
import plotly.express as px
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from google.colab import drive
from prettytable import PrettyTable
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import confusion_matrix
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import make_scorer, recall_score
from sklearn.metrics import classification_report

"""## Loading & Analyzing Data

"""

# Mounting google drive in order to access Kaggle data set
drive.mount('/content/drive')

# Create the kaggle directory (only run when restarting kernal!)
!mkdir ~/.kaggle

# Read the uploaded kaggle.json file
!cp /content/drive/MyDrive/kaggle.json ~/.kaggle/

# Download datasets
!!kaggle datasets download -d alphiree/cardiovascular-diseases-risk-prediction-dataset
!!kaggle datasets download -d alexteboul/heart-disease-health-indicators-dataset

# Unzip folders in Colab content folder
!unzip /content/cardiovascular-diseases-risk-prediction-dataset.zip
!unzip /content/heart-disease-health-indicators-dataset.zip

# Read the csv files and save them to dataframes called "BRFSS_2021" and "BRFSS_2015"
BRFSS_2021 = pd.read_csv('CVD_cleaned.csv')
BRFSS_2015 = pd.read_csv('heart_disease_health_indicators_BRFSS2015.csv')
original = BRFSS_2021.copy()

"""#Part 3: Exploratory Data Analysis and Visualization"""

#explore top few columns of datasets
BRFSS_2021.head(10)

BRFSS_2015.head(10)

# datatypes & details of our datasets
BRFSS_2021.dtypes

BRFSS_2021.info()

BRFSS_2021.describe()

BRFSS_2015.dtypes

BRFSS_2015.info()

BRFSS_2015.describe()

#check for null values
nulls = BRFSS_2021.isnull().sum()
print(nulls)

#check for null values
nulls = BRFSS_2015.isnull().sum()
print(nulls)

#inspect all non-numeric columns to figure out how to deal with them
for column in BRFSS_2021.columns:
  if BRFSS_2021[column].dtype == "object":
    print(BRFSS_2021[column].unique())

#apply SQL queries to encode categorical variables
query_general_health = """
SELECT
  CASE
    WHEN General_Health = 'Poor' THEN 0
    WHEN General_Health = 'Fair' THEN 1
    WHEN General_Health = 'Good' THEN 2
    WHEN General_Health = 'Very Good' THEN 3
    WHEN General_Health = 'Excellent' THEN 4
  END as General_Health
FROM BRFSS_2021;
"""

query_checkup = """
SELECT
  CASE
    WHEN Checkup = 'Within the past year' THEN 0
    WHEN Checkup = 'Within the past 2 years' THEN 1
    WHEN Checkup = 'Within the past 5 years' THEN 2
    WHEN Checkup = '5 or more years ago' THEN 3
    WHEN Checkup = 'Never' THEN 4
  END as Checkup
FROM BRFSS_2021;
"""

query_exercise = """
SELECT
  CASE
    WHEN Exercise = 'No' THEN 0
    WHEN Exercise = 'Yes' THEN 1
  END as Exercise
FROM BRFSS_2021;
"""

query_heart_disease = """
SELECT
  CASE
    WHEN Heart_Disease = 'No' THEN 0
    WHEN Heart_Disease = 'Yes' THEN 1
  END as Heart_Disease
FROM BRFSS_2021;
"""

query_skin_cancer = """
SELECT
  CASE
    WHEN Skin_Cancer = 'No' THEN 0
    WHEN Skin_Cancer = 'Yes' THEN 1
  END as Skin_Cancer
FROM BRFSS_2021;
"""

query_other_cancer = """
SELECT
  CASE
    WHEN Other_Cancer = 'No' THEN 0
    WHEN Other_Cancer = 'Yes' THEN 1
  END as Other_Cancer
FROM BRFSS_2021;
"""

query_depression = """
SELECT
  CASE
    WHEN Depression = 'No' THEN 0
    WHEN Depression = 'Yes' THEN 1
  END as Depression
FROM BRFSS_2021;
"""

query_diabetes = """
SELECT
  CASE
    WHEN Diabetes = 'No' THEN 0
    WHEN Diabetes = 'No, pre-diabetes or borderline diabetes' THEN 1
    WHEN Diabetes = 'Yes, but female told only during pregnancy' THEN 2
    WHEN Diabetes = 'Yes' THEN 3
  END as Diabetes
FROM BRFSS_2021;
"""

query_arthritis = """
SELECT
  CASE
    WHEN Arthritis = 'No' THEN 0
    WHEN Arthritis = 'Yes' THEN 1
  END as Arthritis
FROM BRFSS_2021;
"""

query_sex = """
SELECT
  CASE
    WHEN Sex = 'Female' THEN 0
    WHEN Sex = 'Male' THEN 1
  END as Sex
FROM BRFSS_2021;
"""

query_age_category = """
SELECT
  CASE
    WHEN Age_Category = '18-24' THEN 0
    WHEN Age_Category = '25-29' THEN 1
    WHEN Age_Category = '30-34' THEN 2
    WHEN Age_Category = '35-39' THEN 3
    WHEN Age_Category = '40-44' THEN 4
    WHEN Age_Category = '45-49' THEN 5
    WHEN Age_Category = '50-54' THEN 6
    WHEN Age_Category = '55-59' THEN 7
    WHEN Age_Category = '60-64' THEN 8
    WHEN Age_Category = '65-69' THEN 9
    WHEN Age_Category = '70-74' THEN 10
    WHEN Age_Category = '75-79' THEN 11
    WHEN Age_Category = '80+' THEN 12
  END as Age_Category
FROM BRFSS_2021;
"""

query_smoking_history = """
SELECT
  CASE
    WHEN Smoking_History = 'No' THEN 0
    WHEN Smoking_History = 'Yes' THEN 1
  END as Smoking_History
FROM BRFSS_2021;
"""

query_diet = """
SELECT
  (Fruit_Consumption + Green_Vegetables_Consumption - FriedPotato_Consumption)
  as Diet
FROM BRFSS_2021;
"""

# putting each of these individual queries into dataframes
df_general_health = psql.sqldf(query_general_health, locals())
df_checkup = psql.sqldf(query_checkup, locals())
df_exercise = psql.sqldf(query_exercise, locals())
df_heart_disease = psql.sqldf(query_heart_disease, locals())
df_skin_cancer = psql.sqldf(query_skin_cancer, locals())
df_other_cancer = psql.sqldf(query_other_cancer, locals())
df_depression = psql.sqldf(query_depression, locals())
df_diabetes = psql.sqldf(query_diabetes, locals())
df_arthritis = psql.sqldf(query_arthritis, locals())
df_sex = psql.sqldf(query_sex, locals())
df_age_category = psql.sqldf(query_age_category, locals())
df_smoking_history = psql.sqldf(query_smoking_history, locals())
df_diet = psql.sqldf(query_diet, locals())

# concatting our dataframes back into BRFSS_2021
BRFSS_2021 = pd.concat([
    df_general_health,
    df_checkup,
    df_exercise,
    df_heart_disease,
    df_skin_cancer,
    df_other_cancer,
    df_depression,
    df_diabetes,
    df_arthritis,
    df_sex,
    df_age_category,
    df_smoking_history,
    df_diet,
    BRFSS_2021[["Height_(cm)","Weight_(kg)","BMI","Alcohol_Consumption"]]
], axis=1)

#our new dataframe
BRFSS_2021.head(10)

# count plot of general health numbers - gives us a sense of initial questioning

plt.figure(figsize=(8, 6))
sns.countplot(data=BRFSS_2021, x='General_Health')
plt.title('Total People by General Health Responses')
plt.xlabel('General Health Response')
plt.ylabel('People')

health_types = {
    '0': 'Poor',
    '1': 'Fair',
    '2': 'Good',
    '3': 'Very Good',
    '4': 'Excellent'
}

plt.xticks(ticks=range(len(health_types)), labels=list(health_types.values()))
plt.show()

# histogram of bmi distribution of dataset

plt.figure(figsize=(8, 6))
plt.hist(BRFSS_2021['BMI'], bins=50)
plt.title('Distribution of BMI')
plt.xlabel('BMI')
plt.ylabel('Frequency')
plt.show()

# box plot measuring relationship between BMI values and reported exercise

sns.boxplot(x='Exercise', y='BMI', data=BRFSS_2021)
plt.title('Box Plot of BMI by Exercise Level')
plt.xlabel('Exercise Level')
plt.ylabel('BMI')
plt.show()

# barplot of various disease distribution amongst users split by gender

disease_columns = ['Heart_Disease', 'Skin_Cancer', 'Other_Cancer', 'Diabetes', 'Arthritis']
original[disease_columns] = original[disease_columns].apply(lambda x: x.map({'Yes': 1, 'No': 0}))
df_melted = pd.melt(original, id_vars='Sex', value_vars=disease_columns, var_name='Disease', value_name='Affected')
plt.figure(figsize=(10, 6))
sns.barplot(x='Sex', y='Affected', hue='Disease', data=df_melted, palette='viridis')
plt.title('Distribution of Diseases by Gender')
plt.ylabel('Number of Individuals')
plt.show()

# barplot comparing exercise habits to reports of general health

original['Exercise'] = original['Exercise'].map({'Yes': 1, 'No': 0})
plt.figure(figsize=(8, 6))
sns.barplot(x='General_Health', y='Exercise', data=original, palette='Set2')
plt.title('Exercise Habits Across General Health Categories')
plt.ylabel('Percentage of Individuals Exercising')
plt.xlabel('General Health')
plt.show()

# breakdown of smoking history answers split by gender, represented through FacetGrid

g = sns.FacetGrid(BRFSS_2021, col='Sex', height=6)
order = BRFSS_2021['Smoking_History'].value_counts().index
g.map(sns.countplot, 'Smoking_History', palette='husl', order=order)

g.set_axis_labels('Smoking History', 'Number of Respondants')
g.set_xticklabels(labels=['No', 'Yes'])

g.set_titles(col_template="{col_name}")
g.axes[0, 0].set_title("Sex = Female")
g.axes[0, 1].set_title("Sex = Male")
plt.show()

# standard box plot of comparison between age and weight

sns.boxplot(x=BRFSS_2021['Age_Category'], y=BRFSS_2021['Weight_(kg)'])
plt.title('Box Plot of Age and Weight')
plt.xlabel('Age Category')
plt.ylabel('Weight (kg)')
plt.show()

# interactive scatter plot showing BMI vs. age, color coding those that have been diagnosed with heart disease

BRFSS_2021_positive_diets = BRFSS_2021[BRFSS_2021['Diet'] > 0]

sampled_data = BRFSS_2021_positive_diets.sample(n=1000, random_state=42)

fig = px.scatter(sampled_data, x="BMI", y="Age_Category", color="Heart_Disease",
                 size="Diet", hover_name="General_Health",
                 labels={"Heart_Disease": "Has Heart Disease"},
                 title="Scatter Plot of BMI vs Age with Heart Disease Color Coding")

fig.update_layout(yaxis_title_text="Age Category", yaxis_title_standoff=20)

fig.show()

# crosstabs for object columns to determine breakdowns of heart disease related to the certain features

categoricals = original.select_dtypes(include='object')

category_crosstabs = {}

for column in categoricals.columns:
    crosstab = pd.crosstab(index=original[column], columns=original['Heart_Disease'], margins=True, margins_name='Total')
    category_crosstabs[column] = crosstab

for column, crosstab in category_crosstabs.items():
    print(f"Crosstab for {column}:\n")

    table = PrettyTable()
    table.field_names = ["Category", "No Heart Disease", "Heart Disease", "Total"]

    for index, row in crosstab.iterrows():
        table.add_row([index, row[0], row[1], row['Total']])

    print(table)
    print("\n")

# correlation heatmap
plt.figure(figsize=(12,12))
fig = sns.heatmap(data = BRFSS_2021.corr(), cmap = 'RdBu', vmin = -1, vmax = 1, annot = True, fmt=".2f")
plt.show()

BRFSS_2021_cleaned = BRFSS_2021.drop(columns={'Height_(cm)', 'Weight_(kg)'})

# new correlation with cleaned data heatmap
plt.figure(figsize=(12,12))
fig = sns.heatmap(data = BRFSS_2021_cleaned.corr(), cmap = 'RdBu', vmin = -1, vmax = 1, annot = True, fmt=".2f")
plt.show()

"""# Part 4: Modeling

##4.1 Creating Training and Testing Datasets
"""

#extract feature columns
features = BRFSS_2021_cleaned.drop(columns=["Heart_Disease"])

#extract target column
target = BRFSS_2021_cleaned["Heart_Disease"]

#split into training and testing data
seed = 42
X_train,X_test,y_train,y_test = train_test_split(features,target,test_size=0.2,random_state=seed)

"""##4.2 Fitting Models Over Standard Data

###4.2.1 Baseline Logistic Regression Model
"""

# Create a pipeline with StandardScaler and logistic regression
pipeline_lr = Pipeline([
    ('scaler', StandardScaler()),
    ('logistic_regression', LogisticRegression(max_iter=1000))
])

# Define gridsearch parameters for tuning
param_grid_lr = {
    'logistic_regression__penalty': ['l1', 'l2', None],
    'logistic_regression__C': [0.1, 1],
    'logistic_regression__solver': ['saga']  # Both support 'l1'
}

# Initialize grid search with 5 folds for each candidate
grid_search_lr = GridSearchCV(pipeline_lr, param_grid_lr, cv=5, scoring="accuracy",verbose=1.1)

# Fit the model
grid_search_lr.fit(X_train, y_train)

# Best parameters and best score
print("Best parameters for Logistic Regression:", grid_search_lr.best_params_)
print("Best score for Logistic Regression:", grid_search_lr.best_score_)

# Predict on the test set
y_pred_lr = grid_search_lr.predict(X_test)

#Retrieve feature importance breakdowns
best_pipeline = grid_search_lr.best_estimator_
best_model = best_pipeline.named_steps['logistic_regression']
feature_importance = best_model.coef_[0]
feature_names = features.columns.tolist()
imp = zip(feature_names,feature_importance)
orderedImp = sorted(imp,key=lambda v: abs(v[1]), reverse=True)
for n,i in orderedImp:
  print(f"{n}: {i}")

"""###4.2.2 Logistic Regression Model with PCA"""

# Create a pipeline with PCA and logistic regression
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('pca', PCA(n_components=0.80)),
    ('logistic_regression', LogisticRegression(max_iter=1000))
])

# Define the parameter grid
param_grid_pca = {
    'logistic_regression__penalty': ['l1', 'l2', None],
    'logistic_regression__C': [0.1, 1],
    'logistic_regression__solver': ['saga']
}

# Initialize the GridSearchCV object
grid_search_pca = GridSearchCV(pipeline, param_grid_pca, cv=5, scoring="accuracy",verbose=1.1)

# Fit the model
grid_search_pca.fit(X_train, y_train)

# Best parameters and best score
print("Best parameters for PCA Logistic Regression:", grid_search_pca.best_params_)
print("Best score for PCA Logistic Regression:", grid_search_pca.best_score_)

# Predict on the test set
y_pred_pca = grid_search_pca.predict(X_test)

"""###4.2.3 Random Forest Model"""

# Define the parameter grid
param_grid_rf = {
    'max_depth': [None, 10],
    'min_samples_split': [2, 5]
}

# Initialize the GridSearchCV object
grid_search_rf = GridSearchCV(RandomForestClassifier(), param_grid_rf, cv=5, scoring='accuracy',verbose=1.1)

# Fit the model
grid_search_rf.fit(X_train, y_train)

# Best parameters and best score
print("Best parameters:", grid_search_rf.best_params_)
print("Best score:", grid_search_rf.best_score_)

# Predict on the test set
y_pred_rf = grid_search_rf.predict(X_test)

best_model = grid_search_rf.best_estimator_
feature_importance = best_model.feature_importances_
feature_names = features.columns.tolist()
imp = zip(feature_names,feature_importance)
orderedImp = sorted(imp,key=lambda v: abs(v[1]), reverse=True)
for n,i in orderedImp:
  print(f"{n}: {i}")

"""###4.2.4 KNN Model"""

# Initialize the KNN model
knn = KNeighborsClassifier()

# Define the parameter grid for KNN
param_grid_knn = {
    'n_neighbors': [3, 5],  # Number of neighbors
}

# Initialize the GridSearchCV object for KNN
grid_search_knn = GridSearchCV(knn, param_grid_knn, cv=5, scoring='accuracy',verbose=1.1)

# Fit the model
grid_search_knn.fit(X_train, y_train)

# Best parameters and best score
print("Best parameters for KNN:", grid_search_knn.best_params_)
print("Best score for KNN:", grid_search_knn.best_score_)

# Predict on the test set
y_pred_knn = grid_search_knn.predict(X_test)

"""###4.2.5 Summary of Model Performances"""

confusion = confusion_matrix(y_test,y_pred_lr)
print("Confusion Matrix for Logistic Regression:")
print(confusion)
classification_rep = classification_report(y_test, y_pred_lr)
print("Classification Report for Logistic Regression:")
print(classification_rep)
print()

confusion = confusion_matrix(y_test,y_pred_pca)
print("Confusion Matrix for Logistic Regression with PCA:")
print(confusion)
classification_rep = classification_report(y_test, y_pred_pca)
print("Classification Report for Logistic Regression with PCA:")
print(classification_rep)
print()

confusion = confusion_matrix(y_test,y_pred_rf)
print("Confusion Matrix for Random Forest:")
print(confusion)
classification_rep = classification_report(y_test, y_pred_rf)
print("Classification Report for Random Forest:")
print(classification_rep)
print()

confusion = confusion_matrix(y_test,y_pred_knn)
print("Confusion Matrix for KNN:")
print(confusion)
classification_rep = classification_report(y_test, y_pred_knn)
print("Classification Report for KNN:")
print(classification_rep)

"""#4.3 Fitting Models Over Synthetically-Enhanced Data

###4.3.1 Logistic Regression Model
"""

# Create a pipeline with StandardScaler and logistic regression
pipeline_lr = ImbPipeline([
    ('smote', SMOTE(random_state=seed)),
    ('scaler', StandardScaler()),
    ('logistic_regression', LogisticRegression(max_iter=1000))
])


# Define the parameter grid for logistic regression
param_grid_lr = {
    'logistic_regression__penalty': ['l1', 'l2', None],
    'logistic_regression__C': [0.1, 1],
    'logistic_regression__solver': ['saga']  # Both support 'l1'
}

# Initialize the GridSearchCV object for the pipeline
grid_search_lr = GridSearchCV(pipeline_lr, param_grid_lr, cv=5, scoring="accuracy",verbose=1.1)

# Fit the model
grid_search_lr.fit(X_train, y_train)

# Best parameters and best score
print("Best parameters for Logistic Regression:", grid_search_lr.best_params_)
print("Best score for Logistic Regression:", grid_search_lr.best_score_)

# Predict on the test set
y_pred_lr = grid_search_lr.predict(X_test)

best_pipeline = grid_search_lr.best_estimator_
best_model = best_pipeline.named_steps['logistic_regression']
feature_importance = best_model.coef_[0]
feature_names = features.columns.tolist()
imp = zip(feature_names,feature_importance)
orderedImp = sorted(imp,key=lambda v: abs(v[1]), reverse=True)
for n,i in orderedImp:
  print(f"{n}: {i}")

"""###4.3.2 Logistic Regression Model with PCA"""

# Create a pipeline with PCA and logistic regression
pipeline = ImbPipeline([
    ('smote', SMOTE(random_state=seed)),
    ('scaler', StandardScaler()),
    ('pca', PCA(n_components=0.80)),
    ('logistic_regression', LogisticRegression(max_iter=1000))
])

# Define the parameter grid
param_grid_pca = {
    'logistic_regression__penalty': ['l1', 'l2', None],
    'logistic_regression__C': [0.1, 1],
    'logistic_regression__solver': ['saga']
}

# Initialize the GridSearchCV object
grid_search_pca = GridSearchCV(pipeline, param_grid_pca, cv=5, scoring="accuracy",verbose=1.1)

# Fit the model
grid_search_pca.fit(X_train, y_train)

# Best parameters and best score
print("Best parameters for PCA Logistic Regression:", grid_search_pca.best_params_)
print("Best score for PCA Logistic Regression:", grid_search_pca.best_score_)

# Predict on the test set
y_pred_pca = grid_search_pca.predict(X_test)

"""###4.3.3 Random Forest Model"""

# Define the parameter grid
pipeline_rf = ImbPipeline([
    ('smote', SMOTE(random_state=seed)),
    ('random_forest', RandomForestClassifier())
])

param_grid_rf = {
    'random_forest__max_depth': [None, 10],
    'random_forest__min_samples_split': [2, 5]
}

# Initialize the GridSearchCV object
grid_search_rf = GridSearchCV(pipeline_rf, param_grid_rf, cv=5, scoring='accuracy',verbose=1.1)

# Fit the model
grid_search_rf.fit(X_train, y_train)

# Best parameters and best score
print("Best parameters:", grid_search_rf.best_params_)
print("Best score:", grid_search_rf.best_score_)

# Predict on the test set
y_pred_rf = grid_search_rf.predict(X_test)

best_pipeline = grid_search_rf.best_estimator_
best_model = best_pipeline.named_steps['random_forest']
feature_importance = best_model.feature_importances_
feature_names = features.columns.tolist()
imp = zip(feature_names,feature_importance)
orderedImp = sorted(imp,key=lambda v: abs(v[1]), reverse=True)
for n,i in orderedImp:
  print(f"{n}: {i}")

"""###4.3.4 KNN Model"""

pipeline_knn = ImbPipeline([
    ('smote', SMOTE(random_state=42)),
    ('knn', KNeighborsClassifier())
])

# Define the parameter grid for KNN
param_grid_knn = {
    'knn__n_neighbors': [3, 5],  # Number of neighbors
}

# Initialize the GridSearchCV object for KNN
grid_search_knn = GridSearchCV(pipeline_knn, param_grid_knn, cv=5, scoring='accuracy',verbose=1.1)

# Fit the model
grid_search_knn.fit(X_train, y_train)

# Best parameters and best score
print("Best parameters for KNN:", grid_search_knn.best_params_)
print("Best score for KNN:", grid_search_knn.best_score_)

# Predict on the test set
y_pred_knn = grid_search_knn.predict(X_test)

"""###4.3.5 Summary of Model Performances Utilizing SMOTE"""

confusion = confusion_matrix(y_test,y_pred_lr)
print("Confusion Matrix for Logistic Regression:")
print(confusion)
classification_rep = classification_report(y_test, y_pred_lr)
print("Classification Report for Logistic Regression:")
print(classification_rep)
print()

confusion = confusion_matrix(y_test,y_pred_pca)
print("Confusion Matrix for Logistic Regression with PCA:")
print(confusion)
classification_rep = classification_report(y_test, y_pred_pca)
print("Classification Report for Logistic Regression with PCA:")
print(classification_rep)
print()

confusion = confusion_matrix(y_test,y_pred_rf)
print("Confusion Matrix for Random Forest:")
print(confusion)
classification_rep = classification_report(y_test, y_pred_rf)
print("Classification Report for Random Forest:")
print(classification_rep)
print()

confusion = confusion_matrix(y_test,y_pred_knn)
print("Confusion Matrix for KNN:")
print(confusion)
classification_rep = classification_report(y_test, y_pred_knn)
print("Classification Report for KNN:")
print(classification_rep)

"""# Part 5: Conclusion

Upon completing the modeling section, I have been able to make various takeaways from this project.


*   I first noticed that there exists a class imbalance in the data that has led to seeing a relatively high accuracy without identifying actually positive cases, leading therefore to a very low recall. However, once attempting to solve this issue through the usage of SMOTE, it was evident that despite a significant improvement in recall of true positive heart disease diagnoses, there also came a significantly increased number of false positives, thus bringing the accuracy of the models down.
*   Overall, this led me to conclude that working with this dataset proved very challenging to predict disese risk, meaning it may have required more specific features that could directly determine whether one is at risk for heart disese.

In the future, there are various things I'd reconsider when approaching this project.


*   I would first attempt to explore additional features that could enhance the prediction model itself, given the inaccuracies resulting from the current features.
*   Next, I would potentially consider integrating various other external datasets apart from strictly health-related issues, which may include but not be limited to environmental data and socioeconomic indicators of poor cardiovascular health.
*   Finally, I'd consider implementing a time-series analysis of data specifically on the lifestyle factors in order to capture specific trends or other temporal patterns contributing to either a positive or negative test of cardiovascular disease.

Thank you so much for reading through the project!






"""