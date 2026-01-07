import pandas as pd
import glob
import os

# ==========================================
# CONFIGURATION
# ==========================================
# Make sure this matches your folder name in VS Code
DATA_FOLDER = 'DataFolder'  

print(f"🕵️ Scanning inside '{DATA_FOLDER}'...")

def load_and_deduplicate(file_pattern, category_name):
    # 1. Recursive Search (Finds files in subfolders)
    search_path = os.path.join(DATA_FOLDER, "**", file_pattern)
    files = glob.glob(search_path, recursive=True)
    
    if len(files) == 0:
        print(f"   ⚠️ No files found for {category_name}")
        return pd.DataFrame()
    
    # 2. Load Files
    df_list = []
    for f in files:
        try:
            temp_df = pd.read_csv(f)
            temp_df.columns = temp_df.columns.str.strip().str.lower()
            df_list.append(temp_df)
        except Exception as e:
            print(f"      ❌ Error loading {f}: {e}")

    if not df_list:
        return pd.DataFrame()
        
    full_df = pd.concat(df_list, ignore_index=True)
    print(f"   📉 {category_name} Raw: {len(full_df)} rows.")

    # 3. FIX DATES (Critical step)
    if 'date' in full_df.columns:
        full_df['date'] = pd.to_datetime(full_df['date'], dayfirst=True, errors='coerce')
        # Drop rows where Date became NaT (invalid)
        full_df = full_df.dropna(subset=['date'])

    # 4. REMOVE DUPLICATES (The Fix)
    # We keep the FIRST occurrence of a specific Date+Pincode and drop the rest.
    # This prevents the 50GB Memory Error.
    subset_cols = ['date', 'state', 'district', 'pincode']
    valid_subset = [c for c in subset_cols if c in full_df.columns]
    
    full_df = full_df.drop_duplicates(subset=valid_subset, keep='first')
    
    print(f"   ✅ {category_name} De-Duplicated: {len(full_df)} unique rows.")
    return full_df

# ==========================================
# EXECUTION
# ==========================================
print("\n--- 1. LOADING ---")
# Using *.csv pattern to match your files
df_enrol = load_and_deduplicate("*enrolment*.csv", "Enrolment")
df_demo  = load_and_deduplicate("*demographic*.csv", "Demographic")
df_bio   = load_and_deduplicate("*biometric*.csv", "Biometric")

print("\n--- 2. MERGING ---")
if df_enrol.empty and df_demo.empty and df_bio.empty:
    print("❌ CRITICAL: No data loaded.")
else:
    # Merge Keys
    merge_keys = ['date', 'state', 'district', 'pincode']
    
    # Start with Enrolment
    if not df_enrol.empty:
        df_master = df_enrol
    elif not df_demo.empty:
        df_master = df_demo
    else:
        df_master = df_bio

    # Merge Demographic
    if not df_demo.empty and not df_master.equals(df_demo):
        print("   🔗 Merging Demographic...")
        df_master = pd.merge(df_master, df_demo, on=merge_keys, how='outer', suffixes=('_enrol', '_demo'))
        
    # Merge Biometric
    if not df_bio.empty and not df_master.equals(df_bio):
        print("   🔗 Merging Biometric...")
        df_master = pd.merge(df_master, df_bio, on=merge_keys, how='outer', suffixes=('', '_bio'))

    # Fill NaN with 0 (For counts)
    df_master = df_master.fillna(0)
    
    print("\n--- 3. SAVING ---")
    output_filename = "aadhaar_master_dataset_FINAL22.csv"
    df_master.to_csv(output_filename, index=False)
    print(f"🎉 SUCCESS! Saved '{output_filename}' with {len(df_master)} rows.")