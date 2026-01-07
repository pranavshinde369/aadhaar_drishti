import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# ==========================================
# CONFIGURATION
# ==========================================
INPUT_FILE = "aadhaar_features_ready_for_ML.csv"

# Output Files
OUTPUT_FRAUD  = "engine_fraud_30days.csv"
OUTPUT_BOOM   = "engine_boom_180days.csv"
OUTPUT_GHOST  = "engine_ghost_3years.csv"
OUTPUT_DIGITAL= "engine_digital_1year.csv"

print(f"🚀 Loading Master Dataset: {INPUT_FILE}...")
df = pd.read_csv(INPUT_FILE)

# 1. TIME INDEXING (Mandatory Rule 1)
df['date'] = pd.to_datetime(df['date'])
LATEST_DATE = df['date'].max()
print(f"   📅 Data Reference Date: {LATEST_DATE.date()}")

# ==========================================
# HELPER: TIME SLICER
# ==========================================
def get_time_slice(days):
    """Returns data from (Latest Date - Days) to Latest Date"""
    cutoff = LATEST_DATE - pd.Timedelta(days=days)
    return df[df['date'] >= cutoff].copy()

# ==========================================
# 🔴 ENGINE 3: INTEGRITY SHIELD (Fraud)
# ⏳ Horizon: Last 30 Days (Short-Term Burst)
# ==========================================
print("\n--- 🔴 Running Engine 3: Integrity Shield (Last 30 Days) ---")
fraud_df = get_time_slice(30)

if len(fraud_df) > 0:
    # Aggregation
    fraud_stats = fraud_df.groupby(['state', 'district', 'pincode']).agg(
        total_txns=('total_enrolment', 'sum'),
        velocity_q3=('enrol_velocity', lambda x: x.quantile(0.75)),
        max_velocity=('enrol_velocity', 'max'),
        weekend_activity=('is_weekend', 'mean'),
        bio_sum=('total_bio_updates', 'sum')
    ).reset_index()

    # Feature Engineering
    fraud_stats['bio_rate'] = fraud_stats['bio_sum'] / (fraud_stats['total_txns'] + 1)
    
    # Filter Noise
    active_fraud = fraud_stats[fraud_stats['total_txns'] > 10].fillna(0).copy()
    
    # ML: Isolation Forest
    features = ['velocity_q3', 'max_velocity', 'weekend_activity', 'bio_rate']
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(active_fraud[features])
    
    model = IsolationForest(contamination=0.01, random_state=42)
    active_fraud['anomaly_score'] = model.fit_predict(X_scaled)
    active_fraud['severity_score'] = model.decision_function(X_scaled)
    
    # Extract Suspects
    fraud_suspects = active_fraud[active_fraud['anomaly_score'] == -1].copy()
    
    # Explainability
    def explain_fraud(row):
        reasons = []
        if row['weekend_activity'] > 0.4: reasons.append("Suspicious Weekend Activity")
        if row['velocity_q3'] > 50: reasons.append("Sustained High Speed")
        if row['bio_rate'] < 0.1: reasons.append("Abnormally Low Bio Updates") 
        return ", ".join(reasons) if reasons else "Pattern Anomaly"

    fraud_suspects['risk_reason'] = fraud_suspects.apply(explain_fraud, axis=1)
    print(f"   🚨 Detected {len(fraud_suspects)} Short-Term Fraud Suspects")
else:
    print("   ⚠️ Insufficient data for 30-day window.")
    fraud_suspects = pd.DataFrame()

# ==========================================
# 🔥 ENGINE 1A: BOOM TOWNS
# ⏳ Horizon: Last 180 Days (Seasonal Migration)
# ==========================================
print("\n--- 🔥 Running Engine 1A: Boom Towns (Last 6 Months) ---")
boom_df = get_time_slice(180)

boom_stats = boom_df.groupby(['state', 'district', 'pincode']).agg(
    velocity_q3=('enrol_velocity', lambda x: x.quantile(0.75)),
    volume_sum=('total_enrolment', 'sum'),
    child_ratio=('child_ratio', 'mean')
).reset_index().fillna(0)

# Thresholds
vel_95 = boom_stats['velocity_q3'].quantile(0.95)
vol_med = boom_stats['volume_sum'].median()

# Detection
boom_towns = boom_stats[
    (boom_stats['velocity_q3'] > vel_95) & 
    (boom_stats['volume_sum'] > vol_med) & 
    (boom_stats['child_ratio'] < 0.3)
].copy()

print(f"   🔥 Identified {len(boom_towns)} Migration Hubs")
boom_towns.to_csv(OUTPUT_BOOM, index=False)

# ==========================================
# 👻 ENGINE 1B: GHOST VILLAGES
# ⏳ Horizon: Last 3 Years (Structural Ageing)
# ==========================================
print("\n--- 👻 Running Engine 1B: Ghost Villages (Last 3 Years) ---")
ghost_df = get_time_slice(365 * 3)

ghost_stats = ghost_df.groupby(['state', 'district', 'pincode']).agg(
    elderly_pressure_median=('elderly_pressure', 'median'),
    volume_median=('total_enrolment', 'median')
).reset_index().fillna(0)

# Thresholds
press_90 = ghost_stats['elderly_pressure_median'].quantile(0.90)
vol_base = ghost_stats['volume_median'].median()

# Detection
ghost_villages = ghost_stats[
    (ghost_stats['elderly_pressure_median'] > press_90) &
    (ghost_stats['volume_median'] <= vol_base)
].copy()

print(f"   👻 Identified {len(ghost_villages)} Long-Term Ghost Villages")
ghost_villages.to_csv(OUTPUT_GHOST, index=False)

# ==========================================
# 📱 ENGINE 1C: DIGITAL DIVIDE OVERLAY
# ⏳ Horizon: Last 1 Year (Adoption Curve)
# ==========================================
print("\n--- 📱 Running Engine 1C: Digital Divide (Last 1 Year) ---")
digital_df = get_time_slice(365)

digital_stats = digital_df.groupby(['state', 'district', 'pincode']).agg(
    elderly_pressure=('elderly_pressure', 'median'),
    bio_sum=('total_bio_updates', 'sum'),
    total_vol=('total_enrolment', 'sum')
).reset_index().fillna(0)

digital_stats['bio_rate'] = digital_stats['bio_sum'] / (digital_stats['total_vol'] + 1)

# Thresholds
grey_80 = digital_stats['elderly_pressure'].quantile(0.80)
tech_25 = digital_stats['bio_rate'].quantile(0.25)

digital_zones = digital_stats[
    (digital_stats['elderly_pressure'] > grey_80) &
    (digital_stats['bio_rate'] < tech_25) &
    (digital_stats['total_vol'] > 50)
].copy()

digital_zones['action'] = "Deploy Digital Sahayak"
print(f"   🚨 Identified {len(digital_zones)} Digital Dark Zones")
digital_zones.to_csv(OUTPUT_DIGITAL, index=False)

# ==========================================
# 🛡️ CONTEXT-AWARE AUDIT (The Suppression Logic)
# ==========================================
print("\n--- 🛡️ Generating Audit Trail ---")
if not fraud_suspects.empty and not boom_towns.empty:
    # Merge Fraud Suspects with Boom Towns
    merged = pd.merge(
        fraud_suspects, 
        boom_towns[['state', 'district', 'pincode']], 
        on=['state', 'district', 'pincode'], 
        how='left', 
        indicator=True
    )
    
    def tag_audit(row):
        if row['_merge'] == 'both':
            return "SUPPRESSED - Verified Migration Context"
        else:
            return "HIGH RISK - Action Required"

    merged['audit_status'] = merged.apply(tag_audit, axis=1)
    
    # Save Final Fraud Report
    cols = ['state', 'district', 'pincode', 'audit_status', 'risk_reason', 'severity_score']
    merged[cols].to_csv(OUTPUT_FRAUD, index=False)
    
    suppressed = len(merged[merged['audit_status'].str.contains("SUPPRESSED")])
    print(f"   ✅ Suppressed {suppressed} False Positives using Multi-Horizon Logic.")
    print(f"   💾 Final Fraud Report: {OUTPUT_FRAUD}")

print("\n🎉 MULTI-HORIZON ANALYSIS COMPLETE.")