import datetime
import mysql.connector as db


file=open("D:\\Download\\SchemeData1708191657SS.csv")

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
con=db.connect(host="localhost",user="<your user>",password="<your pwd>",auth_plugin='mysql_native_password',database="<your DB>")

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

def insert_mutual_funds(args):
    try:        
        cursor = con.cursor()
        cursor.callproc('insert_mutual_funds',args)

    finally:
        cursor.close()            
    return "success"

def get_short_name(name):
    if name.startswith("Equity Scheme"):
        return "Equity Scheme"
    elif name.startswith("Debt Scheme"):
        return "Debt Scheme"
    elif name.startswith("Hybrid Scheme"):
        return "Hybrid Scheme"
    elif name.startswith("Other Scheme"):
        return "Other Scheme"
    elif name.startswith("Solution Oriented Scheme"):
        return "Solution Oriented Scheme"
    else:
        return name
try:
    for i,line in enumerate(file):
        if i!=0:
            fields=line.split(",")
            amc=fields[0]
            code=fields[1]
            scheme_name=fields[2]
            scheme_type=fields[3]
            scheme_cat=fields[4]
            scheme_nav_name=fields[5]
            scheme_min_amt=fields[6]
            ld=get_todate(fields[7])
            cd=get_todate(fields[8])
            isin=fields[9]

            args=(amc,int(code),scheme_name,scheme_type,scheme_cat,get_short_name(scheme_cat),scheme_nav_name,scheme_min_amt,ld,cd,isin,0)
            insert_mutual_funds(args)

            print("inserted: ",scheme_nav_name)
finally:
    con.close()