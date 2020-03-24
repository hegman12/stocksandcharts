import datetime
import json
import math
import re
import utils

SHARE_PATTERN_URL="https://www1.nseindia.com/live_market/dynaContent/live_watch/get_quote/companySnapshot/getShareholdingPattern{NSE_ID}.json"

def get_share_pattern(nse_id):
    resp=utils.get_data(SHARE_PATTERN_URL.format(NSE_ID=nse_id))
    if resp.status_code==404:
        return None
    return resp.json()

def fetch_shareholding_stocks_to_process(con):
    try:
        results=[]
        cursor = con.cursor()
        cursor.callproc('get_notprocessed_shareholding_stocks',())
        for r in cursor.stored_results():
            for row in r:
                results.append(dict(zip(r.column_names,row)))
    finally:
        cursor.close()
    return results

def process_shareholding(con):
    try:
        BATCH_NO=100
        counter=0
        stocks_to_process=fetch_shareholding_stocks_to_process(con)
        total=len(stocks_to_process)
        while(counter<=total):
            if len(stocks_to_process[counter:counter+BATCH_NO])>0:
                process_shareholding_data(stocks_to_process[counter:counter+BATCH_NO],con)            
            counter+=BATCH_NO
    except Exception as e:
        utils.log(2,"Fatal error in processing daily stock shaholding details, "+str(e))

def process_shareholding_data(items,con):
    json_args=[]
    for d in items:
        rows=get_share_pattern(d["nse_id"])
        if rows:
            if utils.checkKey(rows,"asOnDate"):
                try:
                    pattern_month=utils.mon_to_n(rows["asOnDate"][1].split("-")[1])
                    pattern_year=rows["asOnDate"][1].split("-")[2]
                    pattern_day=rows["asOnDate"][1].split("-")[0]
                    category=rows["category"]
                    holdingPercent=rows["holdingPercent"]
                    for index,data in enumerate(category):
                        json_args.append({"stock_id":int(d["stock_id"]),"pattern_date": pattern_day+"-"+str(pattern_month)+"-"+pattern_year,"pattern_name":data,"pattern_value":utils.format_num(holdingPercent[index])})
                except IndexError:
                    pass
    insert_shareholding_data(json.dumps(json_args),con)
    

def insert_shareholding_data(args,con):
    #con=db.connect(host="localhost",user="<your user>",password="<your pwd>",auth_plugin='mysql_native_password',database="<your DB>")
    try:
        cursor = con.cursor()
        cursor.callproc('insert_shareholding_pattern_json',(args,0))

    except Exception as e:
        utils.log(2,"Error processing json data in shareholding data: "+", error: "+str(e))
        raise
    finally:
        cursor.close()
        if con.is_connected():
            #con.close()
            pass