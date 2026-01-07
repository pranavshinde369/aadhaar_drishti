import pandas as pd

# ==========================================
# CONFIGURATION
# ==========================================
INPUT_FILE = "aadhaar_features_ready_for_ML.csv"

# Output Files
OUTPUT_BOOM   = "engine1_boom_towns.csv"
OUTPUT_GHOST  = "engine1_ghost_villages.csv"
OUTPUT_DIGITAL = "policy_overlay_digital_divide.csv"

print(f"🚀 Loading Intelligence Data: {INPUT_FILE}...")
df = pd.read_csv(INPUT_FILE)

# ==========================================
# 1. ROBUST AGGREGATION (The Statistical Core)
# ==========================================
print("   - Aggregating Data (Using Robust Stat Metrics)...")

# We aggregate EVERYTHING in one go to be efficient
pin_stats = df.groupby(['state', 'district', 'pincode']).agg(
    # Velocity: Use 75th Percentile to ignore one-day spikes
    velocity_q3=('enrol_velocity', lambda x: x.quantile(0.75)),
    
    # Volume: Split into Scale (Sum) and Typical Day (Median)
    volume_sum=('total_enrolment', 'sum'),
    volume_median=('total_enrolment', 'median'),
    
    # Demographics: Use Median for Elderly Pressure (Structural Ageing)
    elderly_pressure_median=('elderly_pressure', 'median'),
    child_ratio_mean=('child_ratio', 'mean'),
    
    # Digital Awareness: Total Biometric Updates
    bio_sum=('total_bio_updates', 'sum')
).reset_index().fillna(0)

# Calculate Bio Compliance Rate (for Digital Overlay)
# (Bio Updates / Total Activity + 1)
pin_stats['bio_compliance_rate'] = pin_stats['bio_sum'] / (pin_stats['volume_sum'] + 1)

print(f"     Analyzed {len(pin_stats)} unique Pin Codes.")

# ==========================================
# 2. CALCULATE DYNAMIC THRESHOLDS
# ==========================================
print("   - Calculating Dynamic Percentiles (Auto-Tuning)...")

# Boom Town Thresholds
vel_95 = pin_stats['velocity_q3'].quantile(0.95)      # Top 5% Speed
vol_sum_median = pin_stats['volume_sum'].median()     # Top 50% Scale

# Ghost Village Thresholds
press_90 = pin_stats['elderly_pressure_median'].quantile(0.90) # Top 10% Oldest
vol_med_median = pin_stats['volume_median'].median()           # Typical day baseline

# Digital Dark Zone Thresholds
grey_80 = pin_stats['elderly_pressure_median'].quantile(0.80)  # Top 20% Oldest
bio_compliance_25 = pin_stats['bio_compliance_rate'].quantile(0.25) # Bottom 25% Tech-Savvy

print(f"     [Boom] Min Velocity (Q3): > {vel_95:.2f}")
print(f"     [Ghost] Min Elderly Pressure (Median): > {press_90:.2f}")
print(f"     [Digital] Max Compliance Rate: < {bio_compliance_25:.2f}")

# ==========================================
# 3. DETECT "BOOM TOWNS" (Migration Hubs)
# ==========================================
boom_towns = pin_stats[
    (pin_stats['velocity_q3'] > vel_95) & 
    (pin_stats['volume_sum'] > vol_sum_median) & 
    (pin_stats['volume_sum'] > 10) &  # Noise Filter (Must have activity)
    (pin_stats['child_ratio_mean'] < 0.3) # Adult Migration
].sort_values(by='velocity_q3', ascending=False)

# ==========================================
# 4. DETECT "GHOST VILLAGES" (Out-Migration)
# ==========================================
ghost_villages = pin_stats[
    (pin_stats['elderly_pressure_median'] > press_90) &
    (pin_stats['volume_median'] <= vol_med_median) # Stagnant Typical Day
].sort_values(by='elderly_pressure_median', ascending=False)

# ==========================================
# 5. DETECT "DIGITAL DARK ZONES" (Policy Overlay)
# ==========================================
digital_zones = pin_stats[
    (pin_stats['elderly_pressure_median'] > grey_80) & # Greying
    (pin_stats['bio_compliance_rate'] < bio_compliance_25) & # Neglect
    (pin_stats['volume_sum'] > 50) # Ignore empty places
].copy()

# Add Action Tag
digital_zones['recommended_action'] = "Deploy Mobile Aadhaar Vans + Assisted Digital Camps"
digital_zones = digital_zones.sort_values(by='elderly_pressure_median', ascending=False)

# ==========================================
# 6. SAVE ALL REPORTS
# ==========================================
boom_towns.to_csv(OUTPUT_BOOM, index=False)
ghost_villages.to_csv(OUTPUT_GHOST, index=False)
digital_zones.to_csv(OUTPUT_DIGITAL, index=False)

print(f"\n🎉 SUCCESS! All Intelligence Reports Generated:")
print(f"   🔥 Boom Towns Found: {len(boom_towns)} --> Saved to {OUTPUT_BOOM}")
print(f"   👻 Ghost Villages Found: {len(ghost_villages)} --> Saved to {OUTPUT_GHOST}")
print(f"   🚨 Digital Dark Zones: {len(digital_zones)} --> Saved to {OUTPUT_DIGITAL}")