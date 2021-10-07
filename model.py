from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
from flask import Flask, flash, jsonify, redirect, render_template, request, session

app = Flask(__name__)
db = SQLAlchemy(app)

class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    email = db.Column(db.String())
    dob = db.Column(db.String())
    password = db.Column(db.String())
    username = db.Column(db.String())

    def __init__(self, name, username, email, dob, password):
        self.name = name
        self.username = username
        self.email = email
        self.dob = dob
        self.password = password


class PostModel(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.Integer())
    content = db.Column(db.String())
    time = db.Column(db.String())

    def __init__(self, owner, content, time):
        self.owner = owner
        self.content = content
        self.time = time

class TagModel(db.Model):
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String())
    user = db.Column(db.Integer())
    tagpost = db.Column(db.Integer())
    time = db.Column(db.String())

    def __init__(self, tag, user, tagpost, time):
        self.tag = tag
        self.user = user
        self.tagpost = tagpost
        self.time = time

class FollowModel(db.Model):
    __tablename__ = 'follow'

    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer())
    follow_id = db.Column(db.Integer())
    value = db.Column(db.Integer())

    def __init__(self, person, following, value):
        self.person_id = person
        self.follow_id = following
        self.value = value

class LikeModel(db.Model):
    __tablename__ = 'like'

    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.Integer())
    post_id = db.Column(db.Integer())
    value = db.Column(db.Integer())

    def __init__(self, person, post, value):
        self.owner = person
        self.post_id = post
        self.value = value