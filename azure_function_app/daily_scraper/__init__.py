import azure.functions as func
import logging
import os
import sys
from datetime import datetime, timezone

# Add scraper modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scraper_modules'))

def main(mytimer: func.TimerRequest) -> None:
    """
    Main Azure Function entry point
    Runs daily to scrape IESO data
    """
    
    utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    
    logging.info(f'🚀 IESO Data Scraper started at {utc_timestamp}')
    
    try:
        # Import our scraper (after path is set)
        from all_datasets_gap_filler import run_all_gap_fillers
        
        # Run the scraper
        logging.info('📊 Starting comprehensive gap filling...')
        results = run_all_gap_fillers()
        
        # Log results
        total_files = sum(r['files_processed'] for r in results.values())
        success_count = sum(1 for r in results.values() if r['status'] == 'success')
        
        logging.info(f'✅ Scraper completed: {total_files} files, {success_count}/5 datasets successful')
        
        # Log any errors
        for dataset, result in results.items():
            if result['status'] == 'error':
                logging.error(f'❌ {dataset} failed: {result["error"]}')
            else:
                logging.info(f'✅ {dataset}: {result["files_processed"]} files processed')
        
    except Exception as e:
        logging.error(f'💥 Fatal error in scraper: {str(e)}')
        raise
    
    logging.info('🎉 IESO Data Scraper completed successfully')
