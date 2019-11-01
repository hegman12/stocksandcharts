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
app.config["MAIL_USERNAME"]="email name"
app.config["MAIL_PASSWORD"]="your email pwd"
app.config["MAIL_SERVER"]="smtpout.secureserver.net"
app.config["MAIL_PORT"]=465
app.config["MAIL_USE_SSL"]=True
mail = Mail(app)
@basic_auth.verify_password
def verify_password(username, password):
    #con=db.connect(host="localhost",user="<your user>",password="<your pwd>",auth_plugin='mysql_native_password',database="<your DB>")
    if username=="hegde":
        return True    
    return False

@token_auth.error_handler
def auth_error():
    return make_response()

def get_db_connection():
    global con
    if con==None:
        con=db.connect(host="localhost",user="<your user>",password="<your pwd>",auth_plugin='mysql_native_password',database="<your DB>")
        return con
    if not con.is_connected():
        con=db.connect(host="localhost",user="<your user>",password="<your pwd>",auth_plugin='mysql_native_password',database="<your DB>")
    return con

@token_auth.verify_token
def verify_token(token):
    ret=True
    try:
        validatedToken=validate_session((token,0))
        if validatedToken =="expired":
            return False
    except Exception:
        ret=False
        raise
        #con.close()
    finally:
        pass
        #con.close()
    return ret

def randomString(stringLength):
    """Generate a random string with the combination of lowercase and uppercase letters """
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(stringLength))

def get_rc_from_db(args):
    con=get_db_connection()
    try:
        results=[]
        cursor = con.cursor()
        cursor.callproc('get_result_category_labels',args)
        for r in cursor.stored_results():
            for row in r:
                results.append(dict(zip(r.column_names,row)))
    finally:
        cursor.close()
    return results

def get_all_amc_from_db():
    con=get_db_connection()
    try:
        results=[]
        cursor = con.cursor()
        cursor.callproc('get_all_amcs',tuple())
        for r in cursor.stored_results():
            for row in r:
                results.append(dict(zip(r.column_names,row)))
    finally:
        cursor.close()
    return results


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

@app.route('/category/<int:stock_id>/<string:mode>/<int:no_of_qtr>')
@token_auth.login_required
def get_result_category_labels(stock_id,mode,no_of_qtr):
    stockCompare=request.args.get('stockCompare',0)
    con=get_db_connection()
    category_labels=[]
    try:
        category_labels=get_rc_from_db((stock_id,int(stockCompare),no_of_qtr,mode))
    finally:
        if con.is_connected():
            pass
            #con.close()
    return jsonify(category_labels)

def get_type_from_db(args):
    con=get_db_connection()
    try:
        results=[]
        cursor = con.cursor()
        cursor.callproc('get_result_type_label',args)
        for r in cursor.stored_results():
            for row in r:
                results.append(dict(zip(r.column_names,row)))
    finally:
        cursor.close()
    return results

def get_scheme_nav_from_db(args):
    con=get_db_connection()
    try:
        results=[]
        cursor = con.cursor()
        cursor.callproc('get_scheme_nav',args)
        for r in cursor.stored_results():
            for row in r:
                results.append(dict(zip(r.column_names,row)))
    finally:
        cursor.close()
    return results

def get_scheme_cat_from_db(args):
    con=get_db_connection()
    try:
        results=[]
        cursor = con.cursor()
        cursor.callproc('get_scheme_category',args)
        for r in cursor.stored_results():
            for row in r:
                results.append(dict(zip(r.column_names,row)))
    finally:
        cursor.close()
    return results

def get_mf_nav_from_db(args):
    con=get_db_connection()
    try:
        results1=[]
        results2=[]
        cursor = con.cursor()
        cursor.callproc('get_mutual_funds_nav',args)
        for i,r in enumerate(cursor.stored_results()):
            for row in r:
                if i==0:
                    results1.append(dict(zip(r.column_names,row)))
                else:
                    results2.append(dict(zip(r.column_names,row)))
    finally:
        cursor.close()
    return results1,results2

@app.route("/mutualFunds/schemeCat/<int:amc1>/<int:amc2>")
def get_scheme_category(amc1,amc2):
    scheme_cat=get_scheme_cat_from_db((amc1,amc2))
    return jsonify(scheme_cat)
 
@app.route("/mutualFunds/schemeNav/<int:amc1>/<int:amc2>/<int:scheme_cat_id>")
def get_scheme_nav(amc1,amc2,scheme_cat_id):
    scheme_nav=get_scheme_nav_from_db((amc1,amc2,scheme_cat_id))
    return jsonify(scheme_nav)

@app.route("/mutualFunds/performance/<int:code1>/<int:code2>/<int:days>")
def get_mf_nav(code1,code2,days):
    mf_nav=get_mf_nav_from_db((code1,code2,days))
    return jsonify(mf_nav)

@app.route('/type/<int:stock_id>/<string:mode>/<int:no_of_qtr>/<int:catID>')
@token_auth.login_required
def get_result_type_labels(stock_id,mode,no_of_qtr,catID):
    stockCompare=request.args.get('stockCompare',0)
    con=get_db_connection()
    type_labels=[]
    try:
        type_labels=get_type_from_db((stock_id,int(stockCompare),no_of_qtr,mode,catID))
    finally:
        if con.is_connected():
            pass
            #con.close()

    return jsonify(type_labels)

@app.route('/search/<string:search_string>')
@token_auth.login_required
def get_stock_search_results(search_string):
    con=get_db_connection()
    try:
        cur=con.cursor(prepared=True)
        select_stmt = "SELECT stock_id,stock_name FROM stocks WHERE stock_name like %s or nse_id like %s or bse_id like %s"
        cur.execute(select_stmt, ( "%"+search_string+"%","%"+search_string+"%","%"+search_string+"%"))
        #cur.callproc('visualize.search_stock',(search_string,refcur))
        #for i,j in cur:
         #   print(i,j)
        out=[{'stockId':id,'stockName':name.decode("utf-8") } for id,name in cur]        
    finally:
        pass
        #con.close()
    return jsonify(out)

@app.route('/graph/<int:stockID>')
@token_auth.login_required
def get_graph_data(stockID):
    mode=request.args.get('mode',None)
    categoryId=request.args.get('categoryId',None)
    fromQtr=request.args.get('fromQtr',None)
    totalQtr=request.args.get('totalQtr',None)
    totalQtrIncome=request.args.get('totalQtrIncome',None)
    stmtTypeID=request.args.get('resultTypeId',None)
    secondaryStockID=request.args.get('secondaryStockID',None)
    price1=request.args.get('price1','N')
    price2=request.args.get('price2','N')
    con=get_db_connection()
    try:
        cur=con.cursor()
        cur.callproc('get_graph_data',(stockID,secondaryStockID,categoryId,stmtTypeID,mode,fromQtr,totalQtr,totalQtrIncome,price1,price2))
        results=[]
        price1=[]
        price2=[]
        for i,r in enumerate(cur.stored_results()):
            if i==0:
                for row in r:
                    results.append(dict(zip(r.column_names,row)))
            elif i==1:
                for row in r:
                    if request.args.get('price1','N')=="Y":
                        price1.append(dict(zip(r.column_names,row)))
                    else:
                        price2.append(dict(zip(r.column_names,row)))
            else:
                for row in r:
                    price2.append(dict(zip(r.column_names,row)))
        if mode !="S":
            out=[{'name':r["stock_id"],'year':r["period"],'value':float(r["value"])} for r in results]
        else:
            out=[{'year':r["period"],'value':float(r["value"])} for r in results]
    finally:
        pass
        #con.close()

    return jsonify(income=out,price1=price1,price2=price2)

@app.route('/')
def login(): 
    #qryr_labels=[('6qtr',1),('8qtr',2),('12qtr',3),('max',4)]
    #return render_template('test.html',qryr_labels=qryr_labels)
    #return render_template('test.html',message="Please login to use the service")
    return render_template('login.html',login=True,mf_class="none",eq_class="active")

@app.route('/mutualFunds',methods=['GET'])
def mutualFunds():
    token=request.cookies.get("token")
    if verify_token(token):
        amcs=get_all_amc_from_db()
        resp=make_response(render_template('mutualFunds.html',amcs=amcs,login=False,mf_class="active",eq_class="none",tokenIn=token))
    else:
        resp=make_response(render_template('messageToUser.html',message="There was an error validating session. Please try again later."))
    return resp

@app.route('/home',methods=['POST','GET'])
def home():
    if request.method=="POST":
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

@app.route('/register',methods=['POST'])
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
        mail.send(msg)
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

@app.route('/activate/<int:actid>/<string:token>')
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

if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', debug=True)
    finally:
        if con.is_connected():
            con.close()
