from flask import Blueprint, render_template, request, redirect, url_for, session,flash
from flask_login import login_required, current_user
import json
import time
import uuid
import sqlite3
import random
import string
import datetime

time_between_pairs = 2
time_for_each_pair = 5
max_pairs_in_session = 20

views = Blueprint('views', __name__)

conn = sqlite3.connect(
    "../img_db", check_same_thread=False)

cur = conn.cursor()
'''
cur.execute('SELECT distinct image_class FROM aspect_images')
img_class = cur.fetchall()
dist_img_class = random.choice(img_class)
print(dist_img_class[0])
cur.execute(f'SELECT img_id FROM aspect_images where image_class = {dist_img_class[0]}')
imgs = cur.fetchall()
img_2 = [[0, 1], [0, 2]]
cur.execute(f'SELECT max(width) from aspect_images')
max_width = cur.fetchall()
'''
x = random.choice([1])
print(x)
#print(max_width[0][0])