from flask import Flask, render_template, url_for,request,jsonify,g,make_response
import datetime
from flask_cors import CORS 
import mysql.connector as db
from flask_httpauth import HTTPBasicAuth,MultiAuth,HTTPTokenAuth
import base64
from flask_mail import Mail,Message
import random
import string

con=None
app = Flask(__name__)

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth(scheme='Basic')
CORS(app)
app.config.from_pyfile('app_config.py')
app.config["MAIL_USERNAME"]="email name"
app.config["MAIL_PASSWORD"]="your email pwd"
app.config["MAIL_SERVER"]="smtpout.secureserver.net"
app.config["MAIL_PORT"]=465
app.config["MAIL_USE_SSL"]=True
mail = Mail(app)


"""
@app.route('/mutualFunds',methods=['GET'])
def mutualFunds():
    token=request.cookies.get("token")
    if verify_token(token):
        amcs=get_all_amc_from_db()
        resp=make_response(render_template('mutualFunds.html',amcs=amcs,login=False,mf_class="active",eq_class="none",tokenIn=token))
    else:
        resp=make_response(render_template('messageToUser.html',message="There was an error validating session. Please try again later."))
    return resp
"""

"""
@app.route('/')
@app.route('/home',methods=['POST','GET'])
def home():
    if request.method ["POST","GET"]:
        email=request.form.get('emailInput',None)
        con=get_db_connection()
        try:
            cur=con.cursor()
            results=cur.callproc('verify_user',(email,0))
            if results[-1] != "N":
                token=randomString(30)
                s=create_session((email,token,0))
        except Exception:
            #con.close()
            pass
        finally:
            pass
            #con.close()
        if results[-1]=="N":
            return render_template('messageToUser.html',message="You are not registered. Please enter email and click register and activate your ID to use this tool.") 
        qryr_labels=[('6qtr',1),('8qtr',2),('12qtr',3),('max',4)]
        if s=="fail":
            render_template('messageToUser.html',message="There was an error creating session. Please try again later.") 
        else:
            resp=make_response(render_template('equity.html',qryr_labels=qryr_labels,tokenIn=token,login=False,mf_class="none",eq_class="active"))
            resp.set_cookie('token', token)
            return resp
    else:
        token=request.cookies.get("token")
        if verify_token(token):
            qryr_labels=[('6qtr',1),('8qtr',2),('12qtr',3),('max',4)]
            resp=make_response(render_template('equity.html',qryr_labels=qryr_labels,tokenIn=token,login=False,mf_class="none",eq_class="active"))
        else:
            resp=make_response(render_template('messageToUser.html',message="There was an error validating session. Please try again later."))
        return resp
"""

@app.route('/danalytics')
def getDailyAnalytics():
    v=vw_how_much_retails_lost()
    print(v)
    return render_template('danalytics.html',vw_mc_gt_10kcr_dpct_gt_60_tbl=vw_mc_gt_10kcr_dpct_gt_60(),vw_how_much_retails_lost_tbl=vw_how_much_retails_lost(),vw_bought_sold_perct_tbl=vw_bought_sold_perct(),vw_dividend_opportunities_tbl=vw_dividend_opportunities())

#@app.route('/mc_gt_10kcr_dpct_gt_60')
def vw_mc_gt_10kcr_dpct_gt_60():
    con=get_db_connection()
    cur=con.cursor()
    ret=[]
    try:
        stmt = "select * from vw_mc_gt_10kcr_dpct_gt_60"
        cur.execute(stmt)
        for (s,m,d,v) in cur:
            #ret.append(dict(zip(cur.column_names,(s,m,d,v))))
            ret.append((s,m,d,v))
    except Exception as e:
        raise
    finally:
        cur.close()
    return ret

def vw_how_much_retails_lost():
    con=get_db_connection()
    cur=con.cursor()
    ret=[]
    try:
        stmt = "select * from vw_how_much_retails_lost"
        cur.execute(stmt)
        for (s,w,v) in cur:
            #ret.append(dict(zip(cur.column_names,(s,m,d,v))))
            ret.append((s,w,v))
    except Exception as e:
        raise
    finally:
        cur.close()
    return ret

def vw_dividend_opportunities():
    con=get_db_connection()
    cur=con.cursor()
    ret=[]
    try:
        stmt = "select * from vw_dividend_opportunities"
        cur.execute(stmt)
        for (s,w,v) in cur:
            #ret.append(dict(zip(cur.column_names,(s,m,d,v))))
            ret.append((s,w,v))
    except Exception as e:
        raise
    finally:
        cur.close()
    return ret


def vw_bought_sold_perct():
    con=get_db_connection()
    cur=con.cursor()
    ret=[]
    try:
        stmt = "select * from vw_bought_sold_perct"
        cur.execute(stmt)
        for (s,aq,sh,cu) in cur:
            #ret.append(dict(zip(cur.column_names,(s,m,d,v))))
            ret.append((s,aq,sh,cu))
    except Exception as e:
        raise
    finally:
        cur.close()
    return ret


if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', debug=True)
    finally:
        if con.is_connected():
            con.close()
