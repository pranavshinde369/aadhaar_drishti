import pandas as pd
import numpy as np

# ==========================================
# CONFIGURATION
# ==========================================
INPUT_FILE = "aadhaar_master_dataset_FINAL22.csv" 
OUTPUT_FILE = "aadhaar_features_ready_for_ML.csv"

print(f"🚀 Loading {INPUT_FILE}...")
df = pd.read_csv(INPUT_FILE)

# ==========================================
# 1. RENAME COLUMNS (Strict Mapping)
# ==========================================
print("   - Renaming columns...")

# Mapping your RAW columns to the NAMES needed for formulas
rename_map = {
    'age_18_greater': 'age_18_plus',       # Enrolment Adult
    'demo_age_5_17':  'demo_young',        # Demographic Young (Proxy for 0-17)
    'demo_age_17_':   'demo_old',          # Demographic Old
    'bio_age_5_17':   'bio_young',         # Biometric Young (5-17)
    'bio_age_17_':    'bio_old'            # Biometric Old (17+)
}

df = df.rename(columns=rename_map)

# Verify Renaming
required = ['age_0_5', 'age_5_17', 'age_18_plus', 'demo_young', 'demo_old', 'bio_young', 'bio_old']
missing = [c for c in required if c not in df.columns]

if missing:
    print(f"❌ ERROR: Still missing columns: {missing}")
    print(f"   Current Columns: {list(df.columns)}")
    exit()
else:
    print("   ✅ Rename successful.")

# ==========================================
# 2. FILL NULLS (Safety)
# ==========================================
# Replace NaN with 0 for all math columns
for c in required:
    df[c] = df[c].fillna(0)

# ==========================================
# 3. CALCULATE FORMULAS (Adjusted for your data)
# ==========================================
print("   - Calculating Metrics...")

# Formula 1: Total Enrolment
# (Sum of all 3 enrolment columns you have)
df['total_enrolment'] = df['age_0_5'] + df['age_5_17'] + df['age_18_plus']

# Formula 2: Total Biometric Updates
# (Sum of Young + Old biometric updates)
df['total_bio_updates'] = df['bio_young'] + df['bio_old']

# Formula 3: Child Ratio
# (Enrolment 0-5 / Total Enrolment + 1)
df['child_ratio'] = df['age_0_5'] / (df['total_enrolment'] + 1)

# Formula 4: Elderly Pressure (Migration Proxy)
# (Old Demographic Updates / Young Demographic Updates + 1)
# Note: Using 'demo_young' (5-17) because you don't have 0-5 demo data.
df['elderly_pressure'] = df['demo_old'] / (df['demo_young'] + 1)

# ==========================================
# 4. TIME & VELOCITY
# ==========================================
print("   - Calculating Velocity...")

df['date'] = pd.to_datetime(df['date'])
df = df.sort_values(by=['pincode', 'date'])

# Velocity: How fast is enrolment growing?
df['enrol_velocity'] = df.groupby('pincode')['total_enrolment'].diff().fillna(0)

# Time Features
df['month'] = df['date'].dt.month
df['is_weekend'] = df['date'].dt.dayofweek.apply(lambda x: 1 if x >= 5 else 0)

# ==========================================
# 5. SAVE
# ==========================================
df.to_csv(OUTPUT_FILE, index=False)
print(f"\n🎉 SUCCESS! Feature Engineering Complete.")
print(f"💾 Saved to: {OUTPUT_FILE}")