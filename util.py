import os
import requests
import urllib.parse
import re

from flask import redirect, render_template, request, session
from functools import wraps
from model import *
from datetime import datetime

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def get_info(user):
    info = UserModel.query.filter_by(username=user).first()
    return info

def get_following(user):
    Following = FollowModel.query.filter_by(person_id=user).all()
    followings = []
    for follow in Following:
        if follow.value == 1:
            followings.append(follow)
    return followings

def get_profile_pic(email):
    path = "static/images/user/" + email + "/profile.jpg"
    if not os.path.exists(path):
         return "static/images/profile.png"
    else:
        return path

def sort_posts(Post):
    try:
        Post.sort(key=lambda x: x.time, reverse=True)
    except:
        return Post
    else:
        return Post

def get_posts(user):
    user_now = session["user_id"]
    following = get_following(user)
    Post = []
    for x in range(len(following)):
        Post_temp = PostModel.query.filter_by(owner=following[x].follow_id).order_by(PostModel.time.desc()).all()
        for x in range(len(Post_temp)):
            Post.append(Post_temp[x])

    Post = sort_posts(Post)
    posts = []

    for post in Post:
        owner_search = UserModel.query.filter_by(id=post.owner).first()
        owner = owner_search.name
        owner_username = owner_search.username

        profile_user = get_profile_pic(owner_search.email)

        content = post.content
        post_id = post.id

        post_like = find_is_like(user_now, post_id)
        time = time_parse(post.time)
        like_n = LikeModel.query.filter_by(post_id=post_id).count()

        post_n = {"id" : post_id, "owner": owner, "content": content, "time": time, "username": owner_username, "profile_path": profile_user, "like" : like_n, "is_like": post_like}
        posts.append(post_n)
    return posts

def get_contacts(user):
    contacts = FollowModel.query.filter_by(person_id=user).all()

    contacts_list = []
    for contact in contacts:
        personal_data = UserModel.query.filter_by(id=contact.follow_id).first()
        username = personal_data.username
        name = personal_data.name
        email = personal_data.email
        profile = get_profile_pic(email)
        contact_dict = {"username": username, "name": name, "email": email, "profile_path": profile}
        contacts_list.append(contact_dict)

    return contacts_list

def get_user_post(user):
    posts = PostModel.query.filter_by(owner=user).all()

    user_now = session["user_id"]
    posts = sort_posts(posts)
    post_list = []

    for post in posts:
        owner_search = UserModel.query.filter_by(id=post.owner).first()
        owner = owner_search.name
        owner_username = owner_search.username

        profile_user = get_profile_pic(owner_search.email)

        content = post.content
        time = time_parse(post.time)
        post_id = post.id

        post_like = find_is_like(user_now, post_id)
        post_n = {"id" : post_id, "owner": owner, "content": content, "time": time, "username": owner_username, "profile_path": profile_user, "is_like" : post_like}
        post_list.append(post_n)

    return post_list

def check_following(user, following_id):
    following = FollowModel.query.filter(FollowModel.person_id==user, FollowModel.follow_id==following_id).first()
    try:
        is_following = following.person_id
    except:
        return False
    else:
        return True

def check_number_posts(posts):
    n = 0
    for post in posts:
        n += 1
    return n

def get_following_n(user):
    id_user_query = UserModel.query.filter_by(username=user).first()

    id_user = id_user_query.id
    following = get_following(id_user)
    if following == None:
        n = 0
        return n
    else:
        try:
            n = len(following)
            return n
        except:
            return 1

def get_follower_n(user):
    id_user_query = UserModel.query.filter_by(username=user).first()

    id_user = id_user_query.id
    followers = FollowModel.query.filter(FollowModel.follow_id==id_user).all()

    if followers == None:
        n = 0
        return n
    else:
        try:
            n = len(followers)
            return n
        except:
            return 1

def check_user(usernow, user):
    if usernow == user:
        return True
    else:
        return False


def time_parse(time):
    year = time.year
    month = time.month
    date = time.day
    month_str = time.strftime("%b")


    hour = time.hour
    minute = time.minute
    second = time.second

    now = datetime.now()
    year_now = int(now.strftime("%Y"))
    month_now = int(now.strftime("%m"))
    date_now = int(now.strftime("%d"))

    hour_now = int(now.strftime("%H"))
    minute_now = int(now.strftime("%M"))

    if year == year_now:
        year_ = True
    else:
        year_ = False

    if month == month_now:
        month_ = True
    else:
        month_ = False

    if date == date_now:
        date_ = True
    else:
        date_ = False

    if hour == hour_now:
        hour_ = True
    else:
        hour_ = False

    if minute == minute_now:
        minute_ = True
    else:
        minute_ = False

    if year_:
        if month_:
            if date_:
                if hour_:
                    if minute_:
                        time_ = "Just Now"
                    else:
                        time_ = str(minute_now - minute) + "m"
                else:
                    if hour_now - hour == 1:
                        if (minute + 60) - minute_now < 60:
                            time_ = str(minute + 60 - minute_now) + "m"
                        else:
                            time_ = "1h"
                    else:
                        time_ = str(hour_now - hour) + "h"
            else:
                if date_now - date == 1:
                    if (hour + 24) - hour_now < 24:
                        time_ = str(hour + 23 - hour_now) + "h"
                    else:
                        time_ = "1d"
                else:
                    time_= str(date_now - date) + "d"
        else:
            time_ = str(month_str) + " " + str(date)
    else:
        time_ = str(month_str) + " " + str(date) + ", " + str(year)
    return time_

def find_tag(content):
    tag = re.findall(r"#(\w+)", content)
    return tag

def find_is_like(user, post):
    like = LikeModel.query.filter(LikeModel.owner==user, LikeModel.post_id==post).count()

    if like == 0:
        return False
    else:
        return True