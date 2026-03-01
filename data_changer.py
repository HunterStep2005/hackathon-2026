import pandas as pd

# Define real and generated facility IDs (as strings for consistency)
real_ids = ['12345', '23456', '34567', '45678']
generated_ids = ['1234', '56789', '67890', '78901', '89012', '90123']

# Reference mappings: chosen based on closest # Beds and ensuring births >0 where applicable
ref_map = {
    '1234': '12345',    # Savannah 381 -> Denver 452
    '56789': '12345',   # Orlando 458 -> Denver 452
    '67890': '23456',   # Tampa 664 -> Austin 768
    '78901': '12345',   # Salt Lake 468 -> Denver 452
    '89012': '45678',   # Myrtle 246 -> Hopewell 132 (has births)
    '90123': '12345'    # Nashville 321 -> Denver 452
}

# Load sheets
df_fac = pd.read_excel("C:\hackathon-2026\HCA Census Metrics.xlsx", sheet_name='Facility Info')
df_met = pd.read_excel("C:\hackathon-2026\HCA Census Metrics.xlsx", sheet_name='Metrics')

# Standardize columns in Metrics (assuming first column is Metric)
df_met.columns = ['Metric', 'OrgId', 'SourceUpdateDate', 'MetricValue']
df_met['OrgId'] = df_met['OrgId'].astype(str)  # Ensure OrgId is string

# Filter to real data
real_df = df_met[df_met['OrgId'].isin(real_ids)].copy()

# List to hold generated dataframes
gen_dfs = []

# Generate data for each generated facility
for gen_id in generated_ids:
    ref_id = ref_map[gen_id]
    
    # Get scales
    gen_beds = df_fac[df_fac['Facility ID'] == int(gen_id)]['# Beds'].values[0]
    ref_beds = df_fac[df_fac['Facility ID'] == int(ref_id)]['# Beds'].values[0]
    scale_beds = gen_beds / ref_beds
    
    gen_icu_max = df_fac[df_fac['Facility ID'] == int(gen_id)]['ICU Max'].values[0]
    ref_icu_max = df_fac[df_fac['Facility ID'] == int(ref_id)]['ICU Max'].values[0]
    scale_icu = gen_icu_max / ref_icu_max
    
    # Copy reference data
    gen_df = df_met[df_met['OrgId'] == ref_id].copy()
    gen_df['OrgId'] = gen_id
    
    # Scale values based on metric
    for idx in gen_df.index:
        metric = gen_df.at[idx, 'Metric']
        val = gen_df.at[idx, 'MetricValue']
        
        if metric in ['Admissions', 'Births', 'Discharges', 'Total Census']:
            new_val = round(val * scale_beds)
        elif metric == 'ICU Occupancy':
            new_val = round(val * scale_icu)
        else:
            new_val = val  # Unchanged if any unexpected metric
        
        gen_df.at[idx, 'MetricValue'] = new_val
    
    gen_dfs.append(gen_df)

# Combine real and generated
new_met_df = pd.concat([real_df] + gen_dfs)

# Sort for consistency (by OrgId, Metric, SourceUpdateDate ascending)
new_met_df = new_met_df.sort_values(['OrgId', 'Metric', 'SourceUpdateDate'])

# Write to new Excel file
with pd.ExcelWriter('C:\hackathon-2026\HCA Census Metrics Edited.xlsx', engine='openpyxl') as writer:
    df_fac.to_excel(writer, sheet_name='Facility Info', index=False)
    new_met_df.to_excel(writer, sheet_name='Metrics', index=False)

print("Edited file saved as 'HCA Census Metrics Edited.xlsx'")