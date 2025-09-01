from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key = True)
    full_name = db.Column(db.String, nullable = False)
    email = db.Column(db.String, nullable = False, unique = True)
    phone_no = db.Column(db.Integer, nullable = False, unique = True, )
    password = db.Column(db.String, nullable = False, unique = True)
    role = db.Column(db.String, default = "user")
    #Relationship to Reserve_parking_spots
    reserve_parking_spot_user = db.relationship('Reserve_parking_spot', back_populates = 'user_rel')
    #Relationship to Parking_lots
    parking_lots = db.relationship('Parking_lot', back_populates = 'user_rel')


class Parking_lot(db.Model):
    __tablename__ = 'Parking_lots'
    id = db.Column(db.Integer, primary_key = True)
    location = db.Column(db.String, nullable = False)
    price = db.Column(db.Integer, nullable = False)
    address = db.Column(db.String, nullable = False)
    pin_code = db.Column(db.Integer, nullable = False)
    max_spots = db.Column(db.Integer, nullable = False)
    unique_lot_code = db.Column(db.String, nullable = False, unique = True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))

    #Relationship to parking_spots
    spots=db.relationship('Parking_spot', back_populates = 'rel_to_parking_lot')
    #Relationship to users
    user_rel = db.relationship('User', back_populates = 'parking_lots')

class Parking_spot(db.Model):
    __tablename__ = 'Parking_spots'
    id = db.Column(db.Integer, primary_key = True)
    lot_id = db.Column(db.Integer, db.ForeignKey('Parking_lots.id'), nullable = False)
    status = db.Column(db.String, default="Available")

    #Relationship to parking_lot
    rel_to_parking_lot = db.relationship('Parking_lot', back_populates = 'spots')

    #Relationship to Reserve_parking_spot
    reserve_spot=db.relationship('Reserve_parking_spot', back_populates = 'rel_to_parking_spot')
    
class Reserve_parking_spot(db.Model):
    __tablename__ = 'Reserve_parking_spots'
    id = db.Column(db.Integer, primary_key = True)
    spot_id = db.Column(db.Integer, db.ForeignKey('Parking_spots.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    in_time = db.Column(db.DateTime, nullable = False)
    out_time = db.Column(db.DateTime, nullable = False)
    parking_cost = db.Column(db.Integer, nullable = False)
    car_type = db.Column(db.String, nullable = False)
    vehicle_no = db.Column(db.String, nullable = False)
    
    #Relationship to parking_spot 
    rel_to_parking_spot = db.relationship('Parking_spot', back_populates = 'reserve_spot')

    #Relationship to users
    user_rel = db.relationship('User', back_populates = 'reserve_parking_spot_user')

class ParkingHistory(db.Model):
    __tablename__ = 'Parking_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    spot_id = db.Column(db.Integer, nullable=False)
    in_time = db.Column(db.DateTime, nullable=False)
    out_time = db.Column(db.DateTime, nullable=False)
    parking_cost = db.Column(db.Integer, nullable=False)
    car_type = db.Column(db.String, nullable=False)
    vehicle_no = db.Column(db.String, nullable=False)
    lot_name = db.Column(db.String, nullable=False)

    #Relationship to users
    user = db.relationship('User', backref='parking_histories')
    #Relationship to parking_spot
    #spot = db.relationship('Parking_spot', backref='parking_histories')