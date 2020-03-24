import datetime
import json
import math
import re
import utils

URL="https://www.nseindia.com/api/quote-equity?symbol={nse_id}&section=corp_info"
error_stocks=[]

def fetch_all_stocks_to_process(con):
    try:
        results=[]
        cursor = con.cursor()
        cursor.callproc('get_not_processed_corpinfo_daily',())
        for r in cursor.stored_results():
            for row in r:
                results.append(dict(zip(r.column_names,row)))
    finally:
        cursor.close()
    return results


def insert_announcement(rows,con):
    cur=con.cursor()
    try:
        stmt = "INSERT IGNORE INTO announcements (stock_id,Descr,attchmntText,attchmntFile,an_dt,process_date) values(%s,%s,%s,%s,%s,date(now()))"
        cur.executemany(stmt, rows)
        cur.execute("commit;")
    except Exception as e:
        cur.execute("rollback;")
        utils.log(3,"Error while inserting data into announcements, values are: "+str(e)+", details: "+str(rows))
        raise
    finally:
        cur.close()

def insert_board_meeting(rows,con):
    cur=con.cursor()
    try:
        stmt = "INSERT IGNORE INTO board_meetings (stock_id,bm_purpose,bm_desc,bm_attachment,bm_date,process_date) values(%s,%s,%s,%s,%s,date(now()))"
        cur.executemany(stmt, rows)
        cur.execute("commit;")
    except Exception as e:
        cur.execute("rollback;")
        utils.log(3,"Error while inserting data into board_meetings, values are: "+str(e)+", details: "+str(rows))
        raise
    finally:
        cur.close()

def insert_corp_actions(rows,con):
    cur=con.cursor()
    try:
        stmt = "INSERT IGNORE INTO corp_actions (stock_id,faceval,subject,ex_date,rec_date,bc_start_date,bc_end_date,nd_start_date,nd_end_date,process_date) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,date(now()))"
        cur.executemany(stmt, rows)
        cur.execute("commit;")
    except Exception as e:
        cur.execute("rollback;")
        utils.log(3,"Error while inserting data into board_meetings, values are: "+str(e)+", details: "+str(rows))
        raise
    finally:
        cur.close()

def insert_sast(rows,con):
    cur=con.cursor()
    try:
        stmt = "INSERT IGNORE INTO sast_reg (stock_id,reg_type,aquirer_name,aquirer_date,no_of_shares_quuired,no_of_share_sale,no_share_after,attachment,date_of_disc,process_date) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,date(now()))"
        cur.executemany(stmt, rows)
        cur.execute("commit;")
    except Exception as e:
        cur.execute("rollback;")
        utils.log(3,"Error while inserting data into board_meetings, values are: "+str(e)+", details: "+str(rows))
        raise
    finally:
        cur.close()

def save_announcements(data,stock,con):
    ann=data["corporate"]["announcements"]
    rows=[]
    for d in ann:
        rows.append((stock["stock_id"],d["desc"],d["attchmntText"],d["attchmntFile"],utils.correct_null(d["an_dt"])))
    insert_announcement(rows,con)

def save_board_meeting(data,stock,con):
    ann=data["corporate"]["boardMeetings"]
    rows=[]
    for d in ann:
        rows.append((stock["stock_id"],d["bm_purpose"],d["bm_desc"],d["attachment"],utils.correct_null(d["bm_date"])))
    insert_board_meeting(rows,con)

def save_corp_actions(data,stock,con):
    ann=data["corporate"]["corporateActions"]
    rows=[]
    for d in ann:
        rows.append((stock["stock_id"],int(d["faceVal"]),d["subject"],utils.correct_null(d["exDate"]),utils.correct_null(d["recDate"]),utils.correct_null(d["bcStartDate"]),utils.correct_null(d["bcEndDate"]),utils.correct_null(d["ndStartDate"]),utils.correct_null(d["ndEndDate"])))
    insert_corp_actions(rows,con)

def save_sast(data,stock,con):
    ann=data["corporate"]["sastRegulations_29"]
    rows=[]
    for d in ann:
        rows.append((stock["stock_id"],d["regType"],d["acquirerName"],utils.correct_null(d["acquirerDate"]),int(d["noOfShareAcq"] if d["noOfShareAcq"] else 0),int(d["noOfShareSale"] if d["noOfShareSale"] else 0),int(d["noOfShareAft"] if d["noOfShareAft"] else 0),d["attachement"],utils.correct_null(d["timestamp"])))
    insert_sast(rows,con)

def fetch(stock,con):
    global error_stocks
    try:
        data=utils.get_data(URL.format(nse_id=stock["nse_id"])).json()
        if utils.checkKey(data,"corporate"):
            save_announcements(data,stock,con)
            save_board_meeting(data,stock,con)
            save_corp_actions(data,stock,con)
            save_sast(data,stock,con)
    except Exception as e:
        utils.log(3,"Could not insert data for "+stock["nse_id"]+", error: "+str(e))   
        error_stocks.append(stock["nse_id"])     
    finally:
        pass
     
def process_corp_info():
    global error_stocks
    try:
        con=utils.get_db_connection()
        stocks_to_process=fetch_all_stocks_to_process(con)
        for stock in stocks_to_process:
            fetch(stock,con)
        utils.send_message("S","Successfully scrapped data for corp info. error for "+str(error_stocks))
    except Exception as e:
        utils.log(3,"Could not insert data corp info, error: "+str(e))    
        utils.send_message("S","Unable to process corp info, please check batch_log for details")
    finally:
        print(error_stocks)
        con.close()
    
process_corp_info()
