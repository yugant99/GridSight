#!/usr/bin/env python3
"""
Setup script for Azure Live Scraper
Helps users configure their Azure credentials
"""

import os
import shutil

def setup_config():
    """Setup configuration file"""
    config_template = "config_template.py"
    config_file = "config.py"
    
    if os.path.exists(config_file):
        print(f"✅ {config_file} already exists")
        return
    
    if not os.path.exists(config_template):
        print(f"❌ {config_template} not found")
        return
    
    # Copy template to config
    shutil.copy(config_template, config_file)
    print(f"✅ Created {config_file} from template")
    
    print(f"\n📝 Next steps:")
    print(f"1. Edit {config_file} and add your Azure credentials:")
    print(f"   - ACCOUNT_NAME: Your Azure storage account name")
    print(f"   - ACCOUNT_KEY: Your Azure storage account key")
    print(f"2. Install dependencies: pip install -r requirements.txt")
    print(f"3. Run scraper: python energylmp_gap_filler.py")

def main():
    """Main setup function"""
    print("🚀 Azure Live Scraper Setup")
    print("=" * 30)
    setup_config()

if __name__ == "__main__":
    main() 