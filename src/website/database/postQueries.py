from .models import Post
from .. import db
from os.path import join, dirname, realpath
import os

def deletePost(id):
    Post.query.filter(Post.id == id).delete(synchronize_session=False)
    db.session.commit()
    return

def getMaxPostID():
    max_post = Post.query.order_by(Post.id.desc()).first()
    if max_post == None:
        max_session_id = 1
    else:
        max_session_id = max_post.id + 1
    return max_session_id

def getPosts():
    all_posts = Post.query.order_by(Post.id.desc()).all()
    return all_posts

def addPostWithPicture(id, title, text, date, file):
    fileName = "post" + str(id) + "." + file.filename.rsplit('.', 1)[1]
    UPLOADS_PATH = join(dirname(realpath(__file__)), os.pardir, 'static/pictures/', fileName)
    file.save(UPLOADS_PATH)
    new_post = Post(id=id, imgURL="pictures/" + fileName, title = title, text = text, date = date)
    db.session.add(new_post)
    db.session.commit()

def addPost(id, title, text, date):
    new_post = Post(id=id, imgURL="NoPicture", title = title, text = text, date = date)
    db.session.add(new_post)
    db.session.commit()

def updatePostWithPicture(id, title, date, text, file):
    fileName = "post" + str(id) + "." + file.filename.rsplit('.', 1)[1]
    UPLOADS_PATH = join(dirname(realpath(__file__)), os.pardir, 'static/pictures/', fileName)
    file.save(UPLOADS_PATH)
    imgURL="pictures/" + fileName
    Post.query.filter(Post.id == id).update({Post.title: title, Post.date: date, Post.imgURL: imgURL, Post.text: text})
    db.session.commit()

def updatePost(id, title, date, text):
    Post.query.filter(Post.id == id).update({Post.title: title, Post.date: date, Post.text: text})
    db.session.commit()