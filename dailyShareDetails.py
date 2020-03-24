import utils
import quoteData,pledgedData,financeData,shareHoldingData
con=None

ANNOUNCEMENT_URL="https://www1.nseindia.com/live_market/dynaContent/live_watch/get_quote/companySnapshot/getAnnouncements{NSE_ID}.json"
CORP_ACTION_URL="https://www1.nseindia.com/live_market/dynaContent/live_watch/get_quote/companySnapshot/getCorporateActions{NSE_ID}.json"

def get_announcement(nse_id):
    resp=utils.get_data(ANNOUNCEMENT_URL.format(NSE_ID=nse_id))
    return resp.json()

def get_corp_action(nse_id):
    resp=utils.get_data(CORP_ACTION_URL.format(NSE_ID=nse_id))
    return resp.json()

try:    
    con=utils.get_db_connection()
    quoteData.process_quote(con)
    financeData.process_finance(con)
    shareHoldingData.process_shareholding(con)
    pledgedData.process_pledge(con)
    utils.send_message("S","Successfully scrapped data for daily_stock_price_details.")
    
except Exception as e:
    print(e)
    utils.send_message("E","There was an error scrapping data for daily_stock_price_details. Error is {error}".format(error=e))
finally:
    con.close()
