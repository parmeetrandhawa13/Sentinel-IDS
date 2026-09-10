"""Model loading and inference helpers for Sentinel IDS.

Everything here operates on the real, loaded Random Forest model and the
real demonstration dataset - there is no simulated prediction logic. The
only "demo" aspects of the product are the synthetic dataset itself and the
preset input values on the Live Detection page, both of which are clearly
labelled in the UI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import joblib
import pandas as pd

from utils.preprocessing import FEATURE_COLUMNS, TARGET_COLUMN, validate_dataset


class ArtifactLoadError(Exception):
    """Raised when the model or dataset cannot be loaded or is invalid."""


@dataclass
class Artifacts:
    model: object
    data: pd.DataFrame
    model_path: Path
    data_path: Path


@dataclass
class PredictionResult:
    prediction: int
    label: str
    confidence: float
    prob_normal: float
    prob_attack: float
    risk_level: str
    indicators: list[str] = field(default_factory=list)


def load_artifacts(base_dir: Path) -> Artifacts:
    """Load the trained model and dataset, raising ArtifactLoadError on failure.

    Callers are expected to catch ArtifactLoadError and render a friendly
    in-app message rather than letting Streamlit crash with a traceback.
    """
    model_path = base_dir / "model.pkl"
    data_path = base_dir / "intrusion_data.csv"

    if not model_path.exists():
        raise ArtifactLoadError(
            f"Model file not found at '{model_path.name}'. Run 'python train_model.py' first."
        )
    if not data_path.exists():
        raise ArtifactLoadError(
            f"Dataset file not found at '{data_path.name}'. Restore 'intrusion_data.csv' to the project root."
        )

    try:
        model = joblib.load(model_path)
    except Exception as exc:  # noqa: BLE001 - surfaced to the user, not swallowed
        raise ArtifactLoadError(f"Could not load '{model_path.name}': {exc}") from exc

    try:
        data = pd.read_csv(data_path)
    except Exception as exc:  # noqa: BLE001
        raise ArtifactLoadError(f"Could not read '{data_path.name}': {exc}") from exc

    problems = validate_dataset(data)
    if problems:
        raise ArtifactLoadError("Dataset validation failed: " + " ".join(problems))

    if not hasattr(model, "predict_proba"):
        raise ArtifactLoadError("The loaded model does not support probability predictions.")

    return Artifacts(model=model, data=data, model_path=model_path, data_path=data_path)


def compute_feature_baseline(data: pd.DataFrame) -> pd.DataFrame:
    """Per-class (normal vs attack) mean/std for each feature.

    Used only to decide which threat indicators are actually supported by a
    given input record - never to fabricate findings the model didn't make.
    """
    return data.groupby(TARGET_COLUMN)[FEATURE_COLUMNS].agg(["mean", "std"])


def _elevated(value: float, normal_mean: float, normal_std: float, z: float = 1.5) -> bool:
    """True if value sits meaningfully above the normal-class distribution."""
    if pd.isna(normal_std) or normal_std == 0:
        return value > normal_mean * 1.5 if normal_mean > 0 else value > 0
    return value > normal_mean + z * normal_std


def derive_indicators(row: pd.DataFrame, baseline: pd.DataFrame) -> list[str]:
    """Return only the indicators actually supported by this input record.

    Each check compares the submitted feature values against the normal-class
    distribution observed in the training data. Nothing is asserted about a
    specific attack type - the model classifies traffic as normal/intrusion
    only, so indicators stay descriptive, not diagnostic.
    """
    indicators = []
    r = row.iloc[0]
    normal_mean = baseline.loc[0] if 0 in baseline.index else None
    if normal_mean is None:
        return indicators

    if _elevated(r["packets"], normal_mean[("packets", "mean")], normal_mean[("packets", "std")]):
        indicators.append("Packet count is well above typical normal-traffic volume.")

    if _elevated(r["src_bytes"], normal_mean[("src_bytes", "mean")], normal_mean[("src_bytes", "std")]):
        indicators.append("Source byte volume is unusually high for a single connection.")

    dst_mean = normal_mean[("dst_bytes", "mean")]
    if r["dst_bytes"] < max(dst_mean * 0.1, 0) and r["src_bytes"] > normal_mean[("src_bytes", "mean")]:
        indicators.append("Highly asymmetric byte distribution between source and destination.")

    if r["failed_logins"] >= 3:
        indicators.append("Multiple failed login attempts observed on this connection.")

    if r["duration"] <= 0.5 and r["packets"] > normal_mean[("packets", "mean")]:
        indicators.append("High packet volume delivered in a very short connection duration.")

    return indicators


def predict(model, baseline: pd.DataFrame, row: pd.DataFrame) -> PredictionResult:
    """Run the real model on a single input row and package the result."""
    pred = int(model.predict(row)[0])
    probs = model.predict_proba(row)[0]
    prob_normal, prob_attack = float(probs[0]), float(probs[1])
    confidence = prob_attack if pred == 1 else prob_normal

    if pred == 1:
        risk = "HIGH" if confidence >= 0.85 else "MEDIUM" if confidence >= 0.6 else "LOW"
    else:
        risk = "NONE"

    indicators = derive_indicators(row, baseline) if pred == 1 else []

    return PredictionResult(
        prediction=pred,
        label="INTRUSION DETECTED" if pred == 1 else "NORMAL TRAFFIC",
        confidence=confidence,
        prob_normal=prob_normal,
        prob_attack=prob_attack,
        risk_level=risk,
        indicators=indicators,
    )


def tree_votes(model, row: pd.DataFrame, limit: int = 12) -> list[int]:
    """Individual tree predictions for one row, used by the Algorithm page.

    Returns real per-estimator predictions from the loaded Random Forest -
    this is not a scripted or fabricated visualization.
    """
    values = row.to_numpy()
    votes = [int(tree.predict(values)[0]) for tree in model.estimators_[:limit]]
    return votes
