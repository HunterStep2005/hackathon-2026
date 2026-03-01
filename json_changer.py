import pandas as pd
import json

# Load the Metrics sheet from the edited Excel file
df = pd.read_excel('HCA Census Metrics Edited.xlsx', sheet_name='Metrics')

# Standardize column names
df.columns = ['Metric', 'OrgId', 'SourceUpdateDate', 'MetricValue']

# Ensure OrgId is string
df['OrgId'] = df['OrgId'].astype(str)

# Convert SourceUpdateDate to datetime intelligently
if pd.api.types.is_numeric_dtype(df['SourceUpdateDate']):
    df['datetime'] = pd.to_datetime(df['SourceUpdateDate'], unit='d', origin='1899-12-30')
else:
    df['datetime'] = pd.to_datetime(df['SourceUpdateDate'])

# Sort and drop duplicates (keep last for same OrgId, Metric, datetime)
df = df.sort_values(['OrgId', 'Metric', 'datetime'])
df = df.drop_duplicates(['OrgId', 'Metric', 'datetime'], keep='last')

# Build the chartData structure
chart_data = {}
for org_id, org_group in df.groupby('OrgId'):
    chart_data[org_id] = {}
    for metric, met_group in org_group.groupby('Metric'):
        data_list = []
        for _, row in met_group.iterrows():
            t = row['datetime'].strftime('%Y-%m-%dT%H:%M:%S')
            v = int(row['MetricValue'])  # Convert to int for consistency
            data_list.append({'t': t, 'v': v})
        chart_data[org_id][metric] = data_list

# Create the output dict
output = {'chartData': chart_data}

# Write to JSON file without indentation to match the compact format
with open('C:\hackathon-2026\data-charts(1).json', 'w') as f:
    json.dump(output, f, separators=(',', ':'))
    
print("Converted data saved as 'data-charts(1).json'")