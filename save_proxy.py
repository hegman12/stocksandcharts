import requests
import mysql.connector as db
import re
def next_proxy():
    con=db.connect(host="localhost",user="<your user>",password="<your pwd>",auth_plugin='mysql_native_password',database="<your DB>")
    try:        
        cursor = con.cursor()
        results=cursor.callproc('next_proxy',(0,))

    finally:
        cursor.close()
        if con.is_connected():
            con.close()
            
    return results[-1]

def save_proxy(proxy):
    con=db.connect(host="localhost",user="<your user>",password="<your pwd>",auth_plugin='mysql_native_password',database="<your DB>")
    try:        
        cursor = con.cursor()
        cursor.callproc('save_proxy',(proxy,))

    finally:
        cursor.close()
        if con.is_connected():
            con.close()
            
    return "success"

def update_proxy(proxy):
    con=db.connect(host="localhost",user="<your user>",password="<your pwd>",auth_plugin='mysql_native_password',database="<your DB>")
    try:        
        cursor = con.cursor()
        cursor.callproc('ban_proxy',(proxy,))

    finally:
        cursor.close()
        if con.is_connected():
            con.close()
            
    return "success"

h=requests.get("http://spys.me/proxy.txt")

pattern=r"^[0-9]"
format=re.compile(pattern)

for l in h.text.split("\n"):
    #if format.match(l.split("\t")[0]):
    if l !="":
        print(format.match(l.split()[0]))
