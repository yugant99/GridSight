import pandas as pd 
csv_path = "/Users/yuganthareshsoni/project_tester_1/call_azure_cleanstep1/Azure_backfill/PUB_RealtimeDemandZonal.csv"
with open(csv_path) as f:
    for i , line in enumerate(f):
        if "Date" in line and "Hour" in line:
            header_index = i
            break

df = pd.read_csv(csv_path, skiprows=header_index)
df.columns = df.columns.str.strip()
df['timestamp'] = pd.to_datetime(df['Date']) + pd.to_timedelta(df['Hour'] - 1, unit='h')
print(df.isnull().sum())
print(df.info())
print(df.describe())
print(df.head())
print(df.tail())
print(df.shape)
print(df.columns)
print(df.dtypes)
print(df.index)
print(df.head())
cleaned_path = "/Users/yuganthareshsoni/project_tester_1/call_azure_cleanstep1/Azure_clean_notpushed/PUB_RealtimeDemandZonal_cleaned.csv"
df.to_csv(cleaned_path, index=False)
print(f"✅ Cleaned file saved to: {cleaned_path}")