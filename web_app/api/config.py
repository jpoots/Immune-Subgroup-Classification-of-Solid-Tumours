from flask import Flask, render_template, request, session, redirect
from flask_session import Session
import joblib
from flask_cors import CORS
from middleware import read_data, validate_data

app = Flask(__name__)
app.secret_key = "SECRET"

app.config['SESSION_TYPE'] = "filesystem"
Session(app)
#app.config['SESSION_PERMANENT'] = False
#app.config['SESSION_USE_SIGNER'] = True
#app.config['SESSION_REDIS'] = redis.from_url('redis://127.0.0.1:6379')

CORS(app)
model = joblib.load("model.pkl")
bootstrap_models = joblib.load("bootstrap_models.pkl")

#app.before_request(validate_data)
#app.before_request(read_data)
