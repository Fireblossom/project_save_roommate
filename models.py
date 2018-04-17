#encoding: utf-8

from exts import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    telephone = db.Column(db.String(11), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Contribute(db.Model):
    __tablename__ = 'contribute'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    poet = db.Column(db.String(100), nullable=False)
    dynasty = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    # now()获取的是服务器第一次运行的时间
    # now就是每次创建一个模型的时候，都获取当前的时间
    create_time = db.Column(db.DateTime, default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref=db.backref('contributes'))

class Answer(db.Model):
    __tablename__ = 'answer'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    contribute_id = db.Column(db.Integer, db.ForeignKey('contribute.id', ondelete='CASCADE'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    contribute = db.relationship('Contribute', backref=db.backref('answers', order_by=id.desc()))
    author = db.relationship('User', backref=db.backref('answers'))

class Star(db.Model):
    __tablename__ = 'star'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column(db.DateTime, default=datetime.now)
    contribute_id = db.Column(db.Integer, db.ForeignKey('contribute.id', ondelete='CASCADE'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
