import datetime
import json
import math
import re
import utils

MULTI_QUOTE_URL="https://www1.nseindia.com/live_market/dynaContent/live_watch/get_quote/ajaxGetQuoteJSON.jsp?symbol={NSE_ID}"
PE_URL="https://www1.nseindia.com/live_market/dynaContent/live_watch/get_quote/getPEDetails.jsp?symbol={NSE_ID}"
TOTAL_SHARES_URL="https://www1.nseindia.com/marketinfo/companyTracker/compInfo.jsp?symbol={NSE_ID}&series=EQ"


def get_quotes(nse_ids):
    resp=utils.get_data(MULTI_QUOTE_URL.format(NSE_ID=nse_ids))
    return resp.json()["data"]

def get_pe(nse_id):
    resp=utils.get_data(PE_URL.format(NSE_ID=nse_id))
    r=resp.json()
    if r is None:
        r={"PE":0,"sectorPE":0}
    return r

def get_total_shares(nse_id):
    resp=utils.get_data(TOTAL_SHARES_URL.format(NSE_ID=nse_id))
    t=resp.text
    start_ptr=t.rfind("Issued Cap.")
    t=t[start_ptr:]
    end_ptr=t.find("(shares)")
    t=t[:end_ptr]
    pattern="\\d+"
    ts=re.findall(pattern,t)
    if len(ts)>0:
        return int(ts[0])
    else:
        return 0

def fetch_all_stocks_to_process(con):
    try:
        results=[]
        cursor = con.cursor()
        cursor.callproc('get_not_processed_nseprice_daily',())
        for r in cursor.stored_results():
            for row in r:
                results.append(dict(zip(r.column_names,row)))
    finally:
        cursor.close()
    return results

def get_freefloat_shares(market_cap,price):
    return round((float(market_cap)*10000000)/float(price),2)

def insert_daily_stock_details(rows,con):
    cur=con.cursor()
    try:
        stmt = "INSERT IGNORE INTO stock_daily_details (stock_id,nse_id,close_price,ff_shares,ff_marketcap,promoter_shares,promoter_matketcap,low52,high52,day_low,day_high,open,delivery_percent,traded_volume,is_ex_date_flag,stock_pe,sector_pe,total_issued_shares,value_date) values(get_stock_id_nse(%s),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,date(now()))"
        cur.executemany(stmt, rows)
        cur.execute("commit;")
    except Exception as e:
        cur.execute("rollback;")
        utils.log(2,"Error while inserting data into stock_daily_details, values are: "+str(e)+", details: "+str(rows))
    finally:
        cur.close()

def getClosePrice(d):
    t1=utils.format_num(d["closePrice"])    
    if t1!=0:
        return t1
    else:
        t2=utils.format_num(d["previousClose"])
        if t2 !=0:
            return t2
        else:
            return 1

def getIsExitDateFlag(d):
    if utils.checkKey(d,"isExDateFlag"):
        return bool(d["isExDateFlag"])
    else:
        return False

def process(items):
    nse_ids=items[0]["nse_id"]
    for x in items[1:]:
        nse_ids=nse_ids+","+x["nse_id"]

    results=list()
    data=get_quotes(nse_ids)
    if data:
        for d in data:
            temp=list()
            close_price=getClosePrice(d)
            temp.append(d["symbol"])
            temp.append(d["symbol"])
            temp.append(close_price)
            fs=get_freefloat_shares(utils.format_num(d["cm_ffm"]),close_price)
            temp.append(round(fs/10000000,4))
            temp.append(utils.format_num(d["cm_ffm"]))
            ts=get_total_shares(d["symbol"])
            ps=ts-fs
            pmc=ps*close_price
            temp.append(round(ps/10000000,4))
            temp.append(round(pmc/10000000,2))
            temp.append(utils.format_num(d["low52"]))
            temp.append(utils.format_num(d["high52"]))
            temp.append(utils.format_num(d["dayLow"]))
            temp.append(utils.format_num(d["dayHigh"]))
            temp.append(utils.format_num(d["open"]))
            temp.append(utils.format_num(d["deliveryToTradedQuantity"]))
            temp.append(utils.format_num(d["totalTradedVolume"]))
            temp.append("Y" if getIsExitDateFlag(d) else "N")
            t=get_pe(d["symbol"])
            temp.append(utils.format_num(t["PE"]))
            temp.append(utils.format_num(t["sectorPE"]))
            temp.append(round(ts/10000000,4))
            results.append(temp)
    return results

def process_quote(con):
    try:
        BATCH_NO=5
        counter=0
        stocks_to_process=fetch_all_stocks_to_process(con)
        total=len(stocks_to_process)
        num_rows=0
        
        while(counter<=total):
            if len(stocks_to_process[counter:counter+BATCH_NO])>0:            
                rows=process(stocks_to_process[counter:counter+BATCH_NO])
                insert_daily_stock_details(rows,con)
                num_rows+=len(rows)
                
            counter+=BATCH_NO
    except Exception as e:
        utils.log(2,"Fatal error in processing quote , "+str(e))


