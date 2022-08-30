#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import flask
from models import *
import sys
import json
import dateutil.parser
import babel
from sqlalchemy import func
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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
    venues = Venue.query.order_by(Venue.state, Venue.city).all()

    data_list = []
    data_object = {}
    for venue in venues:
        venue_data = {
            'id': venue.id,
            'name': venue.name
        }

        data_object = {
          'city' : venue.city,
          'state' : venue.state,
          'venues' : [venue_data]
        }

        data_list.append(data_object)

    return render_template('pages/venues.html', areas=data_list)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search = request.form.get('search_term', '')
    returned_result = db.session.query(Venue).filter(
        Venue.name.ilike(f'%{search}%')).all()
    result_list = []

    for result in returned_result:
        result_list.append({
            "id": result.id,
            "name": result.name
        })

    data_object = {
        "count": len(returned_result),
        "data": result_list
    }
    return render_template('pages/search_venues.html', results=data_object, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

    venue = Venue.query.get(venue_id)
    error = False

    try: 
      upcoming_shows_list = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()
      upcoming_shows = []

      past_shows_list = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()
      past_shows = []

      for show in past_shows_list:
        past_shows.append({
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

      for show in upcoming_shows_list:
        upcoming_shows.append({
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
        })

      data_object = {
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link
      }
    except:
      error = True
      flash("There was an error completing this task!")
      return render_template('errors/404.html')

    return render_template('pages/show_venue.html', venue=data_object)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False

    try:
        form = VenueForm(request.form)
        if request.method == 'POST' and form.validate():
            data = Venue(name = form.name.data, city = form.city.data, state = form.state.data, address = form.address.data, 
            phone = form.phone.data, genres = form.genres.data, image_link = form.image_link.data, facebook_link = form.facebook_link.data, 
            website = form.website.data, seeking_talent = True if 'seeking_talent' in request.form else False, seeking_description = form.seeking_description.data)
            db.session.add(data)
            db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
    if not error:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    err = False

    try:
        to_delete = db.session.query(Venue).get(venue_id)
        db.session.delete(to_delete)
        db.session.commit()
    except:
        err = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if err:
        flash(f'An error occurred. Venue {venue_id} could not be deleted.')
    else:
        flash(f'Venue {venue_id} was successfully deleted.')

    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    data = db.session.query(Artist).all()

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    #Similar to search venues, same logic
    
    search = request.form.get('search_term', '')
    returned_result = db.session.query(Artist).filter(
        Artist.name.ilike(f'%{search}%')).all()
    result_list = []

    for result in returned_result:
        result_list.append({
            "id": result.id,
            "name": result.name
        })

    data_object = {
        "count": len(returned_result), #returned result should be a list
        "data": result_list
    }

    return render_template('pages/search_artists.html', results=data_object, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist_query = db.session.query(Artist).get(artist_id)

  if artist_query:
    get_past_shows = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()
    past_shows = []

    for show in get_past_shows:
        past_shows.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_image_link": show.venue.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    get_upcoming_shows = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()
    upcoming_shows = []

    for show in get_upcoming_shows:
        upcoming_shows.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_image_link": show.venue.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    data = {
        "id": artist_query.id,
        "name": artist_query.name,
        "genres": artist_query.genres,
        "city": artist_query.city,
        "state": artist_query.state,
        "phone": artist_query.phone,
        "website": artist_query.website,
        "facebook_link": artist_query.facebook_link,
        "seeking_venue": artist_query.seeking_venue,
        "seeking_description": artist_query.seeking_description,
        "image_link": artist_query.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
  else:
    return render_template('errors/404.html')

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    if artist:
        form.name.data = artist.name
        form.city.data = artist.city
        form.state.data = artist.state
        form.phone.data = artist.phone
        form.genres.data = artist.genres
        form.facebook_link.data = artist.facebook_link
        form.image_link.data = artist.image_link
        form.website.data = artist.website
        form.seeking_venue.data = artist.seeking_venue
        form.seeking_description.data = artist.seeking_description

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False

    if request.method == "POST":
      try:
          artist = db.session.query(Artist).get(artist_id)

          artist.name = request.form['name']
          artist.city = request.form['city']
          artist.state = request.form['state']
          artist.phone = request.form['phone']
          artist.genres = request.form.getlist('genres')
          artist.image_link = request.form['image_link']
          artist.facebook_link = request.form['facebook_link']
          artist.website = request.form['website']
          artist.seeking_venue = True if 'seeking_venue' in request.form else False
          artist.seeking_description = request.form['seeking_description']
          db.session.add(artist)
          db.session.commit()
      except:
          error = True
          db.session.rollback()
          print(sys.exc_info())
      finally:
          db.session.close()
    if error:
        flash('An error occurred. Artist could not be changed.')
    if not error:
        flash('Artist was successfully updated!')
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    if venue:
        form.name.data = venue.name
        form.city.data = venue.city
        form.state.data = venue.state
        form.phone.data = venue.phone
        form.address.data = venue.address
        form.genres.data = venue.genres
        form.facebook_link.data = venue.facebook_link
        form.image_link.data = venue.image_link
        form.website.data = venue.website
        form.seeking_talent.data = venue.seeking_talent
        form.seeking_description.data = venue.seeking_description

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False

    print(f'This is {venue_id}')

    if request.method == 'POST':
      try:
          venue = db.session.query(Venue).get(venue_id)

          venue.name = request.form['name']
          venue.city = request.form['city']
          venue.state = request.form['state']
          venue.address = request.form['address']
          venue.phone = request.form['phone']
          venue.genres = request.form.getlist('genres')
          venue.image_link = request.form['image_link']
          venue.facebook_link = request.form['facebook_link']
          venue.website = request.form['website']
          venue.seeking_talent = True if 'seeking_talent' in request.form else False
          venue.seeking_description = request.form['seeking_description']
          db.session.add(venue)
          db.session.commit()
      except:
          error = True
          db.session.rollback()
          print(sys.exc_info())
      finally:
          db.session.close()
    if error:
        flash(f'An error occurred. Venue could not be changed.')
    if not error:
        flash(f'Venue was successfully updated!')
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    try:
        form = ArtistForm(request.form)
        if request.method == 'POST' and form.validate():
            name = request.form['name']
            city = request.form['city']
            state = request.form['state']
            phone = request.form['phone']
            genres = request.form.getlist('genres'),
            facebook_link = request.form['facebook_link']
            image_link = request.form['image_link']
            website = request.form['website']
            seeking_venue = True if 'seeking_venue' in request.form else False
            seeking_description = request.form['seeking_description']

            data = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link,
                        image_link=image_link, website=website, seeking_venue=seeking_venue, seeking_description=seeking_description)
            db.session.add(data)
            db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
    if not error:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

    shows_query = db.session.query(Show).join(Artist).join(Venue).all()

    data = []
    for show in shows_query:
        data.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    try:
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']

        print(request.form)

        show = Show(artist_id=artist_id, venue_id=venue_id,
                    start_time=start_time)
        db.session.add(show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. ✖')
    if not error:
        flash('Success! ✔')
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
