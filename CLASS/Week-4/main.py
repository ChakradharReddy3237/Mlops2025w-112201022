# Filename: ml_uv_visual.py

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import load_wine, load_breast_cancer, load_diabetes
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_squared_error, classification_report, confusion_matrix
import pandas as pd

# Enable nicer plots
sns.set(style="whitegrid")

datasets = {
    "Wine": load_wine(),
    "Breast Cancer": load_breast_cancer(),
    "Diabetes": load_diabetes()
}

for name, dataset in datasets.items():
    print(f"\n===== Dataset: {name} =====")
    X, y = dataset.data, dataset.target
    feature_names = dataset.feature_names
    if hasattr(dataset, 'target_names'):
        target_names = dataset.target_names
    else:
        target_names = None

    # Create dataframe for visualization
    df = pd.DataFrame(X, columns=feature_names)
    if target_names is not None:
        df['target'] = [target_names[i] for i in y]
    else:
        df['target'] = y

    # 1️⃣ Pairplot for first 4 features
    sns.pairplot(df.iloc[:, :5].assign(target=df['target']), hue='target', diag_kind='kde')
    plt.suptitle(f"{name} Dataset Pairplot", y=1.02)
    plt.show()

    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Standardize
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Model selection
    if name in ["Wine", "Breast Cancer"]:
        model = RandomForestClassifier(n_estimators=100, random_state=42)
    else:
        model = RandomForestRegressor(n_estimators=100, random_state=42)

    # Train
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)

    # 2️⃣ Evaluation plots
    if name in ["Wine", "Breast Cancer"]:
        acc = accuracy_score(y_test, y_pred)
        print(f"Accuracy: {acc:.2f}")
        print(classification_report(y_test, y_pred, target_names=target_names))

        # Confusion Matrix Heatmap
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(6,5))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=target_names, yticklabels=target_names)
        plt.title(f"{name} Confusion Matrix")
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        plt.show()
    else:
        mse = mean_squared_error(y_test, y_pred)
        print(f"Mean Squared Error: {mse:.2f}")
        # Scatter predicted vs actual
        plt.scatter(y_test, y_pred, alpha=0.7)
        plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
        plt.xlabel("Actual")
        plt.ylabel("Predicted")
        plt.title(f"{name} Regression: Actual vs Predicted")
        plt.show()

    # 3️⃣ Feature Importance for tree models
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        plt.figure(figsize=(8,5))
        sns.barplot(x=importances, y=feature_names)
        plt.title(f"{name} Feature Importances")
        plt.xlabel("Importance")
        plt.ylabel("Feature")
        plt.show()

    # 4️⃣ Cross-validation scores
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
    plt.figure(figsize=(6,3))
    sns.barplot(x=list(range(1,6)), y=cv_scores)
    plt.title(f"{name} 5-Fold CV Scores")
    plt.xlabel("Fold")
    plt.ylabel("Score")
    plt.ylim(0,1)
    plt.show()

    # 5️⃣ Sample prediction visualization
    sample = X_test_scaled[:5]
    pred = model.predict(sample)
    print(f"Sample predictions: {pred}, True labels: {y_test[:5]}")
