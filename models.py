from flask_login import UserMixin
from sqlalchemy import ForeignKey

from app import db

# UserMixin allows us to create a database model that can interact with flask-login
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    uid = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(80), unique=True, nullable=False)
    lname = db.Column(db.String(80), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_dev = db.Column(db.Boolean, default=False)

    builds = db.relationship('Build', backref='user', lazy=True)

    def __init__(self, fname, lname, username, password_hash, is_dev=False):
        self.fname = fname
        self.lname = lname
        self.username = username
        self.password_hash = password_hash
        self.is_dev = is_dev

    def __repr__(self):
        return f'User with username: {self.username}, developer: {self.is_dev}'

    def get_id(self):
        return self.uid

class Build(db.Model, UserMixin):
    __tablename__ = 'builds'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    description = db.Column(db.Text, unique=False, nullable=False)
    instructions = db.Column(db.Text, unique=False, nullable=False)
    link = db.Column(db.String(80), unique=False, nullable=False)
    developerID = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)

    def __init__(self, name, desc, instructions, link, devID):
        self.name = name
        self.description = desc
        self.instructions = instructions
        self.link = link
        self.developerID = devID