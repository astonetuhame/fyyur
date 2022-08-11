#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from models import *
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from markupsafe import Markup
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.types import ARRAY
from flask_migrate import Migrate
from sqlalchemy import distinct
from sqlalchemy.exc import SQLAlchemyError
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

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

# Venue View
@app.route('/venues')
def venues():
    data = []
    unique_city_state = Venue.query.with_entities(
        Venue.city, Venue.state).distinct().all()
    for city_state in unique_city_state:
        city = city_state[0]
        state = city_state[1]
        venues = Venue.query.filter_by(city=city, state=state).all()
        shows = venues[0].upcoming_shows
        data.append({
            "city": city,
            "state": state,
            "venues": venues
        })

    return render_template('pages/venues.html', areas=data)

# Venue Search


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%'))
    data = []
    for venue in venues:
        data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": venue.num_upcoming_shows
        })
    count = len(data)
    response = {
        "count": count,
        "data": data
    }

    return render_template('pages/search_venues.html', results=response, search_term=search_term)

# Venue View Specific


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    if venue:
        data = {
            "id": venue.id,
            "name": venue.name,
            "genres": venue.genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website_link": venue.website_link,
            "facebook_link": venue.facebook_link,
            "seeking_talent": True if venue.seeking_talent in (True, 't', 'True') else False,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link if venue.image_link else "",
            "past_shows_count": venue.num_past_shows,
            "upcoming_shows_count": venue.num_upcoming_shows,
        }

    past_shows = []
    for show in venue.past_shows:
        artist = Artist.query.get(show.artist_id)
        past_shows.append({
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.start_time)
        })

    upcoming_shows = []
    for show in venue.upcoming_shows:
        artist = Artist.query.get(show.artist_id)
        upcoming_shows.append({
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.start_time)
        })

    data["past_shows"] = past_shows
    data["upcoming_shows"] = upcoming_shows

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue GET


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

#  Create Venue


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    venue = Venue()
    for field in request.form:
        if field == 'genres':
            setattr(venue, field, request.form.getlist(field))
        elif field == 'seeking_talent':
            setattr(venue, field, True if request.form.get(
                field) in ('y', True, 't', 'True') else False)
        else:
            setattr(venue, field, request.form.get(field))

    try:
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        flash('An error occurred. Show could not be listed. \n' + error)
        db.session.rollback()
        flash('An error occurred. Venue ' +
              venue.name + ' could not be listed.')
        return render_template('pages/home.html')

    finally:
        db.session.close()

    return redirect(url_for('venues'))

# Update Venue (GET)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)

    return render_template('forms/edit_venue.html', form=form, venue=venue)

# Update Venue (POST)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue_id)
    for field in request.form:
        if field == 'genres':
            setattr(venue, field, request.form.getlist(field))
        elif field == 'seeking_talent':
            setattr(venue, field, True if request.form.get(
                field) in ('y', True, 't', 'True') else False)
        else:
            setattr(venue, field, request.form.get(field))
    try:
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        flash('An error occurred. Show could not be listed. \n' + error)
        db.session.rollback()
        flash('An error occurred. Venue ' +
              venue.name + ' could not be listed.')
        return render_template('pages/home.html')

    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

# Delete Venue


@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
    venue = Venue.query.get(venue_id)
    try:
        # venue.delete()
        db.session.delete(venue)
        db.session.commit()
        flash('Venue ' + venue.name + ' was successfully deleted!')

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        flash('An error occurred. Venue ' +
              venue.name + ' could not be deleted.')
        db.session.rollback()
        return None

    finally:
        db.session.close()

    return None  # render_template('pages/home.html')


#  Artists
#  ----------------------------------------------------------------

#  Show artists
@app.route('/artists')
def artists():
    artists = Artist.query.with_entities(Artist.id, Artist.name).all()
    return render_template('pages/artists.html', artists=artists)

# Search Artists


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    artists = Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()
    data = []
    artist_count = len(artists)
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": artist.num_upcoming_shows
        })

    response = {
        "count": artist_count,
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=search_term)

# View specific artist


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    artist = Artist.query.get(artist_id)
    past_shows = []
    for show in artist.past_shows:
        venue = Venue.query.get(show.venue_id)
        past_shows.append({
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time
        })
    upcoming_shows = []
    for show in artist.upcoming_shows:
        venue = Venue.query.get(show.venue_id)
        upcoming_shows.append({
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time
        })
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "seeking_venue": True if artist.seeking_venue in ('y', True, 't', 'True') else False,
        "seeking_description": artist.seeking_description,
        # "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "image_link": artist.image_link,
        "facebook_link": artist.facebook_link,
        "website_link": artist.website_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": artist.num_past_shows,
        "upcoming_shows_count": artist.num_upcoming_shows
    }

    return render_template('pages/show_artist.html', artist=data)

# Update Artist (GET)


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)

    return render_template('forms/edit_artist.html', form=form, artist=artist)

# Update Artist (POST)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.get(artist_id)
    for field in request.form:
        if field == 'genres':
            setattr(artist, field, request.form.getlist(field))
        elif field == 'seeking_venue':
            setattr(artist, field, True if request.form.get(
                field) in ('y', True, 't', 'True') else False)
        else:
            setattr(artist, field, request.form.get(field))

    try:
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')

    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        flash('An error occurred. Artist ' +
              artist.name + ' could not be listed.')
        db.session.rollback()
        db.session.close()
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))

    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real shows data.
    data = [{
        "venue_id": 1,
        "venue_name": "The Musical Hop",
        "artist_id": 4,
        "artist_name": "Guns N Petals",
        "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "start_time": "2019-05-21T21:30:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 5,
        "artist_name": "Matt Quevedo",
        "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        "start_time": "2019-06-15T23:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-01T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-08T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-15T20:00:00.000Z"
    }]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
