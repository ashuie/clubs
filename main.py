import flask as fk
from flask import render_template, redirect
import re
import logging
import html
import sqlite3
from flask_wtf import Form, FlaskForm
from wtforms import (StringField, TextAreaField,  SelectField, SelectMultipleField)
from wtforms import widgets
from wtforms.validators import InputRequired, Length, StopValidation

logging.basicConfig(level=logging.DEBUG)
global db_file
db_file = "clubs/clubs.db"

weekdays = { 1 : 'Monday', 2 :'Tuesday', 3 : 'Wednesday', 4 :'Thursday'}
tags_list = {1 : 'Academic', 2 : 'Arts & Humanities', 3 : 'Competition-based', 4 : 'Community Service', 5 : 'Cultural', 6 : 'Gaming', 7 : 'Leadership', 8 : 'Science & Technology', 9 :  'Sports'}

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
                   choices=[('Before School', 'Before School'),('Lunch', 'Lunch'), ('After School', 'After School'), ('Other','Other')],  
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

def dict_factory(cursor, row):
  d = {}
  for index, col in enumerate(cursor.description):
      d[col[0]] = row[index]
  return d

def get_connection():
  connection = sqlite3.connect("clubs/clubs.db")
  connection.row_factory = dict_factory
  return connection

def get_clubs():
  with get_connection() as con:
    cursor = con.cursor()
    clubs = cursor.execute("SELECT * FROM clubs")
    logging.info(clubs)
    return clubs 

def string_convert(dict, list):
  s = ""
  for i in range(len(list) - 1):
    s += dict[list[i]] + ", "
  s += dict[list[len(list)-1]]
  return s
  
def create_new_club(form):
  with get_connection() as connection:
    cursor = connection.cursor()
    # ADD TO SQL WITH WTFORM
    logging.info(form.tags.data)
    logging.info(string_convert(tags_list, form.tags.data))
    cursor.execute("INSERT INTO clubs (name, sponsor, days, time, location, category, contact, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (str(form.name.data), str(form.sponsor.data), string_convert(weekdays, form.days.data), str(form.time.data), str(form.location.data), string_convert(tags_list, form.tags.data), str(form.contact.data), str(form.description.data)))
    connection.commit()

def load_clubs(clubs):
  return fk.render_template("home.html", clubs=clubs)

@app.route('/', methods=["GET"])
@app.route('/clubs', methods=["GET"],strict_slashes=False)
def root():
  with sqlite3.connect("clubs/clubs.db") as con:
    cursor = con.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS clubs (name TEXT, sponsor TEXT, days TEXT, time TEXT, location TEXT, category TEXT, contact TEXT, description TEXT)")
    clubs = cursor.execute("SELECT * FROM clubs")
    return load_clubs(get_clubs())

@app.route('/addclub', methods=["GET", "POST"])
def add_club():
  method = fk.request.method
  form = ClubForm()
  if method == "POST":
    if form.validate():
      logging.info("GOOD")
      # ADD CLUB TO SQL
      create_new_club(form)
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