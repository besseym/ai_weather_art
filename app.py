from dotenv import load_dotenv
from flask import Flask

load_dotenv()

app = Flask(__name__)

from weather_art.routes import bp  # noqa: E402

app.register_blueprint(bp)

if __name__ == "__main__":
    app.run()