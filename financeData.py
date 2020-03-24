import datetime
import json
import math
import re
import utils

FINANCIAL_RESULTS_URL="https://www1.nseindia.com/live_market/dynaContent/live_watch/get_quote/companySnapshot/getFinancialResults{NSE_ID}.json"


def get_fin_results(nse_id):
    resp=utils.get_data(FINANCIAL_RESULTS_URL.format(NSE_ID=nse_id))
    if resp.status_code==404:
        return None
    return resp.json()


def insert_income_statements(args,con):
    #con=db.connect(host="localhost",user="<your user>",password="<your pwd>",auth_plugin='mysql_native_password',database="<your DB>")
    try:
        cursor = con.cursor()
        cursor.callproc('insert_income_statements_json',(args,0))

    except Exception as e:
        utils.log(2,"Error processing json data in insert_income_statements: "+", error: "+str(e))
        raise
    finally:
        cursor.close()
        if con.is_connected():
            #con.close()
            pass
def getIncomeStmtName(fin_data,key):
    if utils.checkKey(fin_data,key):
        if key=="expenditure":
            return ("Total Expenses","Expenses",fin_data["expenditure"])
        if key=="income":
            return ("Revenue from operations","Revenue from operations",fin_data["income"])
        if key=="reProLossBefTax":
            return ("Profit / (Loss) before tax","Expenses",fin_data["reProLossBefTax"])
        if key=="proLossAftTax":
            return ("Consolidated Net Profit/Loss for the period","Revenue from operations",fin_data["proLossAftTax"])
        if key=="reDilEPS":
            return ("Diluted EPS for continuing operations","Earnings per equity share for continuing operations",fin_data["reDilEPS"])
    else:
        return None

def process_fin_data(items,con):
    json_args=[]
    for d in items:
        json_items={}
        fin_data=get_fin_results(d["nse_id"])
        print("processing fin: "+d["nse_id"])
        
        if fin_data:
            if utils.checkKey(fin_data,"results0"):
                results0=fin_data["results0"]
                month=utils.mon_to_n(results0["toDate"].split()[1].strip())
                year=results0["toDate"].split()[2].strip()
                for key in ["expenditure","income","reProLossBefTax","proLossAftTax","reDilEPS"]:
                    args= getIncomeStmtName(results0,key)
                    json_items={"stock_id":d["stock_id"],"month":int(month),"year":int(year),"stmt_name":args[0],"stmt_value":utils.format_num(args[2]),"stmt_cat":args[1],"status":"A","exchange":"NSE"}
                    json_args.append(json_items)
            if utils.checkKey(fin_data,"results1"):
                results1=fin_data["results1"]
                month=utils.mon_to_n(results1["toDate"].split()[1].strip())
                year=results1["toDate"].split()[2].strip()
                for key in ["expenditure","income","reProLossBefTax","proLossAftTax","reDilEPS"]:
                    args= getIncomeStmtName(results1,key)
                    json_items={"stock_id":d["stock_id"],"month":int(month),"year":int(year),"stmt_name":args[0],"stmt_value":utils.format_num(args[2]),"stmt_cat":args[1],"status":"A","exchange":"NSE"}
                    json_args.append(json_items)
    insert_income_statements(json.dumps(json_args),con)

def fetch_fin_stocks_to_process(con):
    try:
        results=[]
        cursor = con.cursor()
        cursor.callproc('get_not_processed_fin_stocks',())
        for r in cursor.stored_results():
            for row in r:
                results.append(dict(zip(r.column_names,row)))
    finally:
        cursor.close()
    return results
    

def process_finance(con):
    try:
        BATCH_NO=25
        counter=0
        stocks_to_process=fetch_fin_stocks_to_process(con)
        stocks_to_process=stocks_to_process[0:15]
        total=len(stocks_to_process)
        while(counter<=total):
            if len(stocks_to_process[counter:counter+BATCH_NO])>0:
                process_fin_data(stocks_to_process[counter:counter+BATCH_NO],con)            
                print("processed fin {r} rows".format(r=counter))
            counter+=BATCH_NO
    except Exception as e:
        utils.log(2,"Fatal error in processing finance, "+str(e))


