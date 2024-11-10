from flask import Flask
from app.sequence_handler import SequenceHandler
from app.guide_rna_analyzer import GuideRNAAnalyzer
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret_key')

# Initialize core services
sequence_handler = SequenceHandler()
guide_rna_analyzer = GuideRNAAnalyzer()

from app import routes