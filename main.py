import flask as fk
from flask import render_template
import re
import logging
import sqlite3


values = {"club_name":"", "sponsor":"", "days":"", "time":"", "location":"", "category":"", "e":""}

app = fk.Flask(
    __name__,
    static_folder="stylesheets",
    template_folder="templates",
)

def escape_html(s):
  return html.escape(s)

def get_connection():
  connection = sqlite3.connect("blogbosts.db")
  return connection

def get_clubs():
  connection = get_connection()
  cursor = connection.cursor()
  cursor.execute("SELECT * FROM clubs")
  clubs = cursor.fetchall()
  return clubs 

def create_new_club():
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute("INSERT INTO posts (club_name, sponsor, days, time, location, category) VALUES (?, ?, ?, ?, ?, ?)", (values["club_name"], values["sponsor"], values["days"], values["time"], values["location"], values["category"] ))
    connection.commit()

@app.route('/', methods=["GET"])
@app.route('/clubs', methods=["GET"],strict_slashes=False)
def root():
  with sqlite3.connect("clubs.db") as con:
    cursor = con.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS clubs (name TEXT, sponsor TEXT, days TEXT, meetingTime TEXT, location TEXT, categories TEXT)")
    cursor.execute("SELECT * FROM clubs")
  return fk.render_template("home.html")

@app.route('/addclub', methods=["GET", "POST"])
def add_club():
  method = fk.request.method
  if method=="POST":
    values['club_name'] = escape_html(fk.request.form['name'])
    values['sponsor'] = escape_html(fk.request.form['sponsor'])
    
    
  return fk.render_template("addclub.html")



app.run(host='0.0.0.0', port='3000')