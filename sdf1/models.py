from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# 1. Kateqoriyalar Cədvəli
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    events = db.relationship('Event', backref='category', lazy=True)

# 2. Tədbirlər Cədvəli
class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    date = db.Column(db.String(50), nullable=False)  # Məsələn: YYYY-MM-DD
    time = db.Column(db.String(50), nullable=False)  # Məsələn: HH:MM
    location = db.Column(db.String(150), nullable=False)
    max_participants = db.Column(db.Integer, nullable=False)
    registrations = db.relationship('Registration', backref='event', lazy=True, cascade='all, delete-orphan')

# 3. İstifadəçilər Cədvəli
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    registrations = db.relationship('Registration', backref='user', lazy=True, cascade='all, delete-orphan')

# 4. Qeydiyyatlar Cədvəli (Eyni istifadəçinin təkrar qeydiyyatının qarşısını almaq üçün UniqueConstraint)
class Registration(db.Model):
    __tablename__ = 'registrations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'event_id', name='_user_event_uc'),
    )