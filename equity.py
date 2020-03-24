from flask import Flask, render_template, url_for,request,jsonify,g,make_response,Blueprint
import datetime
from flask_httpauth import HTTPBasicAuth,MultiAuth,HTTPTokenAuth
import random
import string
import utils
import api

bp=Blueprint("equity",__name__)

def get_db_connection():
    return utils.get_db_connection()

def create_session(args):
    con=get_db_connection()
    try:
        results=[]
        cursor = con.cursor()
        results=cursor.callproc('create_session',args)
    finally:
        cursor.close()
    return results[-1]

def validate_session(args):
    con=get_db_connection()
    try:
        results=[]
        cursor = con.cursor()
        results=cursor.callproc('validate_session',args)
    finally:
        cursor.close()
    return results[-1]

def randomString(stringLength):
    """Generate a random string with the combination of lowercase and uppercase letters """
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(stringLength))

@bp.route('/')
@bp.route('/home',methods=['POST','GET'])
def home():
    token=randomString(30)
    qryr_labels=[('6qtr',1),('8qtr',2),('12qtr',3),('max',4)]
    resp=make_response(render_template('equity/equity.html',qryr_labels=qryr_labels,tokenIn=token,login=False,mf_class="none",eq_class="active"))
    return resp

