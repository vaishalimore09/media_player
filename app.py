# app.py

from flask import Flask
from flask_cors import CORS
from routes import media_playback, search, highlight

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(media_playback)
app.register_blueprint(search)
app.register_blueprint(highlight)


if __name__ == '__main__':
    app.run(debug=True)
