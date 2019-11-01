from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import mysql.connector as db

con=db.connect(host="localhost",user="<your user>",password="<your pwd>",auth_plugin='mysql_native_password',database="<your DB>")

def fetch_result_types():
    try:
        results=[]
        cursor = con.cursor()
        cursor.callproc('fetch_result_types',())
        for r in cursor.stored_results():
            for row in r:
                results.append(dict(zip(r.column_names,row)))
    finally:
        cursor.close()
    return results

def processor(p):
    return p["income_stmt_name"]
groups=[]
def get_next(choices):
    global groups
    t=[]
    for v in groups:
        t.append(v["main"])
        for vv in v["sub"]:
            t.append(vv)
    rr= [r for r in choices if r not in t]
    return rr
def get_matches(matches):
    return [v for v,_ in matches]

choices = fetch_result_types()

flag=True
while flag:
    c=get_next(choices)
    #print("++++++++++++++++++++++++++++",c)
    if len(c)>1:
        query=c[0]
        matches=process.extractBests(query,choices[1:],processor=processor,scorer=fuzz.partial_token_sort_ratio ,score_cutoff=100)
        
        
        if len(matches)>0:  mmn 
            print("query: ",query)
            print("maches: ",matches[1:])
            groups.append({"main":query,"sub":get_matches(matches[1:])})
        else:
            print("query: ",query)
            groups.append({"main":query,"sub":[]})
    else:
        if len(c)==1:                                                                                                                                                                                                                                                                                                bvc                                                                                                                                                                                                                                                        
            groups.append({"main":c[0],"sub":[]})
            flag=False
        else:
            flag=False
print(groups)
con.close()
