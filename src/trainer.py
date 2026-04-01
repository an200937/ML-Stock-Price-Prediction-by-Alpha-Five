# TASK 3 — MODEL TRAINER
# 3 models only: Linear Regression, Decision Tree, Random Forest
# Strong regularization settings to prevent overfitting on stock data.

import numpy as np
import pandas as pd
from sklearn.linear_model  import LinearRegression
from sklearn.tree          import DecisionTreeRegressor
from sklearn.ensemble      import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.impute        import SimpleImputer
from sklearn.metrics       import mean_squared_error, mean_absolute_error, r2_score


# ── 3 models with ANTI-OVERFITTING settings ────────────────────────────────
MODELS = {
    "Linear Regression": LinearRegression(),

    # max_depth=5 prevents memorising training data
    "Decision Tree": DecisionTreeRegressor(
        max_depth=5,
        min_samples_leaf=10,   # each leaf needs at least 10 points
        random_state=42
    ),

    # Many shallow trees — more robust than one deep tree
    "Random Forest": RandomForestRegressor(
        n_estimators=100,
        max_depth=6,           # shallow trees = less overfitting
        min_samples_leaf=8,
        max_features=0.6,      # only see 60% of features per split
        n_jobs=-1,
        random_state=42
    ),
}


def preprocess(X_train_df: pd.DataFrame, X_test_df: pd.DataFrame):
    """
    Fill missing values (median) → Scale to zero-mean unit-variance.
    Fit ONLY on train data, apply to both.
    """
    imputer = SimpleImputer(strategy="median")
    scaler  = StandardScaler()

    X_tr = scaler.fit_transform(imputer.fit_transform(X_train_df))
    X_te = scaler.transform(imputer.transform(X_test_df))

    return X_tr, X_te, imputer, scaler


def train_all(X_train, y_train, X_test, y_test):
    """
    Trains all 3 models and returns:
      performance     → DataFrame with RMSE, MAE, R²
      trained_models  → dict of fitted models
      test_preds      → dict of predictions on test set
    """
    rows, trained, test_preds = [], {}, {}

    for name, model in MODELS.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        mae  = float(mean_absolute_error(y_test, y_pred))
        r2   = float(r2_score(y_test, y_pred))

        rows.append({"Model": name, "RMSE": rmse, "MAE": mae, "R²": r2})
        trained[name]     = model
        test_preds[name]  = y_pred.tolist()

    perf = (pd.DataFrame(rows).set_index("Model").sort_values("RMSE"))
    return perf, trained, test_preds
