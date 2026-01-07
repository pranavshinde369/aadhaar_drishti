# 🇮🇳 Aadhaar Drishti: Predictive Intelligence for Inclusive Governance

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn)
![Status](https://img.shields.io/badge/Status-Prototype%20Ready-success?style=for-the-badge)

> **"Data should not just look back; it must look forward."**
> A multi-horizon time-series intelligence platform that transforms Aadhaar enrollment logs into actionable governance decisions, preventing fraud while ensuring inclusion.

---

## 📑 Table of Contents
1. [🚨 Problem Statement](#-problem-statement)
2. [🏗 System Architecture](#-system-architecture)
3. [🧠 The Logic Engines (Deep Dive)](#-the-logic-engines-deep-dive)
4. [💡 The "Secret Sauce": Cross-Engine Context](#-the-secret-sauce-cross-engine-context)
5. [⚙️ Tech Stack](#-tech-stack)
6. [🚀 Installation & Setup](#-installation--setup)
7. [📂 Directory Structure](#-directory-structure)

---

## 🚨 Problem Statement

The current Aadhaar ecosystem operates on a **Reactive Model**:
* **Fraud Detection is Rigid:** Rule-based systems flag *any* high-volume center as "suspicious," often punishing honest operators in high-migration zones.
* **Infrastructure Mismatch:** Enrollment kits are deployed statically, failing to catch up with rapid urbanization ("Boom Towns"), causing long queues.
* **Silent Exclusion:** Aging populations in rural areas ("Ghost Villages") suffer from biometric failure but cannot travel to update centers, leading to service denial.

**Aadhaar Drishti** solves this by moving to a **Predictive Model**, using historical data to forecast stress, validate migration, and automate service delivery.

---

## 🏗 System Architecture

The system processes data through a **Multi-Horizon Pipeline**, analyzing the same dataset through three different time lenses:

| Component | Time Horizon | Goal | Logic Model |
| :--- | :--- | :--- | :--- |
| **Integrity Shield** | Short-Term (30 Days) | Detect Anomalies | Isolation Forest (Unsupervised) |
| **Migration Tracker** | Mid-Term (180 Days) | Trend Analysis | Velocity & Moving Averages |
| **Demographic Scanner** | Long-Term (3 Years) | Pattern Recognition | Correlation Analysis |

---

## 🧠 The Logic Engines (Deep Dive)

### 1. 🛡️ Engine A: Integrity Shield (Context-Aware Fraud)
Instead of simple threshold rules (e.g., "If > 50 enrollments, flag fraud"), we use **Unsupervised Machine Learning**.

* **Algorithm:** `IsolationForest` (Scikit-Learn)
* **Features Used:**
    * `packets_per_hour`: Intensity of operator activity.
    * `biometric_success_rate`: < 10% or > 95% are suspicious.
    * `off_hour_activity`: Enrollments done between 10 PM - 6 AM.
* **The Logic:**
    The model calculates an `anomaly_score` for every center.
    ```python
    # Logic Snippet
    model = IsolationForest(contamination=0.05)
    df['anomaly_score'] = model.fit_predict(features)
    
    # -1 indicates an anomaly (potential fraud)
    potential_fraud = df[df['anomaly_score'] == -1]
    ```

### 2. 🔥 Engine B: Migration Tracker (Boom Town Detection)
This engine identifies where infrastructure is breaking due to population influx.

* **Logic:** **Velocity Ratio Analysis**
    We compare the current enrollment rate against the historical baseline.
* **The Math:**
    $$ \text{Velocity Ratio} = \frac{\text{Avg Daily Enrollments (Last 30 Days)}}{\text{Avg Daily Enrollments (Previous 180 Days)}} $$
* **Thresholds:**
    * `Ratio > 1.5` (50% increase): **"Emerging Hotspot"**
    * `Ratio > 2.0` (100% increase): **"Boom Town"** (Triggers Infrastructure Alert)

### 3. 👻 Engine C: Demographic Scanner (Inclusion)
This engine identifies areas where citizens are "stuck"—unable to update their biometrics.

* **Logic:** **Exclusion Index**
    We look for a specific correlation: High Elderly Population + Low Biometric Success + Low Update Velocity.
* **The Math:**
    $$ \text{Exclusion Score} = (\text{Elderly Ratio} \times 0.5) + (\text{Bio Failure Rate} \times 0.5) $$
* **Outcome:**
    If `Exclusion Score > 0.8`, the district is flagged as a **"Digital Dark Zone"**, automatically generating a route plan for Mobile Aadhaar Vans.

---

## 💡 The "Secret Sauce": Cross-Engine Context

The biggest differentiator of Aadhaar Drishti is that **engines talk to each other**. A fraud alert is not valid until it passes the "Context Check."

**The Workflow:**
1.  **Step 1:** `Integrity Shield` detects a spike at Center X (Anomaly = True).
2.  **Step 2:** System queries `Migration Tracker` for the same District.
3.  **Step 3:**
    * *If Migration Tracker says "Boom Town":* The system **SUPPRESSES** the fraud alert. (Reason: The spike is due to legitimate workers arriving).
    * *If Migration Tracker says "Normal":* The system **ESCALATES** the alert to High Risk.

> **Impact:** This logic reduces false positive fraud alerts by an estimated **25%**, saving thousands of auditor hours.

---

## ⚙️ Tech Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Frontend** | Streamlit | Interactive Command Center Dashboard |
| **Data Processing** | Pandas / NumPy | Time-series aggregation & cleaning |
| **Machine Learning** | Scikit-Learn | Isolation Forest (Anomaly Detection) |
| **Visualization** | Plotly Express | Geospatial Heatmaps & Interactive Charts |
| **Deployment** | Streamlit Cloud | Instant web-based delivery |

---

## 🚀 Installation & Setup

Follow these steps to run the National Command Center locally.

### Prerequisites
* Python 3.8 or higher
* Git

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/aadhaar-drishti.git](https://github.com/your-username/aadhaar-drishti.git)
cd aadhaar-drishti