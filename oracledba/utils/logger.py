"""
Logger utility
"""

import logging
from pathlib import Path
from datetime import datetime

def setup_logger(name='oracledba', log_dir='/var/log/oracledba'):
    """Setup logger"""
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    log_file = log_path / f"oracledba_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(name)


logger = setup_logger()
