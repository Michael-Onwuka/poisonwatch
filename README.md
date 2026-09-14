# PoisonWatch  Data Poisoning Detection for Network Intrusion Detection Systems

Final Year BSc Dissertation Project | Middlesex University

PoisonWatch is an end-to-end pipeline for detecting **label-flipping data poisoning attacks** against machine learning-based Network Intrusion Detection Systems (NIDS). It simulates poisoning attacks on a baseline classifier, then uses an unsupervised anomaly detector to catch the poisoned samples  all wrapped in a Flask dashboard so non-technical users can run the analysis and read the results.

## Why This Matters

ML-based intrusion detection systems are only as trustworthy as the data they're trained on. An attacker who can flip a small percentage of training labels (e.g. relabeling malicious traffic as benign) can quietly degrade a model's ability to catch real attacks  without ever touching the model itself. This project measures how much damage that does, and builds a detector to catch it before it happens.

## How It Works

1. **Upload & preprocessing**  A user uploads a CSV (e.g. a UNSW-NB15 export). All columns are label-encoded and scaled to prepare the feature matrix.
2. **Anomaly detection**  An Isolation Forest flags suspicious/anomalous rows in the uploaded data, using a user-adjustable contamination estimate (the expected proportion of anomalous samples).
3. **Baseline classifier**  A Random Forest classifier is trained on a held-out split of the data to report a baseline accuracy score for the dataset as provided.
4. **Visualization**  A bar chart contrasts clean vs. flagged samples for quick interpretation.
5. **Dashboard**  All of the above runs through a Flask web app, so a non-technical user can upload a file, set parameters, and get results without touching code.

*Note: this is an unsupervised anomaly-flagging prototype  it does not simulate label-flipping attacks or score itself against known-poisoned ground truth, so it reports flagged-sample counts and baseline accuracy rather than precision/recall metrics.*

## Example Run

| Metric | Value |
|---|---|
| Dataset rows | 175,341 |
| Features used | 42 |
| Suspicious samples flagged (10% contamination) | 17,534 |
| Baseline model accuracy | 95.83% |

*(Run against the UNSW-NB15 training set. `attack_cat` and `id` are excluded from the feature set  `attack_cat` near-perfectly determines the label and would otherwise cause data leakage.)*

## Tech Stack

- **Language:** Python
- **ML / Data:** scikit-learn, pandas
- **Web app:** Flask
- **Dataset:** UNSW-NB15

## Dataset

This project uses the [UNSW-NB15 dataset](https://research.unsw.edu.au/projects/unsw-nb15-dataset), which is **not included in this repository** due to licensing restrictions on redistribution. To run the pipeline:

1. Download the dataset directly from the official source above
2. Place it in a local `data/` folder in the project root
3. The `data/` folder is excluded via `.gitignore` and will not be tracked by Git

## Setup & Usage

```bash
# Clone the repo
git clone https://github.com/[yourname]/poisonwatch.git
cd poisonwatch

# Install dependencies
pip install flask pandas numpy scikit-learn matplotlib

# Run the dashboard
python poisoning_detector_v2.py
```

Then open `http://127.0.0.1:5000` in your browser.

**Using the dashboard:**
1. Prepare a CSV version of your dataset (e.g. a UNSW-NB15 export)
2. Upload the CSV under "CSV upload"
3. Enter the target label column name (e.g. `label`)
4. Set a contamination estimate (e.g. `0.10` for 10%)
5. Click **Run poisoning analysis** to view dataset rows, feature count, suspicious samples flagged, baseline model accuracy, and a results chart

## Key Takeaways

- Unsupervised anomaly detection (Isolation Forest) can flag suspicious training samples in network traffic data without needing pre-labeled examples of poisoning.
- Pairing this with a baseline supervised classifier gives a quick, interpretable picture of both data quality and model performance side by side.
- This tool is a proof-of-concept  flagged samples indicate rows worth further investigation, not a definitive poisoning verdict.

## Future Work

- Add ground-truth poisoning simulation (controlled label-flipping at known contamination levels) so detection performance can be scored with precision/recall/F1 against a known answer
- Extend detection to other poisoning strategies beyond label-flipping (e.g. feature-space poisoning)
- Test against additional NIDS datasets (e.g. CICIDS2017) to check generalization

## Author

Ugochukwu Michael Onwuka · michaelonwuka224@gmail.com
