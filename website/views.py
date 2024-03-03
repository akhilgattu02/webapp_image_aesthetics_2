from flask import Blueprint, render_template, request, redirect, url_for, session,flash
from flask_login import login_required, current_user
from .models import User
from . import db
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
    "img_db", check_same_thread=False)

cur = conn.cursor()

'''
cur.execute('SELECT * FROM images')
imgs = cur.fetchall()


cur.execute('SELECT * FROM aspect_images')
imgs = cur.fetchall()
total_imgs = len(imgs)

cur.execute('SELECT * from audios')
auds = cur.fetchall()
total_auds = len(auds)
'''
cur.execute(f'SELECT max(width) from aspect_images')
max_width = cur.fetchall()
max_width = max_width[0][0]

cur.execute(f'SELECT max(height) from aspect_images')
max_height = cur.fetchall()
max_height = max_height[0][0]

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    global_time = time.time()
    sess_idntfr = ''.join(random.choices(string.ascii_uppercase +
                                         string.digits, k=10))  # Generate a custom session ID
    session["sql_query_aspect_data"] = "INSERT INTO aspect_data(user_id, session_id, img1, img2, selection,time_taken) VALUES"
    session["sql_query_data"] = "INSERT INTO data(user_id, session_id, img1, img2, selection,time_taken) VALUES"
    session["small_query_aspect_data"] = ""
    session["small_query_data"] = ""
    session["update_no"] = 0
    session["start_time"] = 0
    session["image_selection"] = []
    session["id"] = sess_idntfr
    session["global_time"] = global_time
    session["eml"] = ""
    cur.execute('SELECT distinct image_class FROM aspect_images')
    image_classes =  cur.fetchall()
    image_classes_unique = random.choice(image_classes)
    cur.execute(f'SELECT img_id FROM aspect_images where image_class = {image_classes_unique[0]}')
    links = cur.fetchall()
    for i in range(0, len(links)):
        links[i] = links[i][0]
    session["links"] = links
    return render_template("home.html", user=current_user, sid=sess_idntfr)


@views.route('/select')
@login_required
def select():
    try:
        sess = session["id"]  # store the value of session_identifier from home
    except:
        flash('Something went wrong with the session! Please try again',category='error')
        render_template(url_for('views.home'))

    survey_type = session.get('survey_type')
    if survey_type is None: #if survey_type is none, it means select is being called from home and we need to request it from the form.
        survey_type = request.args.get('survey') #if survey_type is already stored in the session, then no need to request
        session['survey_type'] = survey_type    

    #setting the right table to insert into
    if survey_type == 'temple':
        table_name = 'data'
    elif survey_type == 'aspect':
        table_name = 'aspect_data'
    else:
        return redirect(url_for('views.home'))
    
    cursorObject = conn.cursor()
    '''
    try:
        cursorObject.execute(f"SELECT img1, img2 FROM {table_name} WHERE session_id ='{sess}' ")  # select images from the database with same session_id so that they can be removed.
    except:
        flash('Something went wrong with the database! Please re-take the survey',category='error')
        redirect(url_for('views.home'))
    res = cursorObject.fetchall()
    '''
    if session["update_no"] == 0 and len(session["image_selection"]) != 0:
        if table_name == 'data':
            session["small_query_data"] = "(\'%s\', \'%s\', %s, %s, %s, %s)"%(str(current_user), str(session["id"]), session["image_selection"][-1][0], session["image_selection"][-1][1], -1, 5)
        if table_name == 'aspect_data':
            session["small_query_aspect_data"] = "(\'%s\', \'%s\', %s, %s, %s, %s)"%(str(current_user), str(session["id"]), session["image_selection"][-1][0], session["image_selection"][-1][1], -1, 5)

    sess_limit = True if len(session["image_selection"]) == max_pairs_in_session else False
    # make a list of all such rows and delete them
    #lis = list(range(1, total_imgs+1))
    #lis = list(range(1, total_imgs+1))
    lis = session["links"].copy()
    '''
    for x in session["image_selection"]:
        #print(x[0],x[1])
        if x[0] in lis:
            lis.remove(x[0])
        if x[1] in lis:
            lis.remove(x[1])
    '''
    # if all images are done, render the home page
    login_timeout = max_pairs_in_session * time_for_each_pair + 3
    session_time = time.time()-session["global_time"]
    if len(lis) == 0 or sess_limit or (session_time >= login_timeout):
        if table_name == 'data':
            session["sql_query_data"] = session["sql_query_data"] + session["small_query_data"]
        if table_name == 'aspect_data':
            session["sql_query_aspect_data"] = session["sql_query_aspect_data"] + session["small_query_aspect_data"]
        try:
            if session["small_query_data"] != "":
                cursorObject.execute(session["sql_query_data"])
            if session["small_query_aspect_data"] != "":
                cursorObject.execute(session["sql_query_aspect_data"])
            conn.commit()
        except:
            print("Sql aspect data\n")
            print(session["sql_query_aspect_data"])
            print("Sql data\n")
            print(session["sql_query_data"])
            flash('Something went wrong with the database! Please re-take the survey',category='error')
            redirect(url_for('views.home'))   
        session["sql_query_aspect_data"] = "INSERT INTO aspect_data(user_id, session_id, img1, img2, selection,time_taken) VALUES"
        session["sql_query_data"] = "INSERT INTO data(user_id, session_id, img1, img2, selection,time_taken) VALUES"
        session["small_query_data"] = ""
        session["small_query_aspect_data"] = ""
        session["image_selection"] = []
        session.pop('survey_type')
        print(lis)
        return redirect(url_for('views.thank_you'))
    if table_name == 'data':
        if session["small_query_data"] != "":
            session["sql_query_data"] = session["sql_query_data"] + session["small_query_data"] + ","
    if table_name == 'aspect_data':
        if session["small_query_aspect_data"] != "": 
            session["sql_query_aspect_data"] = session["sql_query_aspect_data"] + session["small_query_aspect_data"] + ","
    if table_name == 'data': table_name = 'images'
    if table_name == 'aspect_data': table_name = 'aspect_images'

    # make random choices and select those images
    i1 = random.choice(lis)
    lis.remove(i1)
    i2 = random.choice(lis)
    try:
        cursorObject.execute(
        f"SELECT img_id,link FROM {table_name} WHERE img_id={i1}")
    except:
        flash('Something went wrong with the database! Please re-take the survey',category='error')
        redirect(url_for('views.home'))
    image1 = cursorObject.fetchone()
    try:
        cursorObject.execute(
        f"SELECT img_id,link FROM {table_name} WHERE img_id={i2}")
    except:
        flash('Something went wrong with the database! Please re-take the survey',category='error')
        redirect(url_for('views.home'))   
    image2 = cursorObject.fetchone()
    session["start_time"] = time.time()
    imgs_chosen = []
    imgs_chosen.append(i1)
    imgs_chosen.append(i2)
    session["image_selection"].append(imgs_chosen)
    session["update_no"] = 0
    return render_template('survey.html', img1=image1, img2=image2, user=current_user,survey_type=survey_type, max_width_db=max_width, max_height_db=max_height)

@ views.route('/submit', methods=['POST'])
@ login_required
def submit():
    # get the user's selection and the two images that were shown
    user_id = request.form['user_id']
    selection = request.form['selection']
    img1 = request.form['img1']
    img2 = request.form['img2']
    try:
        time_taken_ = time.time()-session["start_time"]
    except:
        flash('Something went wrong with the timer! Please re-take the survey',category='error')
        return redirect(url_for('views.home'))

    survey_type = request.form['survey']  # Get the survey type from the submitted form data

    if survey_type == 'temple':
        table_name = 'data'
        session["small_query_data"] = "(\'%s\', \'%s\', %s, %s, %s, %s)"%(user_id, session["id"], img1, img2, selection,time_taken_) 
    elif survey_type == 'aspect':
        table_name = 'aspect_data'
        session["small_query_aspect_data"] = "(\'%s\', \'%s\', %s, %s, %s, %s)"%(str(user_id), str(session["id"]), img1, img2, selection,time_taken_) 
    '''    
    else:
        flash('Something went wrong with the database! Please re-take the survey',category='error')
        return redirect(url_for('views.home',survey_type=survey_type))
    '''
    session["update_no"] = 1
    time.sleep(time_between_pairs)  
    # insert the data into the database
    #cur = conn.cursor()
    
    '''
    try:
        cur.execute(f"INSERT INTO {table_name} (user_id, session_id, img1, img2, selection,time_taken) VALUES (?, ?, ?, ?, ?,?)",
                (user_id, sess_idntfr, img1, img2, selection,time_taken_))
    except:
        flash('Something went wrong with the database! Please re-take the survey',category='error')
        redirect(url_for('views.home'))
    conn.commit()
    '''
    # redirect to the home page to show the next pair of images
    
    return redirect(url_for('views.select',survey_type=survey_type))

########################
#Routes for audio survey

# @views.route('/audio_select')
# @login_required
# def audio_select():
#     sess = sess_idntfr  # store the value of session_identifier from home
#     cursorObject = conn.cursor()
#     cursorObject.execute(
#         "SELECT aud1, aud2 FROM audio_data WHERE session_id = '{}' ".format(sess))  # select audios from the database with same session_id so that they can be removed.
#     res = cursorObject.fetchall()
#     sess_limit = True if len(res) == max_pairs_in_session else False
#     # make a list of all such rows and delete them
#     lis = list(range(1, total_auds+1))
    
#     for x in res:
#         lis.remove(x[0])
#         lis.remove(x[1])

#     # if all audios are done, render the home page
#     if len(lis) == 0 or sess_limit:
#         return redirect(url_for('views.thank_you'))

#     # make random choices and select those audios
#     i1 = random.choice(lis)
#     lis.remove(i1)
#     i2 = random.choice(lis)
#     cursorObject.execute(
#         "SELECT aud_id,link FROM audios WHERE aud_id={}".format(i1))
#     a1 = cursorObject.fetchone()
#     cursorObject.execute(
#         "SELECT aud_id,link FROM audios WHERE aud_id={}".format(i2))
#     a2 = cursorObject.fetchone()
#     global start_time
#     start_time = time.time()
#     return render_template('audio_survey.html', aud1=a1, aud2=a2, user=current_user)

# @ views.route('/audio_submit', methods=['POST'])
# @ login_required
# def audio_submit():
#     # get the user's selection and the two audios that were shown
#     user_id = request.form['user_id']
#     selection = request.form['selection']
#     aud1 = request.form['aud1']
#     aud2 = request.form['aud2']
#     sess_id = request.form['sess_id']
#     time_taken_ = time.time()-start_time
#     # insert the data into the database
#     cur = conn.cursor()
#     cur.execute("INSERT INTO audio_data (user_id, session_id, aud1, aud2, selection, time_taken) VALUES (?, ?, ?, ?, ?,?)",
#                 (user_id, sess_idntfr, aud1, aud2, selection,time_taken_))
#     conn.commit()
#     # redirect to the survey page to show the next pair of audios
#     return redirect(url_for('views.audio_select'))

@ views.route('/thank_you')
@login_required
def thank_you():
    return render_template("thankyou.html",user= current_user)