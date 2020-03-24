from flask import render_template, url_for,request,jsonify,make_response,Blueprint
import utils

bp=Blueprint("mutualfunds",__name__,url_prefix="/mutualfunds")

def get_db_connection():
    return utils.get_db_connection()

@bp.route('/',methods=['GET'])
def mutualFunds():
    token=request.cookies.get("token")
    amcs=get_all_amc_from_db()
    resp=make_response(render_template('mf/mutualFunds.html',amcs=amcs,login=False,mf_class="active",eq_class="none",tokenIn=token))
    return resp

def get_all_amc_from_db():
    con=get_db_connection()
    try:
        results=[]
        cursor = con.cursor()
        cursor.callproc('get_all_amcs',tuple())
        for r in cursor.stored_results():
            for row in r:
                results.append(dict(zip(r.column_names,row)))
    finally:
        cursor.close()
    return results


def get_scheme_nav_from_db(args):
    con=get_db_connection()
    try:
        results=[]
        cursor = con.cursor()
        cursor.callproc('get_scheme_nav',args)
        for r in cursor.stored_results():
            for row in r:
                results.append(dict(zip(r.column_names,row)))
    finally:
        cursor.close()
    return results

def get_scheme_cat_from_db(args):
    con=get_db_connection()
    try:
        results=[]
        cursor = con.cursor()
        cursor.callproc('get_scheme_category',args)
        for r in cursor.stored_results():
            for row in r:
                results.append(dict(zip(r.column_names,row)))
    finally:
        cursor.close()
    return results

def get_mf_nav_from_db(args):
    con=get_db_connection()
    try:
        results1=[]
        results2=[]
        cursor = con.cursor()
        cursor.callproc('get_mutual_funds_nav',args)
        for i,r in enumerate(cursor.stored_results()):
            for row in r:
                if i==0:
                    results1.append(dict(zip(r.column_names,row)))
                else:
                    results2.append(dict(zip(r.column_names,row)))
    finally:
        cursor.close()
    return results1,results2

@bp.route("/schemeCat/<int:amc1>/<int:amc2>")
def get_scheme_category(amc1,amc2):
    scheme_cat=get_scheme_cat_from_db((amc1,amc2))
    return jsonify(scheme_cat)
 
@bp.route("/schemeNav/<int:amc1>/<int:amc2>/<int:scheme_cat_id>")
def get_scheme_nav(amc1,amc2,scheme_cat_id):
    scheme_nav=get_scheme_nav_from_db((amc1,amc2,scheme_cat_id))
    return jsonify(scheme_nav)

@bp.route("/performance/<int:code1>/<int:code2>/<int:days>")
def get_mf_nav(code1,code2,days):
    mf_nav=get_mf_nav_from_db((code1,code2,days))
    return jsonify(mf_nav)
