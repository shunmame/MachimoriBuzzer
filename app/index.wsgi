# coding: utf-8

import sys
sys.path.insert(0, '****')

import os
# os.environ['DB_USER'] = '****'
os.environ['DB_USER'] = '****'
os.environ['DB_PASS'] = '****'
# os.environ['DB_HOST'] = '****'
os.environ['DB_HOST'] = '****'
# os.environ['DB_DB'] = '****'
os.environ['DB_DB'] = '****'
os.environ['DB_PORT'] = '****'

os.environ['UPLOAD_FOLDER'] = '****'
os.environ['SECRET_KEY'] = '****'

#from flask_test import app as application
from app import app as application
