import datetime
from datetime import datetime as dtime
import mysql.connector as db
import urllib.request as r
from flask_mail import Mail,Message
from flask import Flask

app = Flask(__name__)
app.config["MAIL_USERNAME"]="email"
app.config["MAIL_PASSWORD"]="email pwd"
app.config["MAIL_SERVER"]="smtpout.secureserver.net"
app.config["MAIL_PORT"]=465
app.config["MAIL_USE_SSL"]=True
mail = Mail(app)

con=None

def mon_to_n(inp):
    if inp=="Jan":
        return 1
    elif inp=="Feb":
        return 2
    elif inp=="Mar":
        return 3
    elif inp=="Apr":
        return 4
    elif inp=="May":
        return 5
    elif inp=="Jun":
        return 6
    elif inp=="Jul":
        return 7
    elif inp=="Aug":
        return 8
    elif inp=="Sep":
        return 9
    elif inp=="Oct":
        return 10
    elif inp=="Nov":
        return 11
    elif inp=="Dec":
        return 12
    else:
        return 0

def get_todate(p):
    if p:
        d=p[0:2]
        m=mon_to_n(p[3:6])
        y=p[7:]
        if len(y)<4:
            if int(y)>70:
                y="19"+y
            else:
                y="20"+y
        return datetime.date(int(y),int(m),int(d))
    else:
        return datetime.date(1900,1,1)

def get_db_connection():
    global con
    if con==None:
        con=db.connect(host="localhost",user="<your user>",password="<your pwd>",auth_plugin='mysql_native_password',database="<your DB>")
        return con
    if not con.is_connected():
        con=db.connect(host="localhost",user="<your user>",password="<your pwd>",auth_plugin='mysql_native_password',database="<your DB>")
    return con

def get_data_processing_start_date(batch_id):
    con=get_db_connection()
    try:        
        cursor = con.cursor()
        results=cursor.callproc('get_data_date',(batch_id,0))

    finally:
        cursor.close()
        if con.is_connected():
            #con.close()
            pass
    return results[-1]

def update_data_processing_start_date(batch_id,data_date):
    con=get_db_connection()
    try:        
        cursor = con.cursor()
        cursor.callproc('update_data_date_batch',(batch_id,data_date))

    finally:
        cursor.close()
        if con.is_connected():
            #con.close()
            pass

def log(batch_id,message):
    con=get_db_connection()
    try:        
        cursor = con.cursor()
        cursor.callproc('insert_batch_log',(batch_id,message))
    finally:
        cursor.close()
        if con.is_connected():
            #con.close()
            pass

try:
    url=None
    start_time=get_data_processing_start_date(1)
    start_time=dtime.strptime(start_time, "%Y-%m-%d")
    print(start_time.date())
    flag=True
    while flag:
        d=datetime.datetime.date(datetime.datetime.now())
        if start_time.weekday() in [5,6]:
            start_time=start_time+datetime.timedelta(days=1)
            continue    
        if start_time.date()>=d:
            break
        url="http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?tp=1&frmdt={start_time}".format(start_time=start_time.strftime("%d-%b-%Y"))
        print(url)
        start_time=start_time+datetime.timedelta(days=1)

        req = r.Request(url)
        response = r.urlopen(req)
        the_page = response.read()
        args=[]
        for line in the_page.decode("utf-8").split("\r\n"):
            if line:
                if line[0] in ['1','2','3','4','5','6','7','8','9','0']:
                    fields=line.split(";")
                    scheme_code=fields[0]
                    nav_date=get_todate(fields[-1])
                    nav_value= 0 if fields[4]=="N.A." else float(fields[4])
                    args.append((int(scheme_code),nav_date,nav_value))
        cur=con.cursor()
        try:
            stmt = "INSERT IGNORE INTO mutual_funds_nav (scheme_code, nav_date,nav_value) values(%s,%s,%s)"
            cur.executemany(stmt, args)
            cur.execute("commit;")
        finally:
            cur.close()
        # if con.is_connected():
        #     con.close()   
        log(1,"Scraped data for url: {url}".format(url=url))
    update_data_processing_start_date(1,start_time)

    msg = Message("Daily mutual fund nav batch success",sender="communications@stocksandcharts.in",recipients=["hegman12@gmail.com"])
    msg.body = "testing"
    msg.html = """<div'>
    <p>Successfully scraped data for {start_time}</p>
    </div>""".format(start_time=start_time)
    with app.app_context():
        mail.send(msg)
    con.close()
except Exception as e:
    log(1,"unable to scrap data for url: {url} , error: {error}".format(url=url,error=e))
    msg = Message("Daily mutual fund nav batch error",sender="communications@stocksandcharts.in",recipients=["hegman12@gmail.com"])
    msg.body = "testing"
    msg.html = """<div'>
    <p>Error scrapping data for {start_time}</p>
    </div>""".format(start_time=start_time)
    with app.app_context():
        mail.send(msg)
    con.close()
finally:
    con.close()

