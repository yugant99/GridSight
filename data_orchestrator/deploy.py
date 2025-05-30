#!/usr/bin/env python3
"""
Deployment script for ML Orchestrator Azure Function
Handles automated deployment to Azure with proper configuration
"""

import os
import sys
import subprocess
import json
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Azure configuration
FUNCTION_APP_NAME = "ml-orchestrator-gridsight"  # Must be globally unique
RESOURCE_GROUP = "my-data-project"  # Your existing resource group
LOCATION = "canadacentral"  # Same as your storage account
STORAGE_ACCOUNT = "datastoreyugant"  # Your existing storage account
STORAGE_KEY = "YOUR_AZURE_STORAGE_KEY_HERE"  # Replace with your actual storage key

def run_command(command, description=""):
    """Run shell command and handle errors"""
    try:
        logging.info(f"Running: {description or command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        if result.stdout:
            logging.info(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {e}")
        if e.stdout:
            logging.error(f"Stdout: {e.stdout}")
        if e.stderr:
            logging.error(f"Stderr: {e.stderr}")
        return False

def check_prerequisites():
    """Check if required tools are installed"""
    logging.info("🔍 Checking prerequisites...")
    
    # Check Azure CLI
    if not run_command("az --version", "Checking Azure CLI"):
        logging.error("❌ Azure CLI not found. Please install: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
        return False
    
    # Check Azure Functions Core Tools
    if not run_command("func --version", "Checking Azure Functions Core Tools"):
        logging.error("❌ Azure Functions Core Tools not found. Please install: npm install -g azure-functions-core-tools@4 --unsafe-perm true")
        return False
    
    logging.info("✅ Prerequisites check passed")
    return True

def login_to_azure():
    """Login to Azure CLI"""
    logging.info("🔐 Checking Azure login status...")
    
    # Check if already logged in
    result = subprocess.run("az account show", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        account_info = json.loads(result.stdout)
        logging.info(f"✅ Already logged in as: {account_info.get('user', {}).get('name', 'Unknown')}")
        return True
    
    # Need to login
    logging.info("Please login to Azure...")
    return run_command("az login", "Azure login")

def create_function_app():
    """Create Azure Function App if it doesn't exist"""
    logging.info(f"🏗️ Creating Function App: {FUNCTION_APP_NAME}")
    
    # Check if function app already exists
    check_cmd = f"az functionapp show --name {FUNCTION_APP_NAME} --resource-group {RESOURCE_GROUP}"
    result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        logging.info("✅ Function App already exists")
        return True
    
    # Create the function app
    create_cmd = f"""
    az functionapp create \
        --resource-group {RESOURCE_GROUP} \
        --consumption-plan-location {LOCATION} \
        --runtime python \
        --runtime-version 3.11 \
        --functions-version 4 \
        --name {FUNCTION_APP_NAME} \
        --storage-account {STORAGE_ACCOUNT} \
        --os-type Linux
    """
    
    if run_command(create_cmd, f"Creating Function App {FUNCTION_APP_NAME}"):
        logging.info("✅ Function App created successfully")
        return True
    else:
        logging.error("❌ Failed to create Function App")
        return False

def configure_app_settings():
    """Configure application settings (environment variables)"""
    logging.info("⚙️ Configuring application settings...")
    
    settings = [
        f"AZURE_STORAGE_ACCOUNT_NAME={STORAGE_ACCOUNT}",
        f"AZURE_STORAGE_ACCOUNT_KEY={STORAGE_KEY}",
        "PYTHONPATH=/home/site/wwwroot",
        "SCM_DO_BUILD_DURING_DEPLOYMENT=1"
    ]
    
    for setting in settings:
        cmd = f"az functionapp config appsettings set --name {FUNCTION_APP_NAME} --resource-group {RESOURCE_GROUP} --settings {setting}"
        if not run_command(cmd, f"Setting {setting.split('=')[0]}"):
            logging.error(f"❌ Failed to set {setting.split('=')[0]}")
            return False
    
    logging.info("✅ Application settings configured")
    return True

def deploy_function():
    """Deploy the function code"""
    logging.info("🚀 Deploying function code...")
    
    # Ensure we're in the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Deploy using Azure Functions Core Tools
    deploy_cmd = f"func azure functionapp publish {FUNCTION_APP_NAME} --python"
    
    if run_command(deploy_cmd, "Deploying function code"):
        logging.info("✅ Function deployed successfully")
        return True
    else:
        logging.error("❌ Function deployment failed")
        return False

def test_deployment():
    """Test the deployed function"""
    logging.info("🧪 Testing deployed function...")
    
    # Get function app URL
    url_cmd = f"az functionapp show --name {FUNCTION_APP_NAME} --resource-group {RESOURCE_GROUP} --query defaultHostName -o tsv"
    result = subprocess.run(url_cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        logging.error("❌ Could not get function app URL")
        return False
    
    function_url = f"https://{result.stdout.strip()}"
    logging.info(f"Function App URL: {function_url}")
    
    # Test health endpoint
    health_url = f"{function_url}/api/health"
    test_cmd = f"curl -s -o /dev/null -w '%{{http_code}}' {health_url}"
    
    result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)
    if result.stdout.strip() == "200":
        logging.info("✅ Health check passed")
        return True
    else:
        logging.warning(f"⚠️ Health check returned status: {result.stdout.strip()}")
        return False

def main():
    """Main deployment workflow"""
    logging.info("🚀 STARTING ML ORCHESTRATOR DEPLOYMENT")
    logging.info("=" * 60)
    
    steps = [
        ("Prerequisites Check", check_prerequisites),
        ("Azure Login", login_to_azure),
        ("Create Function App", create_function_app),
        ("Configure Settings", configure_app_settings),
        ("Deploy Function", deploy_function),
        ("Test Deployment", test_deployment)
    ]
    
    for step_name, step_func in steps:
        logging.info(f"\n📋 Step: {step_name}")
        try:
            if not step_func():
                logging.error(f"❌ {step_name} failed")
                return False
        except Exception as e:
            logging.error(f"❌ {step_name} crashed: {str(e)}")
            return False
    
    logging.info("\n" + "=" * 60)
    logging.info("🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!")
    logging.info("=" * 60)
    
    logging.info(f"✅ Function App: {FUNCTION_APP_NAME}")
    logging.info(f"✅ Resource Group: {RESOURCE_GROUP}")
    logging.info(f"✅ Schedule: Daily at 2 PM EST")
    logging.info(f"✅ Health Check: https://{FUNCTION_APP_NAME}.azurewebsites.net/api/health")
    
    logging.info("\n📋 Next Steps:")
    logging.info("1. Monitor function execution in Azure Portal")
    logging.info("2. Check Application Insights for logs")
    logging.info("3. Verify ml-outputs container gets created")
    logging.info("4. Build Streamlit dashboard to consume predictions")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 