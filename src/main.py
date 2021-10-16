from app import app
from config import API_PORT, FLASK_DEBUG, FLASK_HOST
import routes.root

if __name__ == '__main__':
    app.run(host=FLASK_HOST, port=API_PORT, debug=FLASK_DEBUG)