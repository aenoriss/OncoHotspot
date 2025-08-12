"""Base extractor class for Bronze layer"""

from abc import ABC, abstractmethod
import json
import os
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
import yaml
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseExtractor(ABC):
    """Base class for all data extractors in the Bronze layer"""
    
    def __init__(self, config_path: str = None):
        """
        Initialize the base extractor
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.extraction_timestamp = datetime.utcnow()
        self.bronze_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'data'
        )
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from YAML file"""
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'config',
                'sources.yaml'
            )
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    @abstractmethod
    def extract(self, **kwargs) -> Dict[str, Any]:
        """
        Extract data from the source
        
        Returns:
            Dictionary containing extracted raw data
        """
        pass
    
    def save_raw(self, data: Dict[str, Any], source_name: str) -> Dict[str, Any]:
        """
        Save raw data to Bronze layer with metadata
        
        Args:
            data: Raw data to save
            source_name: Name of the data source
            
        Returns:
            Metadata about the saved data
        """
        # Create metadata
        metadata = {
            'source': source_name,
            'extraction_time': self.extraction_timestamp.isoformat(),
            'record_count': self._count_records(data),
            'checksum': self._calculate_checksum(data),
            'schema_version': '1.0'
        }
        
        # Create directory if it doesn't exist
        source_dir = os.path.join(self.bronze_path, source_name.split('_')[0])
        os.makedirs(source_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp_str = self.extraction_timestamp.strftime('%Y%m%d_%H%M%S')
        data_file = os.path.join(source_dir, f'{source_name}_{timestamp_str}.json')
        metadata_file = os.path.join(source_dir, f'{source_name}_{timestamp_str}_metadata.json')
        
        # Save data
        with open(data_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        # Save metadata
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Saved {metadata['record_count']} records to {data_file}")
        
        return metadata
    
    def _calculate_checksum(self, data: Dict) -> str:
        """Calculate MD5 checksum of the data"""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def _count_records(self, data: Dict) -> int:
        """Count total records in the data"""
        count = 0
        for key, value in data.items():
            if isinstance(value, list):
                count += len(value)
            elif isinstance(value, dict):
                count += 1
        return count
    
    def rate_limit(self, source_name: str):
        """Apply rate limiting based on configuration"""
        if source_name in self.config.get('sources', {}):
            rate_config = self.config['sources'][source_name].get('rate_limit', {})
            delay = 1.0 / rate_config.get('requests_per_second', 10)
            time.sleep(delay)
    
    def handle_error(self, error: Exception, context: str) -> None:
        """
        Handle extraction errors
        
        Args:
            error: The exception that occurred
            context: Context information about where the error occurred
        """
        logger.error(f"Error in {context}: {str(error)}")
        
        # Save error log
        error_dir = os.path.join(self.bronze_path, 'errors')
        os.makedirs(error_dir, exist_ok=True)
        
        error_file = os.path.join(
            error_dir, 
            f'error_{self.extraction_timestamp.strftime("%Y%m%d_%H%M%S")}.json'
        )
        
        error_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'context': context,
            'error': str(error),
            'error_type': type(error).__name__
        }
        
        with open(error_file, 'w') as f:
            json.dump(error_data, f, indent=2)