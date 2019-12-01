import selenium.webdriver as webdriver
from selenium.webdriver.common.proxy import Proxy,ProxyType
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
from mysql.connector.errors import IntegrityError
from selenium.webdriver.chrome.options import Options
import mysql.connector as db
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os import listdir
from os.path import isfile, join
from selenium.common.exceptions import TimeoutException as TimeoutException

options = webdriver.ChromeOptions()
options.add_argument('user-data-dir=D:\\stock_prices')
driver=webdriver.Chrome(chrome_options=options)

con=db.connect(host="localhost",user="<your user>",password="<your pwd>",auth_plugin='mysql_native_password',database="<your DB>")
driver.get("https://www.bseindia.com/markets/equity/EQReports/StockPrcHistori.aspx?flag=0")

def fetch_all_stocks():
    try:
        results=[]
        cursor = con.cursor()
        cursor.callproc('fetch_all_bse_stocks',())
        for r in cursor.stored_results():
            for row in r:
                results.append(dict(zip(r.column_names,row)))
    finally:
        cursor.close()
        con.close()
    return results

stocks=fetch_all_stocks()

onlyfiles = [f for f in listdir("C:\\Users\\manju\\Downloads") if isfile(join("C:\\Users\\manju\\Downloads", f))]
bse_id=[s.split(".")[0] for s in onlyfiles if s.split(".")[1]=="csv"]

for stock in stocks:
    try:
        if str(stock["bse_id"]) not in bse_id and str(stock["bse_id"])[0]!="9":
            driver.find_element_by_xpath("//*[@id='ContentPlaceHolder1_rdbMonthly']").click()
            driver.find_element_by_xpath("//select[@id='ContentPlaceHolder1_cmbMonthly']/option[text()='Jan']").click()
            driver.find_element_by_xpath("//select[@id='ContentPlaceHolder1_cmbMYear']/option[text()='2010']").click()
            element=driver.find_element_by_xpath("//*[@id='ContentPlaceHolder1_smartSearch']")
            element.clear()
            element.send_keys(stock["bse_id"])
            try:
                element = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='ulSearchQuote2']/li"))
                )
                driver.find_element_by_xpath( "//*[@id='ulSearchQuote2']/li").click()
                
            finally:
                #driver.quit()
                pass
            driver.find_element_by_xpath("//*[@id='ContentPlaceHolder1_btnSubmit']").click()
            try:
                element = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='ContentPlaceHolder1_btnDownload1']"))
                )
                driver.find_element_by_xpath("//*[@id='ContentPlaceHolder1_btnDownload1']").click()
                
            finally:
                #driver.quit()
                pass
    except TimeoutException:
        pass
driver.quit()
