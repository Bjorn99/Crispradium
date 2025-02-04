import os
from pathlib import Path
from typing import Dict, Any


class Config:

    """
    Look, I've been learning computational biology for a while and I don't think
    I will ever finish learning it. However, configuration is always a pain.
    This setup lets us handle different environments (dev/prod) and keep our
    parameters organized. On the plus side, it's easier to updae when new CRISPR
    systems come out - oh, trust me, they will.
    """


    # Base directory
    BASE_DIR = Path(__file__).parent.parent.absolute()

    # Flask stuff - basic but necessary
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my-secret-key-for-dev'
    DEBUG = os.environ.get('FLASK_ENV') == 'development'

    # File upload config - keeping it reasonable
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16MB max file size
    ALLOWED_EXTENSIONS = {'txt', 'fasta', 'fa', 'seq'}
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

    # Analysis parameters
    MIN_SEQUENCE_LENGTH = 20
    MAX_SEQUENCE_LENGTH = 200000  # 200kb should cover most use cases
    CACHE_TIMEOUT = 3600  # 1 hour

    # Scoring weights
    SCORING_WEIGHTS = {
        'gc_content': 0.3,
        'secondary_structure': 0.3,
        'off_target': 0.4
    }

    # RNA folding parameters - don't mess with these unless you know what you're doing
    RNA_FOLDING = {
        'temperature': 37.0,  # Celsius
        'max_loop_length': 30,
        'max_bp_span': 100
    }


    @staticmethod
    def init_app(app):
        """
        Initialize the app with this config. Also creates necessary directories
        because I'm tired of seeing those FileNotFoundError exceptions.
        """
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        # Set some sane defaults for production
        if not Config.DEBUG:
            Config.CACHE_TIMEOUT = 7200  # 2 hours in prod
            Config.MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB in prod


class DevelopmentConfig(Config):
    """
    Dev config - more logging, shorter timeouts, smaller file sizes
    """
    DEBUG = True
    CACHE_TIMEOUT = 300  # 5 minutes
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8MB


class ProductionConfig(Config):
    """
    Prod config - stricter security, longer cache times
    """
    DEBUG = False
    CACHE_TIMEOUT = 7200  # 2 hours
    
    # Override this in environment!
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'seriously-change-this-in-prod'
    
    # Tighter security settings
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True


class TestingConfig(Config):
    """
    Testing config - quick timeouts, smaller files, test folders
    """
    TESTING = True
    CACHE_TIMEOUT = 60  # 1 minute
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1MB
    UPLOAD_FOLDER = os.path.join(Config.BASE_DIR, 'test_uploads')


# Easy access to configs - I use this pattern in all my projects
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config() -> Config:
    """Get the current config based on environment"""
    config_name = os.environ.get('FLASK_ENV') or 'default'
    return config.get(config_name, config['default'])