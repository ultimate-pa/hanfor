import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_testing import TestCase
from hanfor import create_app, db
from hanfor.models import Tag, Variable, Expression
from hanfor.tests.populate_db import populate_patterns, populate_scopes

basedir = os.path.abspath(os.path.dirname(__file__))

class TestEnvironment(TestCase):
    """ Hanfor specific TestCase """
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test_app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True

    def create_app(self):
        return create_app(self)

    def setUp(self):
        db.session.close()
        db.drop_all()
        db.create_all()
        populate_patterns()
        populate_scopes()

    def tearDown(self):
        db.session.remove()
