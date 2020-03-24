from flask import Flask, render_template, url_for,request,jsonify,g,make_response,Blueprint
import datetime
from flask_httpauth import HTTPBasicAuth,MultiAuth,HTTPTokenAuth
import base64
import random
import string
import utils

bp=Blueprint("api",__name__,url_prefix="/api",)

def get_db_connection():
    return utils.get_db_connection()

def verify_password(username, password):
    #con=db.connect(host="localhost",user="<your user>",password="<your pwd>",auth_plugin='mysql_native_password',database="<your DB>")
    if username=="hegde":
        return True    
    return False

#@token_auth.error_handler
def auth_error():
    return make_response()

#@token_auth.verify_token
def verify_token(token):
    ret=True
    try:
        validatedToken=validate_session((token,0))
        if validatedToken =="expired":
            return False
    except Exception:
        ret=False
        raise
        #con.close()
    finally:
        pass
        #con.close()
    return ret

def get_rc_from_db(args):
    con=get_db_connection()
    try:
        results=[]
        cursor = con.cursor()
        cursor.callproc('get_result_category_labels',args)
        for r in cursor.stored_results():
            for row in r:
                results.append(dict(zip(r.column_names,row)))
    finally:
        cursor.close()
    return results

@bp.route('/category/<int:stock_id>/<string:mode>/<int:no_of_qtr>')
#@token_auth.login_required
def get_result_category_labels(stock_id,mode,no_of_qtr):
    stockCompare=request.args.get('stockCompare',0)
    con=get_db_connection()
    category_labels=[]
    try:
        category_labels=get_rc_from_db((stock_id,int(stockCompare),no_of_qtr,mode))
    finally:
        if con.is_connected():
            pass
            #con.close()
    return jsonify(category_labels)

def get_type_from_db(args):
    con=get_db_connection()
    try:
        results=[]
        cursor = con.cursor()
        cursor.callproc('get_result_type_label',args)
        for r in cursor.stored_results():
            for row in r:
                results.append(dict(zip(r.column_names,row)))
    finally:
        cursor.close()
    return results


@bp.route('/type/<int:stock_id>/<string:mode>/<int:no_of_qtr>/<int:catID>')
#@token_auth.login_required
def get_result_type_labels(stock_id,mode,no_of_qtr,catID):
    stockCompare=request.args.get('stockCompare',0)
    con=get_db_connection()
    type_labels=[]
    try:
        type_labels=get_type_from_db((stock_id,int(stockCompare),no_of_qtr,mode,catID))
    finally:
        if con.is_connected():
            pass
            #con.close()

    return jsonify(type_labels)

@bp.route('/search/<string:search_string>')
#@token_auth.login_required
def get_stock_search_results(search_string):
    con=get_db_connection()
    try:
        cur=con.cursor(prepared=True)
        select_stmt = "SELECT stock_id,stock_name FROM stocks WHERE stock_name like %s or nse_id like %s or bse_id like %s"
        cur.execute(select_stmt, ( "%"+search_string+"%","%"+search_string+"%","%"+search_string+"%"))
        #cur.callproc('visualize.search_stock',(search_string,refcur))
        #for i,j in cur:
         #   print(i,j)
        out=[{'stockId':id,'stockName':name.decode("utf-8") } for id,name in cur]        
    finally:
        pass
        #con.close()
    return jsonify(out)

@bp.route('/graph/<int:stockID>')
#@token_auth.login_required
def get_graph_data(stockID):
    mode=request.args.get('mode',None)
    categoryId=request.args.get('categoryId',None)
    fromQtr=request.args.get('fromQtr',None)
    totalQtr=request.args.get('totalQtr',None)
    totalQtrIncome=request.args.get('totalQtrIncome',None)
    stmtTypeID=request.args.get('resultTypeId',None)
    secondaryStockID=request.args.get('secondaryStockID',None)
    price1=request.args.get('price1','N')
    price2=request.args.get('price2','N')
    con=get_db_connection()
    try:
        cur=con.cursor()
        cur.callproc('get_graph_data',(stockID,secondaryStockID,categoryId,stmtTypeID,mode,fromQtr,totalQtr,totalQtrIncome,price1,price2))
        results=[]
        price1=[]
        price2=[]
        for i,r in enumerate(cur.stored_results()):
            if i==0:
                for row in r:
                    results.append(dict(zip(r.column_names,row)))
            elif i==1:
                for row in r:
                    if request.args.get('price1','N')=="Y":
                        price1.append(dict(zip(r.column_names,row)))
                    else:
                        price2.append(dict(zip(r.column_names,row)))
            else:
                for row in r:
                    price2.append(dict(zip(r.column_names,row)))
        if mode !="S":
            out=[{'name':r["stock_id"],'year':r["period"],'value':float(r["value"])} for r in results]
        else:
            out=[{'year':r["period"],'value':float(r["value"])} for r in results]
    finally:
        pass
        #con.close()

    return jsonify(income=out,price1=price1,price2=price2)
