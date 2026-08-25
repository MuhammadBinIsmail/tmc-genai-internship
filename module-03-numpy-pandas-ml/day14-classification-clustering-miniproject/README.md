# Day 14 · Classification, Clustering & Module 3 Mini-Project

**🎯 Objective:** Cover core classifiers/clustering and ship a mini-project.

## Dataset
Titanic passenger data — predicting survival (binary classification).

## Pipeline
1. **Clean:** dropped unusable columns, imputed missing Age/Embarked, encoded categoricals
2. **EDA:** survival distribution, correlation heatmap
3. **Train:** Logistic Regression, KNN, Decision Tree, Random Forest
4. **Evaluate:** accuracy, precision, recall, F1, confusion matrix
5. **Cluster:** K-Means on Age/Fare (unsupervised)
6. **Writeup:** findings included at the end of the notebook

## Key Result
Best-performing model (by F1 score) identified from the results table in the notebook.
Fare/class emerged as the dominant factor in both the supervised and unsupervised results.

## Files
- `classification_clustering.ipynb` — full end-to-end notebook
