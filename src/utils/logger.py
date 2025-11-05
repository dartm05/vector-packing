"""
Logging utilities
"""

import logging
import sys
from datetime import datetime


class Logger:
    """
    Configurable logger for the vector packing solver.
    """
    
    @staticmethod
    def setup_logger(name: str = 'VectorPacking',
                    level: str = 'INFO',
                    log_file: str = None) -> logging.Logger:
        """
        Setup and configure logger.
        
        Args:
            name: Logger name
            level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
            log_file: Optional file to write logs to
            
        Returns:
            Configured logger
        """
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper()))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler (optional)
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    @staticmethod
    def log_experiment_start(logger: logging.Logger, config: dict):
        """Log experiment configuration"""
        logger.info("="*60)
        logger.info("EXPERIMENT START")
        logger.info("="*60)
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        for key, value in config.items():
            logger.info(f"{key}: {value}")
        logger.info("="*60)
    
    @staticmethod
    def log_experiment_end(logger: logging.Logger, results: dict):
        """Log experiment results"""
        logger.info("="*60)
        logger.info("EXPERIMENT END")
        logger.info("="*60)
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        for key, value in results.items():
            logger.info(f"{key}: {value}")
        logger.info("="*60)
