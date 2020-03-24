
import json
import math
import re
import utils

PLEDGE_URL="https://www1.nseindia.com/live_market/dynaContent/live_watch/get_quote/companySnapshot/getPledgeDisclosuresDetails{NSE_ID}.json"

def get_pledge(nse_id):
    resp=utils.get_data(PLEDGE_URL.format(NSE_ID=nse_id))
    if resp.status_code==404:
        return None
    return resp.json()

def fetch_pledge_stocks_to_process(con):
    try:
        results=[]
        cursor = con.cursor()
        cursor.callproc('get_notprocessed_pledge_stocks',())
        for r in cursor.stored_results():
            for row in r:
                results.append(dict(zip(r.column_names,row)))
    finally:
        cursor.close()
    return results

def process_pledge(con):
    try:
        BATCH_NO=100
        counter=0
        stocks_to_process=fetch_pledge_stocks_to_process(con)
        total=len(stocks_to_process)
        while(counter<=total):
            if len(stocks_to_process[counter:counter+BATCH_NO])>0:
                process_pledge_data(stocks_to_process[counter:counter+BATCH_NO],con)            
            counter+=BATCH_NO
    except Exception as e:
        utils.log(2,"Fatal error in processing daily stock shaholding details, "+str(e))

def process_pledge_data(items,con):
    json_args=[]
    for d in items:
        data=get_pledge(d["nse_id"])
        if data:
            if utils.checkKey(data,"rows"):
                rows=data["rows"]
                for row in rows:
                    pattern_month=utils.mon_to_n(row["disclosureDate"].split("-")[1])
                    pattern_year=row["disclosureDate"].split("-")[2]
                    pattern_day=row["disclosureDate"].split("-")[0]
                    per1=row["per1"]
                    per2=row["per2"]
                    per3=row["per3"]
                    json_args.append({"stock_id":d["stock_id"],"disclosureDate":pattern_day+"-"+str(pattern_month)+"-"+pattern_year,"per1":utils.format_num(per1),"per2":utils.format_num(per2),"per3":utils.format_num(per3)})
    insert_pledge_data(json.dumps(json_args),con)
    

def insert_pledge_data(args,con):
    #con=db.connect(host="localhost",user="<your user>",password="<your pwd>",auth_plugin='mysql_native_password',database="<your DB>")
    try:
        cursor = con.cursor()
        cursor.callproc('insert_pledged_json',(args,0))

    except Exception as e:
        utils.log(2,"Error processing json data in pledge data: "+", error: "+str(e))
        raise
    finally:
        cursor.close()
        if con.is_connected():
            #con.close()
            pass