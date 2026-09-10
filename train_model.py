"""Train the Sentinel IDS Random Forest classifier.

Usage:
    python train_model.py

This preserves the original training approach exactly (same algorithm,
same hyperparameters, same train/test split) and just organizes it around
the shared feature schema in utils/preprocessing.py so the training script,
the app, and the model can never silently drift apart on column order.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

from utils.preprocessing import FEATURE_COLUMNS, TARGET_COLUMN, validate_dataset

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "intrusion_data.csv"
MODEL_PATH = BASE_DIR / "model.pkl"

# Unchanged from the original project.
N_ESTIMATORS = 120
MAX_DEPTH = 12
TEST_SIZE = 0.20
RANDOM_STATE = 42


def main() -> None:
    print("=" * 50)
    print(" SENTINEL IDS — MODEL TRAINING")
    print("=" * 50)

    if not DATA_PATH.exists():
        raise SystemExit(f"ERROR: dataset not found at '{DATA_PATH.name}'.")

    df = pd.read_csv(DATA_PATH)
    problems = validate_dataset(df)
    if problems:
        raise SystemExit("ERROR: dataset failed validation:\n  - " + "\n  - ".join(problems))

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    print(f"\nTraining records : {len(X_train):,}")
    print(f"Testing records  : {len(X_test):,}")
    print(f"Features         : {len(FEATURE_COLUMNS)}")

    model = RandomForestClassifier(
        n_estimators=N_ESTIMATORS,
        max_depth=MAX_DEPTH,
        random_state=RANDOM_STATE,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    pred = model.predict(X_test)
    acc = accuracy_score(y_test, pred)

    print(f"\nTest Accuracy: {acc*100:.2f}%\n")
    print(classification_report(y_test, pred, target_names=["Normal", "Attack"]))

    joblib.dump(model, MODEL_PATH)
    print(f"SUCCESS: model saved to '{MODEL_PATH.name}'.")


if __name__ == "__main__":
    main()
