from app import db
from sqlalchemy import UniqueConstraint, distinct
from datetime import datetime


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    shows = db.relationship('Show', backref='Venue', lazy=True, cascade='all, delete-orphan')
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(800))
    website_link = db.Column(db.String(120))
    UniqueConstraint('name', 'city', 'state', 'address', name='unique_name_city_state_address')
    
    @property 
    def upcoming_shows(self):
      upcoming_shows = [show for show in self.shows if show.start_time > datetime.now()] #datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S') > now]
      return upcoming_shows
    
    @property
    def num_upcoming_shows(self):
      return len(self.upcoming_shows)
    
    @property
    def past_shows(self):
      past_shows = [show for show in self.shows if show.start_time < datetime.now()]
      return past_shows
    
    @property
    def num_past_shows(self):
      return len(self.past_shows)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(500), nullable=True)
    shows = db.relationship('Show', backref='Artist', lazy=True)
    
    @property
    def upcoming_shows(self):
      upcoming_shows = [show for show in self.shows if show.start_time > datetime.now()]
      return upcoming_shows
      
    @property
    def num_upcoming_shows(self):      
      return len(self.upcoming_shows)
        
    @property
    def past_shows(self):
      past_shows = [show for show in self.shows if show.start_time < datetime.now()]
      
      return past_shows
      
    @property
    def num_past_shows(self):
      return len(self.past_shows)
    
    
class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
