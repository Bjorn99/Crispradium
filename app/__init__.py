from flask import Flask, render_template, request
from app.sequence_handler import SequenceHandler


app = Flask(__name__)
app.config.from_object('config')

from app import routes