import flask as fk
from flask import render_template, redirect
import re
import logging
import html
import sqlite3
from flask_wtf import Form, FlaskForm
from wtforms import (StringField, TextAreaField, IntegerField, BooleanField, RadioField, SelectField, SelectMultipleField)
from wtforms import widgets
from wtforms.validators import InputRequired, Length, StopValidation

logging.basicConfig(level=logging.DEBUG)

def get_tags():
  return [(1, 'Academic'), (2, 'Arts & Humanities'), (3, 'Competition-based'), (4, 'Community Service'), (5, 'Cultural'), (6, 'Gaming'), (7, 'Leadership'), (8, 'Science & Technology'), (9, 'Sports')]

class MultiCheckboxField(SelectMultipleField):
  widget = widgets.ListWidget(html_tag='ul', prefix_label=False)
  option_widget = widgets.CheckboxInput()

class MultiCheckboxAtLeastOne():
  def __init__(self, message=None):
      if not message:
          message = 'At least one option must be selected'
      self.message = message

  def __call__(self, form, field):
      if not field.data:
          raise StopValidation(self.message)

class ClubForm(FlaskForm):
  name = StringField('Club Name', validators=[InputRequired(message = "Please enter a club name")])
  sponsor = StringField('Sponsor',
validators=[InputRequired(message = "Please enter a sponsor name")])
  days = MultiCheckboxField('Meeting Days', 
                          choices = [(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday')], 
                          validators=[MultiCheckboxAtLeastOne(message="Please choose at least one day")], coerce=int)
  time = SelectField('Meeting Times', 
                   choices=[('BeforeSchool', 'Before School'),('Lunch', 'Lunch'), ('AfterSchool', 'After School'), ('Other','Other')],  
                   validators=[InputRequired("Please select a time")])
  location = StringField('Meeting Location',
validators=[InputRequired(message = "Please enter a location")])
  tags = MultiCheckboxField('Club Tags', 
choices = get_tags(), 
validators=[MultiCheckboxAtLeastOne(message = "Please check at least one category")], coerce=int)
  contact = StringField('Contact Information',
validators=[InputRequired(message = "Please enter a contact")])
  description = TextAreaField('Club Description (max 150 characters)',
validators=[InputRequired(message = "Please enter a club description"), Length(max=150, message = "Description is over 150 characters")])

app = fk.Flask(
    __name__,
    static_folder="stylesheets",
    template_folder="templates",
)
app.config["WTF_CSRF_ENABLED"] = False

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
  form = ClubForm()
  if method == "POST":
    if form.validate():
      logging.info("GOOD")
      # ADD CLUB TO SQL
      return(redirect('/submit', code=308))
    else:
      logging.info("BAD")
      logging.info(form.errors)
      return fk.render_template("addclub.html", form=form)
  else:
    return fk.render_template("addclub.html", form=form)

@app.route('/submit', methods=['POST'])
def submit_success():
  return(fk.render_template("success.html"))


app.run(host='0.0.0.0', port='3000')