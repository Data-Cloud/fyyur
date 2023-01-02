#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from turtle import done
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from email.policy import default
from sqlalchemy import null
from forms import *
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import aliased
import collections 
collections.Callable = collections.abc.Callable
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120), default=' ')
    website_link = db.Column(db.String(120))
    shows = db.relationship("Shows", backref="Artist", lazy='dynamic')

class Shows(db.Model):
  __tablename__ = 'Shows' 
  id = db.Column(db.Integer,primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"),nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"),nullable=False)
  start_time = db.Column(db.DateTime,nullable=False)
  artist = db.relationship('Artist', backref='Show', lazy=True)
  venue = db.relationship('Venue', backref='Show', lazy=True)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = []
  places = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()  
  for city_state in places:
    city = city_state[0]
    state = city_state[1]
    venues = Venue.query.filter_by(city=city, state=state).all()   
    data.append({
      "city": city,
      "state": state,
      "venues": venues
      })
  return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  #done
  venues = Venue.query.filter(Venue.name.ilike('%' + request.form.get('search_term', '') + '%'))
  data = []
  
  for venue in venues:
    data.append({
      "id": venue.id,
      "name": venue.name,
    })
  
  response = {
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  print(venue.id)
  current_t = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  past_shows = Shows.query.join(Venue).filter(Shows.venue_id == venue_id).filter(Shows.start_time < current_t).all()
  upcoming_shows = Shows.query.join(Venue).filter(Shows.venue_id == venue_id).filter(Shows.start_time > current_t).all()
  data = []
  
  past_shows_data = []
  future_shows_data = []
  if len(past_shows) == 0: 
     past_shows_data = []
  else:
    for item in past_shows:
      past_shows_data.append({
        "artist_id": item.artist_id,
        "artist_name": item.Artist.name,
        "artist_image_link":item.Artist.image_link,
        "start_time": item.start_time
      })
      
  if len(upcoming_shows) <= 0: 
     future_shows_data = []
  else:
    for item in upcoming_shows:
      future_shows_data.append({
        "artist_id": item.artist_id,
        "artist_name": item.Artist.name,
        "artist_image_link":item.Artist.image_link,
        "start_time": item.start_time
      })
  # for item in venues:
  data.append({
    "id": venue.id,
    "name": venue.name, 
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website_link": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows_data,
    "upcoming_shows": future_shows_data,
    "past_shows_count": len(past_shows_data),
    "upcoming_shows_count": len(future_shows_data),
  })
  print(data)
  return render_template('pages/show_venue.html', venue=data[0])

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # done
  try: 
    venue = Venue(
      name = request.form['name'],
      city = request.form['city'],
      state = request.form['state'],
      address = request.form['address'],
      phone = request.form['phone'],
      genres = request.form.getlist('genres'),
      image_link = request.form['image_link'],
      facebook_link = request.form['facebook_link'],
      website_link = request.form['website_link'],
      seeking_talent = True if 'seeking_talent' in request.form else False, 
      seeking_description = request.form['seeking_description']
      )
    
    db.session.add(venue)
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
  finally: 
    db.session.close()
  if error: 
    flash('An error occurred. Venue ' + request.form['name']+ ' could not be listed.')
  if not error: 
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  data = []
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name,
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  artists = Artist.query.filter(Artist.name.ilike('%' + request.form.get('search_term', '') + '%'))
  data = []
  
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name,
    })
  
  response = {
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  current_t = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  data = []
  past_shows_data = []
  future_shows_data = []
  
  artist = Artist.query.get(artist_id)
  print(artist.id)

  past_shows = Shows.query.join(Artist).filter(Shows.artist_id == artist_id).filter(Shows.start_time < current_t).all()
  coming_shows = Shows.query.join(Artist).filter(Shows.artist_id == artist_id).filter(Shows.start_time > current_t).all()
  
  if len(past_shows) == 0: 
     past_shows_data = []
  else:
    for item in past_shows:
      past_shows_data.append({
        "artist_id": item.artist_id,
        "artist_name": item.Artist.name,
        "artist_image_link":item.Artist.image_link,
        "start_time": item.start_time
      })
      
  if len(coming_shows) < 1: 
     future_shows_data = []
  else:
    for item in coming_shows:
      future_shows_data.append({
        "artist_id": item.artist_id,
        "artist_name": item.Artist.name,
        "artist_image_link":item.Artist.image_link,
        "start_time": item.start_time
      })

  data.append({
    "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": coming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(coming_shows),
  })
  print(data)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)  
  artist={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website_link": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  artist = Artist.query.get(artist_id)
  
  if 'seeking_venue' in request.form:
    if request.form['seeking_venue'] == 'y': 
      seeking_venue = True
  else:
    seeking_venue = False
  
  print(artist)
  try:
      artist.name = request.form['name']
      artist.city = request.form['city']
      artist.state = request.form['state']
      artist.phone = request.form['phone']
      artist.genres = request.form.getlist('genres')
      artist.image_link = request.form['image_link']
      artist.facebook_link = request.form['facebook_link']
      artist.seeking_venue = seeking_venue
      artist.seeking_description = request.form['seeking_description']
      artist.website_link = request.form['website_link']
      
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + artist.name + ' was successfully updated!')
  except:
      flash('Something went wrong, Artist ' + artist.name + ' was not updated')
      db.session.rollback()
      db.session.close()
  finally:
    db.session.close()
  
  print(artist)
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  
  if 'seeking_talent' in request.form:
    if request.form['seeking_talent'] == 'y': 
      seeking_talent = True
  else:
    seeking_talent = False
  
  print(venue)
  try:
      venue.name = request.form['name']
      venue.city = request.form['city']
      venue.state = request.form['state']
      venue.address = request.form['address']
      venue.phone = request.form['phone']
      venue.genres = request.form.getlist('genres')
      venue.image_link = request.form['image_link']
      venue.facebook_link = request.form['facebook_link']
      venue.website_link = request.form['website_link']
      venue.seeking_talent = seeking_talent
      venue.seeking_description = request.form['seeking_description']
      
      db.session.add(venue)
      db.session.commit()
      flash('venue ' + venue.name + ' was successfully updated!')
  except:
      flash('Something went wrong, venue ' + venue.name + ' was not updated')
      db.session.rollback()
      db.session.close()
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/<int:artist_id>/create', methods=['POST'])
def create_artist_submission(artist_id):
  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  try:
    new_artist = Artist(
      name=request.form['name'],
      genres=request.form.getlist('genres'),
      city=request.form['city'],
      state=request.form['state'],
      phone=request.form['phone'],
      website_link=request.form['website_link'],
      image_link=request.form['facebook_link'],
      facebook_link=request.form['facebook_link'],
      seeking_venue=True if 'seeking_venue' in request.form else False,
      seeking_description=request.form['seeking_description'],
  )
    
    db.session.add(new_artist)
    db.session.commit()
    
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + 'could not be listed. ')
    print(sys.exc_info())
  finally:
    db.session.close()
  # DONE : on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return redirect(url_for('show_artist', artist_id=artist_id))
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  
  shows = Shows.query.join(Venue).filter(Shows.venue_id == Venue.id).join(Artist).filter(Shows.artist_id == Artist.id).all()
  data = []
  print(shows)
  if len(shows) == 0: 
    flash('No Show currently listed!')
    return render_template('pages/shows.html')
  else:
    for show in shows: 
      data.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time
      })
  print(data)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    venue_id = request.form['venue_id']
    artist_id = request.form['artist_id']
    start_time = request.form['start_time']
    
    new_show = Shows(venue_id=venue_id,artist_id=artist_id,start_time=str(start_time))
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
  
  except:
    print(sys.exc_info())
    flash('Sorry show could not be listed!')
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
