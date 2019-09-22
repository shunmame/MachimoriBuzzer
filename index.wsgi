# coding: utf-8

import sys
sys.path.insert(0, '/var/www/app')

import os
os.environ['DB_USER'] = 'machimori'
os.environ['DB_PASS'] = 'yatsushironct'
os.environ['DB_HOST'] = '127.0.0.1'
os.environ['DB_DB'] = 'machimori'
os.environ['DB_PORT'] = '3306'

os.environ['UPLOAD_FOLDER'] = '/var/www/app/static/map_display/img/safeguard/'
os.environ['SECRET_KEY'] = 'machimori'

#from flask_test import app as application
from app import app as application
