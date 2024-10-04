from os import getenv
from flask import Flask

app = Flask(__name__, template_folder="frontend/templates")
app.secret_key = getenv("SECRET_KEY")

from backend import routes

if __name__ == "__main__":
    app.run(debug=True)
