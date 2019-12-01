import mysql.connector as db
from mysql.connector.errors import IntegrityError

con=db.connect(host="localhost",user="<your user>",password="<your pwd>",auth_plugin='mysql_native_password',database="<your DB>")
main_id=0
current_nse_id=""

def fetch_all_stocks():
    try:
        results=[]
        nse_results=[]
        cursor = con.cursor()
        cursor.callproc('fetch_mege_stocks',())
        for i,r in enumerate(cursor.stored_results()):
            if i==0:
                for row in r:
                    results.append(dict(zip(r.column_names,row)))
            else:
                for row in r:
                    nse_results.append(dict(zip(r.column_names,row)))

    finally:
        cursor.close()
    return results,nse_results

def filterNSE(nse):
    global current_nse_id
    return nse["nse_id"]==current_nse_id

def notMainID(row):
    global main_id
    return row["stock_id"]!=main_id
def MainID(row):
    global main_id
    return row["stock_id"]==main_id

def getMax(rows):
    global main_id
    count=0
    for r in rows:        
        if r["dup_count"]>count:
            count=r["dup_count"]
            main_id=r["stock_id"]

def merge_stocks(m,s):
    try:
        cursor = con.cursor()
        cursor.callproc('merge_duplicate_stocks',(m,s))
    finally:
        cursor.close()

res,nse=fetch_all_stocks()

for i,u in enumerate(nse):
    for i in[1,2]:
        
        current_nse_id=u["nse_id"]
        print("processing...."+current_nse_id)
        chunk=filter(filterNSE,res)
        chunk=list(chunk)
        getMax(chunk)
        main=list(filter(MainID,chunk))
        notMain=list(filter(notMainID,chunk))

        for al in notMain:
            merge_stocks(main[0]["stock_id"],al["stock_id"])

con.close()

