from azure.storage.blob import BlobServiceClient
import os

# Import credentials from config file (create config.py with your Azure credentials)
try:
    from config import AZURE_STORAGE_ACCOUNT, AZURE_STORAGE_KEY
    ACCOUNT_NAME = AZURE_STORAGE_ACCOUNT
    ACCOUNT_KEY = AZURE_STORAGE_KEY
except ImportError:
    print("❌ Please create config.py with your Azure credentials:")
    print("AZURE_STORAGE_ACCOUNT = 'your_storage_account'")
    print("AZURE_STORAGE_KEY = 'your_storage_key'")
    exit(1)

CONTAINER_NAME = "cleaned-data"

def download_all_cleaned_data():
    service_client = BlobServiceClient(f"https://{ACCOUNT_NAME}.blob.core.windows.net", credential=ACCOUNT_KEY)
    container = service_client.get_container_client("cleaned-data")

    datasets = {
        'Demand' : 'data/demand/',
        'DemandZonal' : 'data/demandzonal/',
        'EnergyLMP' : 'data/energy_lmp/',
        'GenMix' : 'data/genmix/',
        'IntertieLMP' : 'data/intertie_lmp/',
        'pub_demand' : 'data/pub_demand/',
    }

    for dataset, local_dir in datasets.items():
        os.makedirs(local_dir, exist_ok=True)
        blobs = container.list_blobs(name_starts_with=f"{dataset}/year=2025/")
        for blob in blobs: 
            if blob.name.endswith('.csv'):
                filename = os.path.basename(blob.name)
                local_path = os.path.join(local_dir,filename)

                print(f"📥 Downloading: {blob.name}")
                with open(local_path, "wb") as f:
                    f.write(container.get_blob_client(blob.name).download_blob().readall())
                    
    print("✅ All data downloaded!")

if __name__ == "__main__":
    download_all_cleaned_data()