from flask import Flask, render_template, request
from app.sequence_handler import SequenceHandler
import os


app = Flask(__name__)
#app.config.from_object('config')
# Configure the application with environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_default_secret_key')  # Fallback to a default if not set
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL', 'sqlite:///default.db')  # Default SQLite database
app.config['API_KEY'] = os.getenv('API_KEY', 'your_default_api_key')  # Fallback for API key


from app import routes