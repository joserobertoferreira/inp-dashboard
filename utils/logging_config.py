import logging
import logging.config
import os


def setup_logging():
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)

    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {'format': '%(asctime)s - %(levelname)s - %(name)s - %(message)s'},
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
            },
            'info_file': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': os.path.join(log_dir, 'info.log'),
                'mode': 'a',
                'formatter': 'standard',
            },
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.FileHandler',
                'filename': os.path.join(log_dir, 'error.log'),
                'mode': 'a',
                'formatter': 'standard',
            },
        },
        'root': {'level': 'DEBUG', 'handlers': ['console', 'info_file', 'error_file']},
    }

    logging.config.dictConfig(logging_config)
