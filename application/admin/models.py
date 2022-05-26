from flask import flash, current_app
from application import db
# import decimal
import copy
import os
from sqlalchemy.sql import func
from sqlalchemy import or_, and_
from . import models as wordmodels
from datetime import datetime


# This models file is added later just for admin stuff and should probably contain several things from the application.models file

class News(db.Model):

    """ Users can have different roles """
    __tablename__ = "news"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100))
    title_en = db.Column(db.String(100))
    text = db.Column(db.Text(2000))
    text_en = db.Column(db.Text(2000))
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    word_id = db.Column(db.Integer, db.ForeignKey("words.id"), nullable=True)
    word = db.relationship("Word")

    def __repr__(self):
        return f"News: {self.title}"


