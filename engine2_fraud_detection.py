import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# ==========================================
# CONFIGURATION
# ==========================================
INPUT_FEATURES = "aadhaar_features_ready_for_ML.csv"
INPUT_BOOM_TOWNS = "engine1_boom_towns.csv"
OUTPUT_FRAUD = "engine2_fraud_audit_trail.csv" # Renamed to reflect it contains suppressed rows too

print(f"🚀 Loading Data for Integrity Shield...")
df = pd.read_csv(INPUT_FEATURES)

# ==========================================
# 1. RISK FEATURE ENGINEERING
# ==========================================
print("   - Constructing Risk Profiles (Normalized)...")

fraud_features = df.groupby(['state', 'district', 'pincode']).agg(
    total_txns=('total_enrolment', 'sum'),
    velocity_q3=('enrol_velocity', lambda x: x.quantile(0.75)), # Robust Velocity
    max_velocity=('enrol_velocity', 'max'),
    weekend_activity=('is_weekend', 'mean'),
    bio_sum=('total_bio_updates', 'sum')
).reset_index()

# Normalize Biometric Rate
fraud_features['bio_rate'] = fraud_features['bio_sum'] / (fraud_features['total_txns'] + 1)

# Filter Noise (Only analyze centers with activity)
active_centers = fraud_features[fraud_features['total_txns'] > 50].copy().fillna(0)

print(f"   - Analyzing {len(active_centers)} active centers...")

# ==========================================
# 2. FEATURE SCALING (Refinement 1)
# ==========================================
# Isolation Forest works better if all inputs are on the same scale
print("   - Applying StandardScaler to features...")

features_to_use = ['velocity_q3', 'max_velocity', 'weekend_activity', 'bio_rate']
scaler = StandardScaler()

# Create scaled features for the model (Keep original DF clean for reporting)
X_scaled = scaler.fit_transform(active_centers[features_to_use])

# ==========================================
# 3. TRAIN ISOLATION FOREST
# ==========================================
print("   - Training Anomaly Detection Model...")

model = IsolationForest(
    n_estimators=100,
    contamination=0.01, # Top 1% anomalies
    random_state=42,
    n_jobs=-1
)

# Predict
active_centers['anomaly_score'] = model.fit_predict(X_scaled)
active_centers['severity_score'] = model.decision_function(X_scaled)

# Extract raw suspects (Score = -1)
suspects = active_centers[active_centers['anomaly_score'] == -1].copy()
print(f"   🚨 Initial Machine Learning Flags: {len(suspects)}")

# ==========================================
# 4. CONTEXT-AWARE SUPPRESSION (The Fix + Refinement 2)
# ==========================================
print("   - Cross-referencing with Boom Towns...")

try:
    boom_towns = pd.read_csv(INPUT_BOOM_TOWNS)
    
    # REQUIRED FIX: Use proper merge with indicator
    # We merge Suspects (Left) with Boom Towns (Right) on location keys
    merged = pd.merge(
        suspects, 
        boom_towns[['state', 'district', 'pincode']], 
        on=['state', 'district', 'pincode'], 
        how='left', 
        indicator=True
    )
    
    # Logic:
    # _merge == 'both'      -> It is a Boom Town (Suppress it)
    # _merge == 'left_only' -> It is NOT a Boom Town (True Fraud Risk)
    
    def tag_status(row):
        if row['_merge'] == 'both':
            return "SUPPRESSED - Verified Migration Boom"
        else:
            return "HIGH RISK - Action Required"

    merged['audit_status'] = merged.apply(tag_status, axis=1)
    
    # Calculate stats
    suppressed_count = len(merged[merged['audit_status'].str.contains("SUPPRESSED")])
    risk_count = len(merged[merged['audit_status'].str.contains("HIGH RISK")])
    
    print(f"     ✅ Verified {suppressed_count} alerts as legitimate migration.")
    print(f"     🔥 Confirmed {risk_count} alerts as High Risk Fraud.")

except FileNotFoundError:
    print("     ⚠️ Warning: Boom Town file missing. Marking all as High Risk.")
    merged = suspects.copy()
    merged['audit_status'] = "HIGH RISK - Action Required"

# ==========================================
# 5. EXPLAINABILITY & SAVE
# ==========================================
def explain_fraud(row):
    reasons = []
    # Using scaled-back logic or raw thresholds for explanation text
    if row['weekend_activity'] > 0.4: reasons.append("Suspicious Weekend Activity")
    if row['velocity_q3'] > 50: reasons.append("Sustained High Speed")
    if row['bio_rate'] < 0.1: reasons.append("Abnormally Low Bio Updates") 
    if row['max_velocity'] > 150: reasons.append("Impossible Speed Spike")
    
    if not reasons: reasons.append("Statistical Pattern Anomaly")
    return ", ".join(reasons)

merged['risk_reason'] = merged.apply(explain_fraud, axis=1)

# Sort: High Risk first, then by Severity
merged = merged.sort_values(by=['audit_status', 'severity_score'], ascending=[True, True])

# Clean Columns
cols = ['state', 'district', 'pincode', 'audit_status', 'total_txns', 'risk_reason', 'severity_score']
merged[cols].to_csv(OUTPUT_FRAUD, index=False)

print(f"\n🎉 SUCCESS! Audit Trail Generated: {OUTPUT_FRAUD}")
print("\n--- SAMPLE AUDIT TRAIL ---")
print(merged[['pincode', 'audit_status', 'risk_reason']].head(5))