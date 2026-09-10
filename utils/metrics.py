"""Evaluation metrics and model-configuration helpers for Sentinel IDS."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from utils.preprocessing import FEATURE_COLUMNS, TARGET_COLUMN


@dataclass
class EvaluationResult:
    accuracy: float
    precision: float
    recall: float
    f1: float
    confusion: np.ndarray
    true_positive: int
    true_negative: int
    false_positive: int
    false_negative: int


def evaluate_model(model, data: pd.DataFrame) -> EvaluationResult:
    """Evaluate on the same reproducible stratified 20% hold-out used for training."""
    X = data[FEATURE_COLUMNS]
    y = data[TARGET_COLUMN]
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    pred = model.predict(X_test)

    cm = confusion_matrix(y_test, pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    return EvaluationResult(
        accuracy=accuracy_score(y_test, pred),
        precision=precision_score(y_test, pred, zero_division=0),
        recall=recall_score(y_test, pred, zero_division=0),
        f1=f1_score(y_test, pred, zero_division=0),
        confusion=cm,
        true_positive=int(tp),
        true_negative=int(tn),
        false_positive=int(fp),
        false_negative=int(fn),
    )


def model_config(model) -> dict:
    """Extract the real hyperparameters of the trained Random Forest."""
    return {
        "n_estimators": getattr(model, "n_estimators", "n/a"),
        "max_depth": getattr(model, "max_depth", None) or "None (unlimited)",
        "criterion": getattr(model, "criterion", "n/a"),
        "class_weight": getattr(model, "class_weight", None) or "None",
        "random_state": getattr(model, "random_state", "n/a"),
    }
