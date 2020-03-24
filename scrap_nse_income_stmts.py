import selenium.webdriver as webdriver
from selenium.webdriver.common.proxy import Proxy,ProxyType
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
from mysql.connector.errors import IntegrityError
from selenium.webdriver.chrome.options import Options
import mysql.connector as db
import js2py
import json
import datetime
import urllib.request as requests
import app_config


capabilities=DesiredCapabilities.CHROME.copy()

myProxy = "http://173.245.239.12:17145"

proxy = Proxy({
'proxyType': ProxyType.MANUAL,
'httpProxy': myProxy,
'ftpProxy': myProxy,
'sslProxy': myProxy,
'noProxy':''})

proxy.add_to_capabilities(capabilities)

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument("--disable-extensions")
driver=webdriver.Chrome(chrome_options=options,desired_capabilities=capabilities)
con=db.connect(host=app_config.DB_HOST,user=app_config.DB_USER,password=app_config.DB_PASS,auth_plugin='mysql_native_password',database=app_config.DB_NAME)

def get_nse_stocks():
    f=open("C:\\Users\\manju\\Desktop\\nse_stocks.txt")
    nse_stocks=[]
    for id in f:
        nse_stocks.append(id.split(",")[0])
    return nse_stocks

def get_all_last_1_months(start,limit):
    out={"rows":[]}
    try:
        url="https://www.nseindia.com/corporates/corpInfo/equities/getFinancialResults.jsp?start={start}&limit={limit}&symbol=&industry=&period=Quarterly&broadcastPeriod=Last%203%20Months".format(start=start,limit=limit)
        #headers={'mode': 'no-cors','User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Mobile Safari/537.36','Content-Type': 'text/html;charset=ISO-8859-1','Host':'www.nseindia.com'}
        req = requests.Request(url, None)
        response = requests.urlopen(req)
        the_page = response.read()
        js="function a() {return JSON.stringify("+the_page.decode("ascii")+")} a()"
        out=json.loads(js2py.eval_js(js))
        insert_log((0,0,0,'NSE','SEARCHINFO',None,url,str(out)))
    except Exception as e:
        insert_log((0,0,0,'NSE','CRITICAL',None,url,"Error getting all 1 month search, "+str(e))) 
    return out

def merge_or_get_stock(p):
    try:        
        cursor = con.cursor()
        results=cursor.callproc('merge_or_get_stock',(p["Symbol"],p["CompanyName"],p["ISIN"],0))
    finally:
        cursor.close()
        if con.is_connected():
            #con.close()
            pass
    return results[-1]

def process_search_monthly(serch_results):
    for p in serch_results["rows"]:
        stock_id=merge_or_get_stock(p)
        processed_flag=already_processed(stock_id)
        if processed_flag=="N":
            url=get_params_url(p)
            grab_and_save_details(url,{"stock_id":stock_id},p)

def get_quarterly_income_data():
    #eventhough we are getting quarterly data, we get all companies which announced results in last 1 month,
    #and oly insert those we did not process already
    batch_size=40
    counter=0
    flag=True
    while flag:
        results=get_all_last_1_months(counter,batch_size)
        num_of_results=results["results"]
        process_search_monthly(results)
        counter +=batch_size
        if counter>=num_of_results:
            flag=False
        
def get_last_24_months(nse_id,stock):
    out={"rows":[]}
    try:
        url="https://www.nseindia.com/corporates/corpInfo/equities/getFinancialResults.jsp?symbol={nse_id}&industry=&period=Quarterly&broadcastPeriod=Last%2024%20Months".format(nse_id=nse_id)
        driver.get(url)
        js="function a(){return JSON.stringify("+driver.find_element_by_css_selector("html body").text+")} a()"
        out=json.loads(js2py.eval_js(js))
        insert_log((stock["stock_id"],0,0,'NSE','SEARCHINFO',None,url,str(out)))
    except Exception as e:
        insert_log((stock["stock_id"],0,0,'NSE','CRITICAL',None,url,"Error getting last 24 month search, "+str(e))) 
    return out

def get_beyond_24_months(nse_id,stock):
    out={"rows":[]}
    try:
        url="https://www.nseindia.com/corporates/corpInfo/equities/getFinancialResults.jsp?symbol={nse_id}&industry=&period=Quarterly&broadcastPeriod=More%20than%2024%20Months".format(nse_id=nse_id)
        driver.get(url)
        js="function a(){return JSON.stringify("+driver.find_element_by_css_selector("html body").text+")} a()"
        out=json.loads(js2py.eval_js(js))
        insert_log((stock["stock_id"],0,0,'NSE','SEARCHINFO',None,url,str(out)))
    except Exception as e:
        insert_log((stock["stock_id"],0,0,'NSE','CRITICAL',None,url,"Error getting beyond 24 month search, "+str(e)))
    return out


def qtr_to_qtrid(param):
    if param["RelatingTo"]=="First Quarter":
        return "Q1"
    elif param["RelatingTo"]=="Second Quarter":
        return "Q2"
    elif  param["RelatingTo"]=="Third Quarter":
        return "Q3"
    else:
        return "Q4"

def get_audited(param):
    if param["Audited"]=="Audited":
        return "A"
    else:
        return "N"

def get_cumulative(param):
    if param["Cumulative"]=="Cumulative":
        return "C"
    else:
        return "N"

def get_consolidated(param):
    if param["Consolidated"]=="Consolidated":
        return "C"
    else:
        return "N"

def get_todate(p):
    d=p["ToDate"][0:2]
    m=mon_to_n(p["ToDate"][3:6])
    y=p["ToDate"][7:]
    return datetime.date(int(y),int(m),int(d))

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

def get_params_url(param):
    base_url="https://www.nseindia.com/corporates/corpInfo/equities/results_Nxbrl.jsp?param={from_date}{to_date}{quarter}{audited}{bank_flag}{cumulative}{consolidated}NE{nse_id}&seq_id={seq_id}&industry=-&viewFlag=N&frOldNewFlag={old_new_flag}"
    base_url=base_url.format(from_date=param["FromDate"],to_date=param["ToDate"],quarter=qtr_to_qtrid(param),audited=get_audited(param),bank_flag=param["Bank"],cumulative=get_cumulative(param),consolidated=get_consolidated(param),nse_id=param["Symbol"],seq_id=param["SeqNumber"],old_new_flag=param["fr_oldNewFlag"])
    return base_url

def get_table_2(url,stock,p):
    try:
        not_allowed=["Total","Total profit before tax"]
        table2=driver.find_element_by_xpath("/html/body/table/tbody/tr/td/table/tbody/tr/td[2]/p/table/tbody/tr/td[2]/table/tbody/tr/td/table")
        headings=table2.find_elements_by_css_selector("tbody tr :not(.tablehead) b")
        rows_with_headings=table2.find_elements_by_css_selector("tbody tr")
        rows_with_headings=rows_with_headings[1:]
        rows_with_headings=[h for h in rows_with_headings if not (h.text.startswith("Notes") or h.text.startswith("Disclosure of notes"))]
        heading_text=[h.text for h in headings if not h.text.startswith("Total")]
        headings_index=[i for i,value in enumerate(rows_with_headings) if value.text in heading_text]
        heading=None
        h_index=0
        for i,v in enumerate(rows_with_headings):
            if i in headings_index:
                heading=heading_text[h_index]
                h_index+=1
                continue
            tds=v.find_elements_by_tag_name("td")
            if tds[0].text not in not_allowed or not (tds[0].text.startswith("Disclosure of notes") or tds[0].text.startswith("Notes")):
                tds1= '0' if tds[1].text=="-" else tds[1].text
                todate=get_todate(p)
                insert_income_statements((int(stock["stock_id"]),todate.month,todate.year,tds[0].text,float(tds1),'A',heading,'NSE',0),url,p)
    except NoSuchElementException as e:
        todate=get_todate(p)
        insert_log((stock["stock_id"],todate.month,todate.year,'NSE','BATCHERR',str(p),url,"No table 2 Error: "+str(e.args)))

def get_table_1(url,stock,p):
    try:
        not_allowed=["Part I","Description","Notes To Accounts","Disclosure of notes on financial results"]
        table1=driver.find_element_by_xpath("/html/body/table/tbody/tr/td/table/tbody/tr/td[2]/p/table/tbody/tr/td[1]/table/tbody/tr/td/table")
                                            # /html/body/table/tbody/tr/td/table/tbody/tr/td[2]/p/table/tbody/tr/td/table/tbody/tr/td/table
        headings=table1.find_elements_by_css_selector("tbody tr b :not(.t1)")
        rows_with_headings=table1.find_elements_by_css_selector("tbody tr")
        heading_text=[h.text for h in headings]    
        headings_index=[i for i,value in enumerate(rows_with_headings) if value.text in heading_text]

        heading=None
        h_index=0
        for i,v in enumerate(rows_with_headings):
            if i in headings_index:
                heading=heading_text[h_index]
                h_index+=1
                continue
            tds=v.find_elements_by_tag_name("td")
            if tds[0].text not in not_allowed or not (tds[0].text.startswith("Disclosure of notes") or tds[0].text.startswith("Notes")) :
                tds1= '0' if tds[1].text=="-" else tds[1].text
                todate=get_todate(p)
                if not tds1.startswith("Amount(Rs. in lakhs)"):
                    insert_income_statements((int(stock["stock_id"]),todate.month,todate.year,tds[0].text,float(tds1),'A',heading,'NSE',0),url,p)
    except NoSuchElementException as e:
        todate=get_todate(p)
        insert_log((stock["stock_id"],todate.month,todate.year,'NSE','BATCHERR',str(p),url,"No table 1 Error: "+str(e.args))) 

def grab_and_save_details(url,stock,p):    
    headers={'mode': 'no-cors','User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    req = requests.Request(url, None, headers)
    response = requests.urlopen(req)
    the_page = response.read()
    with open("C:\\Users\\manju\\OneDrive\\Documents\\temp.html","w+") as f:
        f.write(the_page.decode("utf-8"))    
    driver.get("C:\\Users\\manju\\OneDrive\\Documents\\temp.html")
    get_table_1(url,stock,p)
    get_table_2(url,stock,p)
    

def process_search_results(serch_results,stock):
    for p in serch_results["rows"]:
        url=get_params_url(p)
        grab_and_save_details(url,stock,p)

def fetch_all_stocks():
    try:
        results=[]
        cursor = con.cursor()
        cursor.callproc('fetch_all_stocks',())
        for r in cursor.stored_results():
            for row in r:
                results.append(dict(zip(r.column_names,row)))
    finally:
        cursor.close()
    return results

def already_processed(stock_id):
    try:        
        cursor = con.cursor()
        results=cursor.callproc('already_processed',(stock_id,0))

    finally:
        cursor.close()
        if con.is_connected():
            #con.close()
            pass
    return results[-1]

def insert_log(args):
    try:
        cursor = con.cursor()
        cursor.callproc('insert_income_batch_log',args)
    finally:
        cursor.close()

#process
def insert_income_statements(args,url,p):
    #con=db.connect(host="localhost",user="<your user>",password="<your pwd>",auth_plugin='mysql_native_password',database="<your DB>")
    try:        
        cursor = con.cursor()
        results=cursor.callproc('insert_income_statements',args)

        if results[-1]=="E":
            insert_log((args[0],args[1],args[2],'NSE','BATCHERR',p,url,args))
    
    except IntegrityError:
        pass
    except Exception as e:
        insert_log((args[0],args[1],args[2],'NSE','BATCHERR',str(p),url,str(args)+", Error: "+str(e.args)))
        raise
    finally:
        cursor.close()
        if con.is_connected():
            #con.close()
            pass

def start_batch(type):
    try:
        if type=="batch":
            stocks=fetch_all_stocks()
            for stock in stocks:
                flag=already_processed(stock["stock_id"])
                if flag=='N':
                    process_search_results(get_last_24_months(stock["nse_id"],stock),stock)
                    process_search_results(get_beyond_24_months(stock["nse_id"],stock),stock)
        else:
            get_quarterly_income_data()

    finally:
        if con.is_connected():
            con.close()
            driver.close()

"""
1st AUdited = A or U
2nd Bank flag = N or A or anything in that flag
3rd cumulative = C or N
4th consolidated = C or N
5th anything
6th  E,A,, segment table will be on or off for this
"""
try:
    start_batch("monthly")
finally:
    con.close()
