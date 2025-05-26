import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from typing import List, Dict
import urllib3

# Disable SSL warnings for IESO sites
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scrape_ieso_directory(base_url: str, file_pattern: str = None) -> List[Dict]:
    """Scrape IESO directory page for file links"""
    try:
        response = requests.get(base_url, verify=False, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        files = []
        for link in soup.find_all("a", href=True):
            href = link['href']
            text = link.text.strip()
            
            if href in ['../', '../'] or not text:
                continue
                
            if file_pattern and not re.search(file_pattern, text):
                continue
            
            full_url = href if href.startswith('http') else base_url.rstrip('/') + '/' + href.lstrip('/')
            
            files.append({
                'name': text,
                'url': full_url,
                'size': '',
                'modified': ''
            })
        
        return files
        
    except Exception as e:
        print(f"❌ Error scraping {base_url}: {e}")
        return []

def extract_date_from_filename(filename: str) -> datetime:
    """Extract date from IESO filename patterns"""
    # Pattern 1: YYYYMMDDHH format (EnergyLMP, IntertieLMP)
    match = re.search(r'(\d{8})\d{2}', filename)
    if match:
        date_str = match.group(1)
        try:
            return datetime.strptime(date_str, '%Y%m%d')
        except ValueError:
            pass
    
    # Pattern 2: YYYY format (GenMix, Demand)
    match = re.search(r'_(\d{4})_', filename)
    if match:
        year = int(match.group(1))
        if year >= 2020:
            return datetime(year, 1, 1)
    
    return None

def get_latest_version_files(files: List[Dict]) -> List[Dict]:
    """Keep only the highest version per base name"""
    file_groups = {}
    
    for file in files:
        base_name = re.sub(r'_v\d+', '', file['name'])
        if base_name not in file_groups:
            file_groups[base_name] = []
        file_groups[base_name].append(file)
    
    latest_files = []
    for base_name, group in file_groups.items():
        if len(group) == 1:
            latest_files.append(group[0])
        else:
            def get_version(f):
                match = re.search(r'_v(\d+)', f['name'])
                return int(match.group(1)) if match else 0
            
            latest_file = max(group, key=get_version)
            latest_files.append(latest_file)
    
    return latest_files

def download_file(url: str, timeout: int = 60) -> bytes:
    """Download file from URL and return content as bytes"""
    try:
        response = requests.get(url, verify=False, timeout=timeout)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"❌ Error downloading {url}: {e}")
        raise

def filter_files_by_date(files: List[Dict], start_date: datetime, end_date: datetime = None) -> List[Dict]:
    """Filter files by date range based on filename patterns"""
    if end_date is None:
        end_date = datetime.now()
    
    filtered = []
    for file in files:
        file_date = extract_date_from_filename(file['name'])
        if file_date and start_date <= file_date <= end_date:
            filtered.append(file)
    
    return filtered 