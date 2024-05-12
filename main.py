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

weekdays_list = { 1 : 'Monday', 2 :'Tuesday', 3 : 'Wednesday', 4 :'Thursday'}
tags_list = {1 : 'Academic', 2 : 'Arts & Humanities', 3 : 'Competition-based', 4 : 'Community Service', 5 : 'Cultural', 6 : 'Gaming', 7 : 'Leadership', 8 : 'Science & Technology', 9 :  'Sports'}
times_list = {1: 'Before School', 2 : 'Lunch', 3 : 'After School'}
filter_list = { 1 : 'Monday', 2 : 'Tuesday', 3 : 'Wednesday', 4: 'Thursday', 5 : 'Academic', 6 : 'Arts & Humanities', 7 : 'Competition-based', 8 : 'Community Service', 9 : 'Cultural', 10 : 'Gaming', 11 : 'Leadership', 12 : 'Science & Technology', 13 :  'Sports'}


def get_tags():
  return [(1, 'Academic'), (2, 'Arts & Humanities'), (3, 'Competition-based'), (4, 'Community Service'), (5, 'Cultural'), (6, 'Gaming'), (7, 'Leadership'), (8, 'Science & Technology'), (9, 'Sports')]

def get_filters():
  return [(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Academic'), (6, 'Arts & Humanities'), (7, 'Competition-based'), (8, 'Community Service'), (9, 'Cultural'), (10, 'Gaming'), (11, 'Leadership'), (12, 'Science & Technology'), (13,  'Sports')]
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

class FilterForm(FlaskForm):
  days = MultiCheckboxField('', 
   choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday')])
  times = MultiCheckboxField('', 
     choices=[(1, 'Before School'), (2, 'Lunch'), (3, 'After School')])
  tags = MultiCheckboxField('', 
     choices=get_tags())

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
    return clubs 

def string_convert(dict, list):
  s = ""
  for i in range(len(list) - 1):
    s += dict[list[i]] + ", "
  s += dict[int(list[len(list)-1])]
  return s
  
def create_new_club(form):
  with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute("INSERT INTO clubs (url, name, sponsor, days, time, location, category, contact, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (str(form.name.data).replace(" ", ""), str(form.name.data), str(form.sponsor.data), string_convert(weekdays_list, form.days.data), str(form.time.data), str(form.location.data), string_convert(tags_list, form.tags.data), str(form.contact.data), str(form.description.data)))
    connection.commit()

def load_clubs(clubs, emptysearch, filter_form):
  return fk.render_template("home.html", clubs=clubs, emptysearch=emptysearch, filter_form=filter_form)

def get_clubs_by_filter(filter, column_name):
  logging.info(filter)
  searched_clubs = []
  with get_connection() as con:
    cursor = con.cursor()
    for tag in filter:
      clubs = cursor.execute("SELECT * FROM clubs WHERE " + column_name + " LIKE \'%" + tag + "%\'")
      searched_clubs.append(clubs.fetchall())
  logging.info(searched_clubs)
  return searched_clubs

# get_clubs_by_day

@app.route('/', methods=["GET", "POST"])
@app.route('/clubs', methods=["GET"],strict_slashes=False)
def root():
  filter_form = FilterForm()
  with sqlite3.connect("clubs/clubs.db") as con:
    cursor = con.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS clubs (url TEXT, name TEXT, sponsor TEXT, days TEXT, time TEXT, location TEXT, category TEXT, contact TEXT, description TEXT)")
    return load_clubs(get_clubs(), False, filter_form)

@app.route('/addclub', methods=["GET", "POST"])
def add_club():
  method = fk.request.method
  form = ClubForm()
  if method == "POST":
    if form.validate():
      logging.info("GOOD")
      create_new_club(form)
      return(redirect('/submit', code=308))
    else:
      logging.info("BAD")
      logging.info(form.errors)
      return fk.render_template("addclub.html", form=form)
  else:
    return fk.render_template("addclub.html", form=form)
    
@app.route('/search', methods=["GET", "POST"])
def search_by_query():
  filter_form = FilterForm()
  query = html.escape(fk.request.form["search-query"])
  empty = False
  if (len(query) > 0):
    with get_connection() as con:
      cursor = con.cursor()
      clubs = cursor.execute("SELECT * FROM clubs WHERE name LIKE \'%" + query + "%\' OR description LIKE \'%" + query + "%\'")
      all_clubs = clubs.fetchall()
      if (len(all_clubs) == 0):
        empty = True
      return load_clubs(all_clubs, empty, filter_form)
  else:
      return(redirect('/', code=308))

@app.route('/filter', methods=["GET", "POST"])
def filter_by_tags():
  filter_form = FilterForm()
  empty_search = False
  found_clubs = []
  if (len(filter_form.data) > 0):
    with get_connection() as con:
      cursor = con.cursor()
      
      #clubs = cursor.execute("SELECT * FROM clubs WHERE " + column_name + " LIKE \'%" + tag + "%\'")
        #found_clubs.append(clubs.fetchall())
      if (len(found_clubs) == 0): 
        empty_search = True
      else:
        found_clubs = list(set(found_clubs))
    return load_clubs(found_clubs, empty_search, filter_form)
  else:
    return(redirect('/', code=308))

@app.route('/submit', methods=['POST'])
def submit_success():
  return(fk.render_template("success.html"))

@app.route('/<club_name>', methods=["GET"])
def permapost(club_name):
  with get_connection() as con:
    cursor = con.cursor()
    s = cursor.execute("SELECT * FROM clubs WHERE url=?", (club_name, ))
    club = s.fetchone()
    return fk.render_template("clubpage.html", club=club)


  
app.run(host='0.0.0.0', port='3000')