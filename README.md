<p align="center">
  <img src="assets/logo.svg" width="80" alt="Sentinel IDS logo"/>
</p>

<h1 align="center">Sentinel IDS</h1>
<p align="center"><b>AI-Powered Network Intrusion Detection</b><br/>
Data Security Lab — Practical No. 10</p>

---

## Overview

**Sentinel IDS** is a Machine Learning–based Intrusion Detection System built with **Python**, **scikit-learn**, and **Streamlit**, presented as a Security Operations Center (SOC)–style dashboard. It classifies network traffic records as **Normal** or **Intrusion** using a trained **Random Forest Classifier**.

This is a classroom / laboratory demonstration project. It is designed to clearly explain and visualize how an ML-based IDS works, not to replace a production security monitoring system.

## Problem Statement

*"To develop an Intrusion Detection System using Machine Learning Algorithms."*

## Objective

Build a system that ingests traffic-flow features (duration, protocol, byte counts, packet counts, ports, failed logins) and predicts whether the traffic is normal or a potential intrusion, while making the underlying ML reasoning visible and explainable for a lab viva or technical demonstration.

## Features

- **SOC-style dashboard** — KPI cards, threat distribution, and a detection pipeline visualization
- **Live Detection console** — manual traffic input or one-click Normal/Attack demo presets, analyzed by the real trained model
- **Evidence-based threat indicators** — flags are derived from how far the input deviates from the normal-traffic distribution in the training data, not fabricated
- **Model Performance page** — accuracy, precision, recall, F1, confusion matrix, and TP/TN/FP/FN breakdown computed from the actual model
- **Algorithm explainer** — visual walkthrough of Random Forest and majority voting, including a *live* per-tree vote demo run on the real loaded model
- **Dataset page** — dataset composition, feature list, and plain-language feature descriptions
- **Presentation Mode** — collapses navigation to a short Problem → Algorithm → Live Detection → Performance flow for demos
- Graceful error handling for missing/invalid model or dataset files

## Machine Learning Algorithm

- **Algorithm:** Random Forest Classifier (`scikit-learn`)
- **Estimators:** 120 trees
- **Max depth:** 12
- **Class weighting:** balanced
- **Train/test split:** 80% / 20%, stratified by label

The algorithm, its hyperparameters, and the prediction logic are unchanged from the original practical — this upgrade is a UI/architecture redesign, not a model change.

## System Architecture

```
Network Traffic → Feature Extraction → Data Preprocessing → Random Forest → Majority Voting → Threat Classification
```

See `assets/architecture.svg` for the diagram used in the app.

## Dataset

`intrusion_data.csv` — a **synthetic classroom dataset** of 3,000 labeled traffic records.

> **DEMO DATASET — NOT REAL-TIME NETWORK TRAFFIC.**
> This dataset does not represent captured real-world attack traffic and should not be used to draw conclusions about real-world attack prevalence.

## Features Used

| Feature | Description |
|---|---|
| `duration` | Length of the connection/session, in seconds |
| `protocol` | Transport/network protocol (TCP, UDP, ICMP) |
| `src_bytes` | Bytes sent from source to destination |
| `dst_bytes` | Bytes sent from destination back to source |
| `packets` | Total packets exchanged during the connection |
| `src_port` | Originating port on the source host |
| `dst_port` | Target port on the destination host |
| `failed_logins` | Count of failed authentication attempts on the connection |

## Installation

```bash
git clone <your-repo-url>
cd sentinel-ids
pip install -r requirements.txt
```

## Running the Application

```bash
# 1. Train the model (creates model.pkl)
python train_model.py

# 2. Launch the app
python -m streamlit run app.py
```

Open the local URL Streamlit prints in the terminal (normally `http://localhost:8501`).

## Project Structure

```
sentinel-ids/
│
├── app.py                  # Streamlit application (SOC dashboard, all pages)
├── train_model.py          # Random Forest training script
├── intrusion_data.csv      # Synthetic demonstration dataset
├── model.pkl               # Trained model artifact (generated)
├── requirements.txt
├── README.md
│
├── utils/
│   ├── __init__.py
│   ├── preprocessing.py    # Feature schema, encodings, demo presets
│   ├── prediction.py       # Model loading, inference, risk & indicator logic
│   ├── metrics.py          # Evaluation metrics, model configuration
│   └── ui.py                # Shared CSS theme and HTML rendering helpers
│
└── assets/
    ├── logo.svg
    └── architecture.svg
```

## Screenshots

*Add screenshots of the Dashboard, Live Detection, and Model Performance pages here before submitting.*

## Team Members

- Member 1
- Member 2
- Member 3

*(Replace with actual names before submission.)*

## Limitations

This project is an educational demonstration using a synthetic dataset. It does not perform actual packet capture or production-grade network monitoring. Reported metrics reflect performance on the included synthetic dataset only and should not be interpreted as real-world detection accuracy. The system does not identify a specific attack type — it distinguishes normal traffic from potential intrusions only.

## Future Scope

- Live packet capture (e.g., via `scapy` or `pyshark`)
- Real-time network traffic monitoring
- SIEM integration
- Multi-class attack-type classification
- Automated alerting (email/Slack/webhook)
- Historical log analysis and reporting
- Deployment on cloud infrastructure with authentication
