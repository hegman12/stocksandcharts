import datetime
import mysql.connector as db
import urllib.request as r

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


con=db.connect(host="localhost",user="<your user>",password="<your pwd>",auth_plugin='mysql_native_password',database="<your DB>")

start_time=datetime.date(year=2015,month=3,day=3)

end_time=None
flag=True
while flag:
    d=datetime.datetime.date(datetime.datetime.now())
    if start_time>d:
        break
    end_time=start_time+datetime.timedelta(days=60)
    url="http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?tp=1&frmdt={start}&todt={end}".format(start=start_time.strftime("%d-%b-%Y"),end=end_time.strftime("%d-%b-%Y"))
    start_time=start_time+datetime.timedelta(days=60)

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
    print("scrapped: ",url)
    
con.close()
