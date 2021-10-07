import os
import re
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from util import *
from model import *
from datetime import datetime
import time

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Connect with Database
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://qtensxmkswtswf:02e819c7363c3ab94ad91e1e0deccf178119ce6dba3cc65a9c34cde980936c25@ec2-54-159-107-189.compute-1.amazonaws.com:5432/dc5tf4lgf0b892"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Forget any user_id
        session.clear()

        # Ensure username was submitted
        if not request.form.get("username"):
            flash(f"You must include Username", 'alert')
            return redirect('/login')

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash(f"You must include Password", 'alert')
            return redirect('/login')

        username = request.form.get("username")
        password = request.form.get("password")
        # Query database for username
        user = UserModel.query.filter_by(username=request.form.get("username")).first()

        # Ensure username exists and password is correct
        if user == None:
            flash(f"User not found", 'alert')
            return redirect("/login")

        if password != user.password:
            flash(f"Incorrect Password", 'alert')
            return redirect("/login")

        session["user_id"] = user.id
        session["email"] = user.email
        session["username"] = user.username
        # Redirect user to home page

        return redirect("/home")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        if session.get("user_id") is None:
            return render_template("login.html")
        else:
            session.clear()
            return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    else:
        if not request.form.get("username") or not request.form.get("name") or not request.form.get("date") or not request.form.get("password"):
            flash(f"Please input every information", 'alert')
            return redirect('/signup')
        email = request.form.get("email")
        email = UserModel.query.filter_by(email=email).first()
        if email != None:
            flash(f"You have been registered before. Please log in", 'alert')
            return redirect("/login")
        username = request.form.get("username")
        date = request.form.get("date")
        name = request.form.get("name")
        email = request.form.get("email")
        user = UserModel.query.filter_by(username=username).first()
        if user != None:
            flash(f"Username already exists. Please use another username", 'alert')
            return render_template("signup.html", date=date, name=name, username=username, email=email)
        password = request.form.get("password")

        new_user = UserModel(name, username, email, date, password)
        db.session.add(new_user)
        db.session.commit()

        directory = email
        parent_dir="static/images/user"
        path = os.path.join(parent_dir, directory)

        os.mkdir(path)
        return redirect('/login')

@app.route("/home")
@login_required
def home():
    user = session["user_id"]
    username = session["username"]
    db.session.commit()
    profile = get_profile_pic(session["email"])
    posts = get_posts(user)
    contacts = get_contacts(user)

    return render_template("home.html", posts=posts, profile=profile, user=username, contacts=contacts)

@app.route("/post", methods=["POST"])
@login_required
def post():
    content = request.form.get("content")
    tags = find_tag(content)
    owner = session["user_id"]

    now = datetime.now()
    time = now.strftime("%Y/%m/%d %H:%M:%S")
    post = PostModel(owner, content, time)
    db.session.add(post)
    db.session.commit()

    id_post = post.id

    for tag in tags:
        tag_model = TagModel(tag, owner, id_post, time)
        db.session.add(tag_model)
        db.session.commit()
    return redirect("/home")

@app.route("/user/<string:user>", methods=["GET", "POST"])
@login_required
def user(user):
    info = get_info(user)
    profile = get_profile_pic(info.email)
    db.session.commit()
    user_id = info.id
    posts = get_user_post(user_id)
    number_posts = check_number_posts(posts)

    user_now = session["user_id"]
    user_now_username = session["username"]
    is_following = check_following(user_now, info.id)
    is_user = check_user(user_now, user_id)
    followers = get_follower_n(user)
    following = get_following_n(user)
    return render_template("user.html", user=info, user_now=user_now_username, posts=posts, profile=profile, total=number_posts, is_following=is_following, followers=followers, following=following, is_user=is_user)

@app.route("/search", methods=["POST"])
@login_required
def search():
    query = '%' + request.form.get("query") + '%'
    results = []

    result = UserModel.query.filter(UserModel.username.like(query) | UserModel.name.like(query)).all()
    for result_data in result:
        email = result_data.email
        profile = get_profile_pic(email)
        result_dict = {"data" : result_data, "profile_path": profile}
        results.append(result_dict)
    return render_template("search.html", results=results, query=query)

@app.route("/unfollow", methods=["POST"])
@login_required
def unfollow():
    user = session["user_id"]
    unfollowing = request.form.get("user")

    unfollowing_id_data = UserModel.query.filter_by(username=unfollowing).first()
    unfollowing_id = unfollowing_id_data.id

    unfollow = FollowModel.query.filter(FollowModel.person_id==user, FollowModel.follow_id==unfollowing_id).first()
    unfollow_now = db.session.merge(unfollow)
    db.session.delete(unfollow_now)
    db.session.commit()
    return "", 200

@app.route("/follow", methods=["POST"])
@login_required
def follow():
    user = session["user_id"]
    following = request.form.get("user")

    following_id_data = UserModel.query.filter_by(username=following).first()
    following_id = following_id_data.id

    value = 1
    follow = FollowModel(user, following_id, value)
    db.session.add(follow)
    db.session.commit()
    return '', 200

@app.route("/like", methods=["POST"])
@login_required
def like():
    user = session["user_id"]
    post = request.form.get("post")

    value = 1
    like = LikeModel(user, post, value)
    db.session.add(like)
    db.session.commit()
    return '', 200

@app.route("/dislike", methods=["POST"])
@login_required
def dislike():
    user = session["user_id"]
    post = request.form.get("post")

    value = 1
    like = LikeModel.query.filter(LikeModel.owner==user, LikeModel.post_id==post).first()
    like_now = db.session.merge(like)
    db.session.delete(like_now)
    db.session.commit()
    return '', 200
