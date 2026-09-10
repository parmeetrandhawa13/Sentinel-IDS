"""Feature schema and preprocessing helpers for Sentinel IDS.

This module is the single source of truth for the model's input schema so
that training, inference, and the UI never drift apart. The feature set and
protocol encoding match the original project exactly - nothing about the
underlying data contract has changed.
"""

from __future__ import annotations

import pandas as pd

# Ordered list of feature columns the model was trained on.
FEATURE_COLUMNS = [
    "duration",
    "protocol",
    "src_bytes",
    "dst_bytes",
    "packets",
    "src_port",
    "dst_port",
    "failed_logins",
]

TARGET_COLUMN = "label"

# Protocol categorical encoding (unchanged from the original project).
PROTOCOL_MAP = {"TCP": 0, "UDP": 1, "ICMP": 2}
PROTOCOL_OPTIONS = list(PROTOCOL_MAP.keys())

# Human-readable descriptions shown on the Dataset page.
FEATURE_DESCRIPTIONS = {
    "duration": "Length of the connection/session, in seconds.",
    "protocol": "Transport/network protocol used by the traffic (TCP, UDP, or ICMP).",
    "src_bytes": "Number of bytes sent from the source host to the destination.",
    "dst_bytes": "Number of bytes sent from the destination host back to the source.",
    "packets": "Total number of packets exchanged during the connection.",
    "src_port": "Originating port number on the source host.",
    "dst_port": "Target port number on the destination host.",
    "failed_logins": "Count of failed authentication attempts observed on the connection.",
}

# Demo presets used by the Live Detection page. These populate the input
# form with realistic, hand-picked values - they do not come from live
# network capture.
DEMO_PRESETS = {
    "Normal Traffic": {
        "duration": 10.0,
        "protocol": "TCP",
        "src_bytes": 1200,
        "dst_bytes": 4500,
        "packets": 25,
        "src_port": 443,
        "dst_port": 80,
        "failed_logins": 0,
    },
    "Attack Traffic": {
        "duration": 0.0,
        "protocol": "ICMP",
        "src_bytes": 50000,
        "dst_bytes": 100,
        "packets": 500,
        "src_port": 12345,
        "dst_port": 445,
        "failed_logins": 8,
    },
}

DEFAULT_INPUT = DEMO_PRESETS["Normal Traffic"]


def build_input_row(
    duration: float,
    protocol: str,
    src_bytes: int,
    dst_bytes: int,
    packets: int,
    src_port: int,
    dst_port: int,
    failed_logins: int,
) -> pd.DataFrame:
    """Build a single-row, model-ready DataFrame from raw form values."""
    row = {
        "duration": duration,
        "protocol": PROTOCOL_MAP[protocol],
        "src_bytes": src_bytes,
        "dst_bytes": dst_bytes,
        "packets": packets,
        "src_port": src_port,
        "dst_port": dst_port,
        "failed_logins": failed_logins,
    }
    return pd.DataFrame([row], columns=FEATURE_COLUMNS)


def validate_dataset(df: pd.DataFrame) -> list[str]:
    """Return a list of human-readable problems found in a dataset.

    An empty list means the dataset looks structurally valid.
    """
    problems = []
    if df is None or df.empty:
        problems.append("The dataset is empty.")
        return problems

    missing = [c for c in FEATURE_COLUMNS + [TARGET_COLUMN] if c not in df.columns]
    if missing:
        problems.append(f"Missing required column(s): {', '.join(missing)}.")

    if TARGET_COLUMN in df.columns:
        labels = set(pd.unique(df[TARGET_COLUMN].dropna()))
        if not labels.issubset({0, 1}):
            problems.append("The label column must only contain 0 (normal) or 1 (intrusion).")

    return problems
