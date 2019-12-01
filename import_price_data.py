import mysql.connector as db
from os import listdir
from os import path
from os.path import isfile, join

con=db.connect(host="localhost",user="your user",password="your pwd",auth_plugin='mysql_native_password',database="your DB")
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

def already_processed(stock_id):
    try:        
        cursor = con.cursor()
        results=cursor.callproc('already_processed_price',(stock_id,0))

    finally:
        cursor.close()
        if con.is_connected():
            #con.close()
            pass
    return results[-1]

onlyfiles = [f for f in listdir("C:\\Users\\manju\\Downloads") if isfile(join("C:\\Users\\manju\\Downloads", f))]
files_path=[join("C:\\Users\\manju\\Downloads", f) for f in listdir("C:\\Users\\manju\\Downloads") if isfile(join("C:\\Users\\manju\\Downloads", f)) and f.split(".")[1]=="csv"]
bse_id=[s.split(".")[0] for s in onlyfiles if s.split(".")[1]=="csv"]

for i,f in enumerate(files_path):
    print("procesing file: "+bse_id[i])
    h=open(f)
    lines=h.read().split("\n")
    lines=lines[1:]
    args=[]
    for l in lines:
        if l !='':
            fields=l.split(",")
            if len(fields[0].split("-")[1])>2:
                y=fields[0].split("-")[1]
            else:
                y="20"+fields[0].split("-")[1]
            m=mon_to_n(fields[0].split("-")[0][0:3])
            o=fields[1] if fields[1]!='' else '0'
            h=fields[2] if fields[2]!='' else '0'
            l=fields[3] if fields[3]!='' else '0'
            c=fields[4] if fields[4]!='' else '0'
            n=fields[5] if fields[5]!='' else '0'
            d=fields[8] if fields[8]!='' else '0'
            dp=fields[9] if fields[9]!='' else '0'
            sh=fields[10] if fields[10]!='' else '0'
            so=fields[11] if fields[11]!='' else '0'
            temp=(int(bse_id[i]),int(m),int(y),float(o),float(h),float(l),float(c),int(n),int(d),float(dp),float(sh),float(so),int(m),int(y))
            args.append(temp)

    cur=con.cursor()
    try:
        stmt = "INSERT INTO montly_price (stock_id, month,year,open,high,low,close,no_of_shares,delivery_quantity,delivery_percentage,spread_high_low,spread_open_close,qtr) VALUES (get_stock_name(%s), %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,get_qtr(%s,%s,'latest')+1)"
        cur.executemany(stmt, args)
        cur.execute("commit;")
    finally:
        cur.close()
       # if con.is_connected():
       #     con.close()
con.close()

