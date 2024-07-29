from flask import Flask
from useless_flask.views import *

app = Flask(__name__)
app.register_blueprint(views, url_prefix="/views")

if __name__ == "__main__":
    app.run(debug=True, port=8000)
