import os
from dotenv import load_dotenv

load_dotenv()

API_PORT = int(os.getenv("API_PORT", 3000))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", 1)
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_APP = os.getenv("FLASK_APP", "sentiment-analysis")

# CONSUMER_KEY = os.getenv('CONSUMER_KEY')
# CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
# ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
# ACCESS_SECRET = os.getenv('ACCESS_SECRET')