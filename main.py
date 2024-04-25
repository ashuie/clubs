import flask as fk
from flask import render_template
import re
import logging
import sqlite3

app = fk.Flask(
    __name__,
    static_folder="stylesheets",
    template_folder="templates",
)

@app.route('/', methods=["GET"])
@app.route('/clubs', methods=["GET"],strict_slashes=False)
def root():
  return fk.render_template("home.html")

@app.route('/addclub', methods=["GET"])
def add_club():
  return fk.render_template("addclub.html")


app.run(host='0.0.0.0', port='3000')