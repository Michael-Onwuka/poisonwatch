from flask import Flask, render_template_string, request
import os
import io
import base64
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PoisonWatch Dashboard</title>
    <style>
        :root{
            --bg:#0f172a;
            --panel:#111827;
            --panel-2:#1f2937;
            --card:#111827;
            --muted:#94a3b8;
            --text:#f8fafc;
            --line:rgba(255,255,255,0.08);
            --accent:#14b8a6;
            --accent-2:#0ea5e9;
            --danger:#f43f5e;
            --warn:#f59e0b;
            --ok:#22c55e;
            --radius:18px;
            --shadow:0 10px 30px rgba(0,0,0,0.25);
        }

        *{box-sizing:border-box}
        body{
            margin:0;
            font-family:Inter,Segoe UI,Arial,sans-serif;
            background:linear-gradient(180deg,#0b1220 0%, #111827 100%);
            color:var(--text);
        }

        .app{
            display:grid;
            grid-template-columns:260px 1fr;
            min-height:100vh;
        }

        .sidebar{
            background:rgba(15,23,42,0.95);
            border-right:1px solid var(--line);
            padding:24px;
        }

        .brand{
            display:flex;
            align-items:center;
            gap:12px;
            margin-bottom:32px;
        }

        .logo{
            width:42px;
            height:42px;
            border-radius:12px;
            background:linear-gradient(135deg,var(--accent),var(--accent-2));
            display:flex;
            align-items:center;
            justify-content:center;
            font-weight:800;
            color:white;
            box-shadow:var(--shadow);
        }

        .brand h1{
            margin:0;
            font-size:18px;
        }

        .brand p{
            margin:2px 0 0;
            color:var(--muted);
            font-size:12px;
        }

        .nav-title{
            font-size:12px;
            text-transform:uppercase;
            letter-spacing:0.12em;
            color:var(--muted);
            margin:18px 0 10px;
        }

        .nav-item{
            padding:12px 14px;
            border-radius:12px;
            margin-bottom:8px;
            background:rgba(255,255,255,0.03);
            color:#dbeafe;
            font-size:14px;
        }

        .main{
            padding:28px;
        }

        .topbar{
            display:flex;
            justify-content:space-between;
            align-items:flex-start;
            gap:20px;
            margin-bottom:24px;
            flex-wrap:wrap;
        }

        .hero h2{
            margin:0 0 8px;
            font-size:30px;
            line-height:1.1;
        }

        .hero p{
            margin:0;
            color:var(--muted);
            max-width:760px;
        }

        .badge{
            background:rgba(20,184,166,0.12);
            color:#99f6e4;
            border:1px solid rgba(20,184,166,0.25);
            padding:10px 14px;
            border-radius:999px;
            font-size:13px;
            white-space:nowrap;
        }

        .grid{
            display:grid;
            grid-template-columns:repeat(4,1fr);
            gap:18px;
            margin-bottom:22px;
        }

        .card{
            background:rgba(17,24,39,0.88);
            border:1px solid var(--line);
            border-radius:var(--radius);
            padding:18px;
            box-shadow:var(--shadow);
        }

        .kpi-label{
            color:var(--muted);
            font-size:13px;
            margin-bottom:10px;
        }

        .kpi-value{
            font-size:28px;
            font-weight:800;
        }

        .kpi-sub{
            margin-top:8px;
            font-size:13px;
            color:#cbd5e1;
        }

        .content{
            display:grid;
            grid-template-columns:1.05fr 0.95fr;
            gap:20px;
        }

        .panel-title{
            margin:0 0 8px;
            font-size:18px;
        }

        .panel-sub{
            margin:0 0 18px;
            color:var(--muted);
            font-size:14px;
        }

        .upload-box{
            border:1.5px dashed rgba(148,163,184,0.35);
            border-radius:16px;
            padding:18px;
            background:rgba(255,255,255,0.02);
            margin-bottom:16px;
        }

        input[type=file]{
            width:100%;
            margin-top:10px;
            color:var(--muted);
        }

        .controls{
            display:grid;
            grid-template-columns:1fr 1fr;
            gap:14px;
            margin:16px 0;
        }

        .field label{
            display:block;
            font-size:13px;
            color:var(--muted);
            margin-bottom:8px;
        }

        .field input, .field select{
            width:100%;
            background:#0b1220;
            color:var(--text);
            border:1px solid var(--line);
            border-radius:12px;
            padding:12px 14px;
            outline:none;
        }

        .btn{
            border:none;
            border-radius:14px;
            padding:14px 18px;
            font-weight:700;
            cursor:pointer;
            width:100%;
        }

        .btn-primary{
            background:linear-gradient(135deg,var(--accent),var(--accent-2));
            color:white;
        }

        .btn-secondary{
            background:rgba(255,255,255,0.04);
            color:var(--text);
            border:1px solid var(--line);
        }

        .results-list{
            display:grid;
            gap:12px;
        }

        .result-row{
            display:flex;
            justify-content:space-between;
            gap:12px;
            padding:14px 16px;
            border-radius:14px;
            background:rgba(255,255,255,0.03);
            border:1px solid var(--line);
        }

        .result-row span:first-child{
            color:var(--muted);
        }

        .plot{
            margin-top:18px;
            background:white;
            border-radius:16px;
            padding:10px;
        }

        .info-list{
            display:grid;
            gap:12px;
            margin-top:16px;
        }

        .info-item{
            padding:14px;
            border-radius:14px;
            background:rgba(255,255,255,0.03);
            border:1px solid var(--line);
            color:#dbeafe;
            font-size:14px;
            line-height:1.5;
        }

        .status-good{color:#86efac}
        .status-warn{color:#fcd34d}
        .status-bad{color:#fda4af}

        @media (max-width: 1100px){
            .grid{grid-template-columns:repeat(2,1fr)}
            .content{grid-template-columns:1fr}
        }

        @media (max-width: 760px){
            .app{grid-template-columns:1fr}
            .sidebar{display:none}
            .main{padding:18px}
            .grid{grid-template-columns:1fr}
            .controls{grid-template-columns:1fr}
            .hero h2{font-size:24px}
        }
    </style>
</head>
<body>
<div class="app">
    <aside class="sidebar">
        <div class="brand">
            <div class="logo">PW</div>
            <div>
                <h1>PoisonWatch</h1>
                <p>Training Data Integrity Dashboard</p>
            </div>
        </div>

        <div class="nav-title">Workspace</div>
        <div class="nav-item">Overview</div>
        <div class="nav-item">Detection Run</div>
        <div class="nav-item">Visual Results</div>

        <div class="nav-title">Project fit</div>
        <div class="nav-item">Flask prototype</div>
        <div class="nav-item">Basic visualisation</div>
        <div class="nav-item">User instructions</div>
    </aside>

    <main class="main">
        <div class="topbar">
            <div class="hero">
                <h2>Detect label-flipping poisoning faster.</h2>
                <p>Upload a Prepared CSV Dataset, Run A Lightweight Anomaly Check, Review Simple Metrics & Charts For A Prototype Designed To Detect Data Poisoning Attacks In Machine Learning-Based Intrusion Detection Systems.</p>
            </div>
            <div class="badge">PoisonWatch Dashboard</div>
        </div>

        <div class="grid">
            <div class="card">
                <div class="kpi-label">Dataset rows</div>
                <div class="kpi-value">{{ rows if rows is not none else "--" }}</div>
                <div class="kpi-sub">Loaded from uploaded CSV</div>
            </div>
            <div class="card">
                <div class="kpi-label">Features used</div>
                <div class="kpi-value">{{ features if features is not none else "--" }}</div>
                <div class="kpi-sub">Numeric columns after encoding</div>
            </div>
            <div class="card">
                <div class="kpi-label">Suspicious samples</div>
                <div class="kpi-value">{{ suspicious if suspicious is not none else "--" }}</div>
                <div class="kpi-sub">Flagged by detector</div>
            </div>
            <div class="card">
                <div class="kpi-label">Model accuracy</div>
                <div class="kpi-value">{{ accuracy if accuracy is not none else "--" }}</div>
                <div class="kpi-sub">Baseline quick check</div>
            </div>
        </div>

        <div class="content">
            <section class="card">
                <h3 class="panel-title">Run detection</h3>
                <p class="panel-sub">Upload your CSV file and choose the target label column to test the dataset.</p>

                <form method="POST" enctype="multipart/form-data">
                    <div class="upload-box">
                        <strong>CSV upload</strong>
                        <div style="color:var(--muted); font-size:14px; margin-top:6px;">
                            Use a cleaned tabular dataset such as UNSW-NB15 export in CSV format.
                        </div>
                        <input type="file" name="file" accept=".csv" required>
                    </div>

                    <div class="controls">
                        <div class="field">
                            <label>Target label column</label>
                            <input type="text" name="label_col" placeholder="e.g. label" required>
                        </div>
                        <div class="field">
                            <label>Contamination estimate</label>
                            <input type="number" step="0.01" min="0.01" max="0.49" name="contamination" value="0.10" required>
                        </div>
                    </div>

                    <button class="btn btn-primary" type="submit">Run poisoning analysis</button>
                </form>
            </section>

            <section class="card">
                <h3 class="panel-title">How to use it</h3>
                <p class="panel-sub">Keep the workflow simple and explainable for your report demonstration.</p>

                <div class="info-list">
                    <div class="info-item"><strong>Step 1:</strong> Prepare a CSV version of the dataset.</div>
                    <div class="info-item"><strong>Step 2:</strong> Enter the class label column name, for example <code>label</code>.</div>
                    <div class="info-item"><strong>Step 3:</strong> Run the detector and review suspicious sample counts and accuracy.</div>
                    <div class="info-item"><strong>Step 4:</strong> Use screenshots of this dashboard and chart in your Work Done and Findings sections.</div>
                </div>
            </section>
        </div>

        {% if results %}
        <div style="height:20px"></div>
        <div class="content">
            <section class="card">
                <h3 class="panel-title">Detection results</h3>
                <p class="panel-sub">A simple overview of the dataset and anomaly screening outcome.</p>

                <div class="results-list">
                    <div class="result-row"><span>Total rows</span><strong>{{ results.total_rows }}</strong></div>
                    <div class="result-row"><span>Total features</span><strong>{{ results.total_features }}</strong></div>
                    <div class="result-row"><span>Suspicious rows flagged</span><strong class="status-warn">{{ results.suspicious_rows }}</strong></div>
                    <div class="result-row"><span>Flag rate</span><strong>{{ results.flag_rate }}</strong></div>
                    <div class="result-row"><span>Baseline model accuracy</span><strong class="status-good">{{ results.model_accuracy }}</strong></div>
                </div>
            </section>

            <section class="card">
                <h3 class="panel-title">Interpretation</h3>
                <p class="panel-sub">Use this wording for a simple academic demonstration.</p>

                <div class="info-list">
                    <div class="info-item">The model provides an initial indication of unusual training samples using anomaly detection.</div>
                    <div class="info-item">A higher suspicious count may suggest potential poisoning or noisy records, but flagged points still require further validation.</div>
                    <div class="info-item">This prototype is suitable as a proof-of-concept tool rather than a final production security platform.</div>
                </div>
            </section>
        </div>

        {% if plot_url %}
        <section class="card" style="margin-top:20px;">
            <h3 class="panel-title">Visual output</h3>
            <p class="panel-sub">Simple chart for screenshots and report evidence.</p>
            <div class="plot">
                <img src="data:image/png;base64,{{ plot_url }}" alt="Detection results chart" style="width:100%; border-radius:12px;">
            </div>
        </section>
        {% endif %}
        {% endif %}
    </main>
</div>
</body>
</html>
"""

def make_plot(total_rows, suspicious_rows):
    clean_rows = total_rows - suspicious_rows
    labels = ["Clean / Remaining", "Suspicious"]
    values = [clean_rows, suspicious_rows]
    colors = ["#14b8a6", "#f43f5e"]

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(labels, values, color=colors, width=0.55)
    ax.set_title("Poisoning Detection Overview")
    ax.set_ylabel("Number of Samples")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + max(values)*0.02, f"{int(height)}",
                ha='center', va='bottom', fontsize=10)

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

@app.route("/", methods=["GET", "POST"])
def home():
    context = {
        "results": None,
        "plot_url": None,
        "rows": None,
        "features": None,
        "suspicious": None,
        "accuracy": None
    }

    if request.method == "POST":
        file = request.files.get("file")
        label_col = request.form.get("label_col", "").strip()
        contamination = float(request.form.get("contamination", 0.10))

        if file and label_col:
            df = pd.read_csv(file)
            df = df.drop(columns=[c for c in ["attack_cat", "id"] if c in df.columns])

            if label_col not in df.columns:
                return f"Column '{label_col}' not found in dataset."

            data = df.copy()

            for col in data.columns:    
                data[col] = data[col].astype(str) if data[col].dtype == "object" else data[col]
                data[col] = LabelEncoder().fit_transform(data[col].astype(str))

            X = data.drop(columns=[label_col])
            y = data[label_col]

            X = pd.get_dummies(X)
            y = LabelEncoder().fit_transform(y.astype(str))
            X = X.fillna(0)

            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            detector = IsolationForest(contamination=contamination, random_state=42)
            preds = detector.fit_predict(X_scaled)
            suspicious_rows = int((preds == -1).sum())

            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )

            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            acc = accuracy_score(y_test, y_pred)

            plot_url = make_plot(len(df), suspicious_rows)

            context["results"] = {
                "total_rows": len(df),
                "total_features": X.shape[1],
                "suspicious_rows": suspicious_rows,
                "flag_rate": f"{(suspicious_rows / len(df)) * 100:.2f}%",
                "model_accuracy": f"{acc * 100:.2f}%"
            }
            context["plot_url"] = plot_url
            context["rows"] = len(df)
            context["features"] = X.shape[1]
            context["suspicious"] = suspicious_rows
            context["accuracy"] = f"{acc * 100:.1f}%"

    return render_template_string(HTML, **context)

if __name__ == "__main__":
    app.run(debug=True) 