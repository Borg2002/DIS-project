from flask import Flask, render_template
from database import init_db
init_db()
from controllers import update_controller
import random as rnd

"""
Step by step guide: https://github.com/rafaelcgs10/dis2025

url: http://127.0.0.1:5000/

Commands (windows): 
Set-ExecutionPolicy Unrestricted -Scope Process
.venv\Scripts\activate
flask run --debug

Commands (mac)
. .venv/bin/activate
flask run --debug

"""

app = Flask(__name__)

@app.route("/")
def hello_world():
    template = update_controller.update()
    return template #render_template("index.html", question="", answer="")

app.register_blueprint(update_controller.bp)


