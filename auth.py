from flask import Flask, render_template, url_for,request,jsonify,make_response,Blueprint,current_app
import datetime
from flask_httpauth import HTTPBasicAuth,MultiAuth,HTTPTokenAuth
from flask_mail import Mail,Message
import random
import string
import utils
import api

bp=Blueprint("auth",__name__,url_prefix="/auth",)

def randomString(stringLength):
    """Generate a random string with the combination of lowercase and uppercase letters """
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(stringLength))

def get_db_connection():
    return utils.get_db_connection()

@bp.route('/register',methods=['POST'])
def register():
    results=[]
    email=request.form.get('emailInput',None)
    con=get_db_connection()
    try:
        cur=con.cursor()
        token=randomString(10)
        results=cur.callproc('register_user',(email,'S',token,0,1))
    except Exception:
        results.append("fail")
    finally:
        pass
        #con.close()
    if results[-2]!="success":
        if results[-2]=="AR":
            return render_template('messageToUser.html',message="Already registered. Please activate your ID if you have not done so.") 
        else:
            return render_template('messageToUser.html',message="There was an error registering you. Please try again later.") 
    msg = Message("Hello",sender="communications@stocksandcharts.in",recipients=[email])
    msg.body = "testing"
    msg.html = """<div style='margin-left: 50px;margin-right: 50px;margin-bottom: 50px'>
    <p>Dear {email}</p><br>
    <span>Thanks for your interest in the service. You can activate your account by clicking below link.</span><br>
    <br>
    <a href='{link}' ' style='background: blue;padding: 10px;color: yellow;font-family: Calibri;font-size: 15px;border-radius: 10px '><b>Activate account<b></a>
    <br>
    <br>
    <p>Thanks and Regards, <br> Manjunath
    </p>

</div>""".format(email=email,link=results[-1])
    try:
        current_app.send(msg)
    except Exception:
        pass
    return render_template('messageToUser.html',message="You have been registered. Please login to your email and activate the servce to login. Dont forget to check spam folder if you did not get email!") 

def activate_user(args):
    con=get_db_connection()
    try:
        results=[]
        cursor = con.cursor()
        results=cursor.callproc('activate_user',args)
    finally:
        cursor.close()
    return results[-1]

@bp.route('/activate/<int:actid>/<string:token>')
def activate(actid,token): 
    message=None
    try:
        results=activate_user((actid,0))
        print(results)
        if results=="success":
            message="You have been activated. Please login to use the service"
        else:
            message=results
    except Exception as e:
        print(e)
        message="There was an error activating. Please ty again"
        #con.close()
    finally:
        pass
        #con.close()    
    return render_template('messageToUser.html',message=message) 

def login(): 
    #qryr_labels=[('6qtr',1),('8qtr',2),('12qtr',3),('max',4)]
    #return render_template('test.html',qryr_labels=qryr_labels)
    #return render_template('test.html',message="Please login to use the service")
    return render_template('auth/login.html',login=True,mf_class="none",eq_class="active")