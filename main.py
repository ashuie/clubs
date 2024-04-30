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

def get_connection():
  connection = sqlite3.connect("blogbosts.db")
  return connection

def get_clubs():
  connection = get_connection()
  cursor = connection.cursor()
  cursor.execute("SELECT * FROM clubs")
  clubs = cursor.fetchall()
  return clubs 

@app.route('/', methods=["GET"])
@app.route('/clubs', methods=["GET"],strict_slashes=False)
def root():
  with sqlite3.connect("clubs.db") as con:
    cursor = con.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS clubs (name TEXT, description TEXT, date TEXT, categories TEXT)")
    cursor.execute("SELECT * FROM clubs")
  return fk.render_template("home.html")

@app.route('/addclub', methods=["GET"])
def add_club():
  return fk.render_template("addclub.html")



app.run(host='0.0.0.0', port='3000')