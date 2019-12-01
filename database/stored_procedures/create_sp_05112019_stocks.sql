DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` PROCEDURE `activate_user`(IN p_pending_id int,out p_message varchar(100))
BEGIN
declare l_email varchar(100);
DECLARE EXIT HANDLER FOR 1062
  BEGIN
set p_message="user already registered";
  END;

select email into l_email from activation_pending where id=p_pending_id;
insert into registered_user(email) values(l_email);
update activation_pending set activated_time=now(),user_activated='Y' where id=p_pending_id;
commit;
set p_message="success";
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` PROCEDURE `already_processed`(IN p_stock_id int,OUT p_out varchar(10))
BEGIN
declare l_count int;
declare l_qtr int;

set l_qtr = get_qtr(month(now()),year(now()),'latest');

select count(*) into l_count from income_statements where stock_id=p_stock_id and qtr_identifier=l_qtr;
if l_count>0 then
set p_out='Y';
else
set p_out='N';
end if;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` PROCEDURE `already_processed_price`(IN p_stock_id int,OUT p_out varchar(10))
BEGIN
declare l_count int;
select count(*) into l_count from montly_price where stock_id=get_stock_name(p_stock_id);
if l_count>0 then
set p_out='Y';
else
set p_out='N';
end if;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` PROCEDURE `ban_proxy`(IN proxy varchar(100))
BEGIN
update proxies set banned='Y' where proxy=proxy;
commit;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` PROCEDURE `create_session`(IN p_email varchar(100),IN p_token varchar(45),out p_message varchar(100))
BEGIN

declare exit handler for SQLEXCEPTION
begin
set p_message="fail";
end;

insert into sessions values(p_email,p_token,now());
commit;
set p_message="success";

END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` PROCEDURE `fetch_all_bse_stocks`()
BEGIN
select bse_id from stocks where status='A' and bse_id !='';
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` PROCEDURE `fetch_all_stocks`()
BEGIN

select stock_id,nse_id,bse_id from stocks where status='A' and nse_id !='';

END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` PROCEDURE `fetch_mege_stocks`()
BEGIN

select p.stock_id,nse_id,count(ic.stock_id) dup_count from(
select stock_id,nse_id,count(nse_id) over(partition by nse_id) cnt from stocks where nse_id !='') p
left outer join income_statements ic on p.stock_id=ic.stock_id
where p.cnt>1 group by p.stock_id,nse_id having count(ic.stock_id)>0 order by nse_id ;

select distinct nse_id from(
select stock_id,nse_id,count(nse_id) over(partition by nse_id) cnt from stocks where nse_id !='') p
left outer join income_statements ic on p.stock_id=ic.stock_id
where p.cnt>1 group by p.stock_id,nse_id having count(ic.stock_id)>0 order by nse_id ;

END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`10.0.0.45` PROCEDURE `get_all_amcs`()
BEGIN
select amc_id,amc_name from amc where status='A' order by amc_name;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` PROCEDURE `get_data_date`(IN p_batch_id int,OUT p_date date)
BEGIN
select start_date_of_data into p_date from batches where batch_id=p_batch_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` PROCEDURE `get_graph_data`(IN p_stock_id int,IN p_stock_to_compare int,IN p_category_id smallint,IN p_type_id smallint,IN p_mode varchar(1),IN p_from_qtr int,IN p_total_qtr int,IN p_total_qtr_income int,IN p_price1 varchar(1),IN p_price2 varchar(1))
BEGIN

declare l_latest_qtr int;

set l_latest_qtr= get_qtr(month(now()),year(now()),'latest');

if p_mode='S' then
SELECT 
    CONCAT(GET_MONTH_NAME(month), '-', year) period,
    IFNULL(ROUND(income_value, 4), 0) value
FROM
    vw_qtr_to_num t1
        LEFT OUTER JOIN
    (SELECT 
        income_month, income_year, income_value
    FROM
        income_statements inc
    WHERE
        stock_id = p_stock_id
            AND result_cat_id = p_category_id
            AND income_stmt_type_id = p_type_id
            AND qtr_identifier >= l_latest_qtr - p_total_qtr_income) t2 ON t1.month = t2.income_month
        AND t1.year = t2.income_year
WHERE
    t1.qtr > l_latest_qtr - p_total_qtr_income
        AND t1.qtr <= l_latest_qtr
ORDER BY year , month;

if p_price1='Y' then
SELECT 
    CONCAT(GET_MONTH_NAME(mp.month), '-', mp.year) period,
    ROUND(IFNULL(close, 0), 2) price
FROM
    vw_qtr_to_num v
        LEFT OUTER JOIN
    montly_price mp ON v.qtr = mp.qtr
WHERE
    mp.stock_id = p_stock_id AND v.qtr > l_latest_qtr - p_total_qtr
        AND v.qtr <= l_latest_qtr
ORDER BY mp.year , mp.month;

end if;

else
SELECT 
    stock_id,
    CONCAT(GET_MONTH_NAME(month), '-', year) period,
    value
FROM
    (SELECT 
        p_stock_id stock_id,
            month,
            year,
            IFNULL(income_value, 0) value
    FROM
        vw_qtr_to_num t1
    LEFT OUTER JOIN (SELECT 
        income_month, income_year, income_value
    FROM
        income_statements inc
    WHERE
        stock_id = p_stock_id
            AND result_cat_id = p_category_id
            AND income_stmt_type_id = p_type_id
            AND qtr_identifier >= l_latest_qtr - p_total_qtr_income) t2 ON t1.month = t2.income_month
        AND t1.year = t2.income_year
    WHERE
        t1.qtr > l_latest_qtr - p_total_qtr_income
            AND t1.qtr <= l_latest_qtr UNION ALL SELECT 
        p_stock_to_compare stock_id,
            month,
            year,
            IFNULL(income_value, 0) value
    FROM
        vw_qtr_to_num t1
    LEFT OUTER JOIN (SELECT 
        income_month, income_year, income_value
    FROM
        income_statements inc
    WHERE
        stock_id = p_stock_to_compare
            AND result_cat_id = p_category_id
            AND income_stmt_type_id = p_type_id
            AND qtr_identifier >= l_latest_qtr - p_total_qtr_income) t2 ON t1.month = t2.income_month
        AND t1.year = t2.income_year
    WHERE
        t1.qtr > l_latest_qtr - p_total_qtr_income
            AND t1.qtr <= l_latest_qtr) c
ORDER BY year , month;

if p_price1='Y' then
SELECT 
    CONCAT(GET_MONTH_NAME(mp.month), '-', mp.year) period,
    ROUND(IFNULL(close, 0), 2) price
FROM
    vw_qtr_to_num v
        LEFT OUTER JOIN
    montly_price mp ON v.qtr = mp.qtr
WHERE
    mp.stock_id = p_stock_id AND v.qtr > l_latest_qtr - p_total_qtr
        AND v.qtr <= l_latest_qtr
ORDER BY mp.year , mp.month;

end if;

if p_price2='Y' then
SELECT 
    CONCAT(GET_MONTH_NAME(mp.month), '-', mp.year) period,
    ROUND(IFNULL(close, 0), 2) price
FROM
    vw_qtr_to_num v
        LEFT OUTER JOIN
    montly_price mp ON v.qtr = mp.qtr
WHERE
    mp.stock_id = p_stock_to_compare AND v.qtr > l_latest_qtr - p_total_qtr
        AND v.qtr <= l_latest_qtr
ORDER BY mp.year , mp.month;

end if;

end if;

END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`10.0.0.45` PROCEDURE `get_mutual_funds_nav`(IN p_scheme_code1 int,IN p_scheme_code2 int,IN p_days int)
BEGIN
SET SESSION max_recursive_iterations = 6000;
select p_scheme_code1 as scheme_code,ifnull(nav_value,0) as nav_value from mf_day_list d left outer join mutual_funds_nav nav on d.day=nav.nav_date and scheme_code=p_scheme_code1 where d.day > date(DATE_SUB(now(), INTERVAL p_days day)) order by d.day asc;
if p_scheme_code2 !=0 then
select p_scheme_code2 as scheme_code,ifnull(nav_value,0) as nav_value from mf_day_list d left outer join mutual_funds_nav nav on d.day=nav.nav_date and scheme_code=p_scheme_code2 where d.day > date(DATE_SUB(now(), INTERVAL p_days day)) order by d.day asc;
end if;

END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` PROCEDURE `get_result_category_labels`(IN p_stock_id int,IN p_stock_to_compare int,IN p_no_of_qtr smallint,IN p_mode varchar(1))
BEGIN

declare l_latest_qtr smallint;
set l_latest_qtr = `get_qtr`(month(now()),year(now()),'latest');

if p_mode="S" then
SELECT 
    rc.category_id label_id, rc.category_name label_name
FROM
    income_statements inc
        INNER JOIN
    result_category rc ON inc.result_cat_id = rc.category_id
        AND inc.stock_id = p_stock_id
WHERE
    inc.qtr_identifier >= l_latest_qtr - p_no_of_qtr and inc.income_value !=0.0
GROUP BY rc.category_id;

else
SELECT 
    t1.category_id label_id, t1.category_name label_name
FROM
    (SELECT DISTINCT
        rc.category_id, category_name
    FROM
        income_statements inc
    INNER JOIN result_category rc ON inc.result_cat_id = rc.category_id
        AND inc.stock_id = p_stock_id
    WHERE
        inc.qtr_identifier >= l_latest_qtr - p_no_of_qtr and inc.income_value !=0.0) t1
        INNER JOIN
    (SELECT DISTINCT
        rc.category_id, rc.category_name
    FROM
        income_statements inc
    INNER JOIN result_category rc ON inc.result_cat_id = rc.category_id
        AND inc.stock_id = p_stock_to_compare
    WHERE
        inc.qtr_identifier >= l_latest_qtr - p_no_of_qtr and inc.income_value !=0.0) t2 ON t1.category_id = t2.category_id
GROUP BY t1.category_id;

end if;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` PROCEDURE `get_result_type_label`(IN p_stock_id int,IN p_stock_to_compare int,IN p_no_of_qtr smallint,IN p_mode varchar(1),IN p_category_id int )
BEGIN

declare l_latest_qtr smallint;
set l_latest_qtr = `get_qtr`(month(now()),year(now()),'latest');

if p_mode="S" then

SELECT 
    ist.income_stmt_type_id label_id, ist.income_stmt_name label_name
FROM
    income_statements inc
        INNER JOIN
    income_stmt_type ist ON inc.income_stmt_type_id = ist.income_stmt_type_id
        AND inc.stock_id = p_stock_id
WHERE
    inc.qtr_identifier >= l_latest_qtr - p_no_of_qtr
        AND inc.result_cat_id = p_category_id and inc.income_value !=0.0
GROUP BY ist.income_stmt_type_id;

else
SELECT 
    ist.income_stmt_type_id label_id, ist.income_stmt_name label_name
FROM
    (SELECT 
        income_stmt_type_id, qtr_identifier
    FROM
        income_statements inc
    WHERE
        stock_id = p_stock_id
            AND inc.qtr_identifier >= l_latest_qtr - p_no_of_qtr
            AND inc.result_cat_id = p_category_id and inc.income_value !=0.0) t1
        INNER JOIN
    (SELECT 
        income_stmt_type_id, qtr_identifier
    FROM
        income_statements inc
    WHERE
        stock_id = p_stock_to_compare
            AND inc.qtr_identifier >= l_latest_qtr - p_no_of_qtr
            AND inc.result_cat_id = p_category_id and inc.income_value !=0.0) t2 ON t1.income_stmt_type_id = t2.income_stmt_type_id
        AND t1.qtr_identifier = t2.qtr_identifier 
        INNER JOIN
    income_stmt_type ist ON t1.income_stmt_type_id = ist.income_stmt_type_id
GROUP BY ist.income_stmt_type_id;

end if;

END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`10.0.0.45` PROCEDURE `get_scheme_category`(IN p_amc1 int,IN p_amc2 int)
BEGIN
if p_amc2=0 then
SELECT distinct cat.scheme_cat_id,cat.scheme_cat_name as scheme_cat_short_name FROM scheme_category cat inner join mutual_funds mf on cat.scheme_cat_id=mf.scheme_category
inner join amc on mf.amc=amc.amc_id where amc.amc_id=p_amc1 order by cat.scheme_cat_name;
else

select t1.scheme_cat_id,t1.scheme_cat_short_name from (
SELECT distinct cat.scheme_cat_id,cat.scheme_cat_name as scheme_cat_short_name FROM scheme_category cat inner join mutual_funds mf on cat.scheme_cat_id=mf.scheme_category
inner join amc on mf.amc=amc.amc_id where amc.amc_id=p_amc1) t1
inner join (
SELECT distinct cat.scheme_cat_id,cat.scheme_cat_name as scheme_cat_short_name FROM scheme_category cat inner join mutual_funds mf on cat.scheme_cat_id=mf.scheme_category
inner join amc on mf.amc=amc.amc_id where amc.amc_id=p_amc2) t2
on t1.scheme_cat_short_name=t2.scheme_cat_short_name order by t1.scheme_cat_short_name;

end if;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`10.0.0.45` PROCEDURE `get_scheme_nav`(IN p_amc1 int,p_amc2 int,IN p_scheme_cat_id int)
BEGIN

if p_amc2=0 then
select p_amc1 amc,mf.code,mf.scheme_nav_name from mutual_funds mf inner join amc on mf.amc=amc.AMC_ID
inner join scheme_category sc on sc.scheme_cat_id=mf.scheme_category
where mf.amc=p_amc1 and sc.scheme_cat_id=p_scheme_cat_id order by mf.Code;

else

select * from (
select p_amc1 amc,mf.code,mf.scheme_nav_name from mutual_funds mf inner join amc on mf.amc=amc.AMC_ID
inner join scheme_category sc on sc.scheme_cat_id=mf.scheme_category
where mf.amc=p_amc1 and sc.scheme_cat_id=p_scheme_cat_id

union all

select p_amc2 amc,mf.code,mf.scheme_nav_name from mutual_funds mf inner join amc on mf.amc=amc.AMC_ID
inner join scheme_category sc on sc.scheme_cat_id=mf.scheme_category
where mf.amc=p_amc2 and sc.scheme_cat_id=p_scheme_cat_id) t1 order by scheme_nav_name;

end if;


END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`10.0.0.45` PROCEDURE `insert_amc`(IN P_amc_name varchar(500), OUT o_id int)
BEGIN
declare l_rc_id int;
declare l_id int;

DECLARE EXIT HANDLER FOR 1062
  BEGIN
select amc_id into o_id from amc where amc_name=P_amc_name;
  END;
	insert into amc(amc_name) values(P_amc_name);
    commit;
SELECT 
    amc_id
INTO o_id FROM
    amc
WHERE
    amc_name = P_amc_name;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` PROCEDURE `insert_batch_log`(IN p_batch_id int,IN p_message longtext)
BEGIN
insert into batch_log(batch_id,message) values(p_batch_id,p_message);
commit;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` PROCEDURE `insert_exchange`(IN P_exchnage_name varchar(50), OUT o_id int)
BEGIN
declare l_id int;


DECLARE EXIT HANDLER FOR 1062
  BEGIN
    select exchange_id into l_id from exchange where exchange_name=P_exchnage_name;
    set o_id=l_id;
  END;

select IFNULL(max(exchange_id),0)+1 into l_id from exchange;
  
	insert into exchange set 
    exchange_id=l_id,
    exchange_name=P_exchnage_name;
    commit;
   set o_id=l_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` PROCEDURE `insert_income_batch_log`(IN p_stock_id int,IN p_month int,IN p_year int,IN p_exchange varchar(10),IN p_type varchar(45),IN p_params mediumtext,IN p_url varchar(500),IN p_response longtext)
BEGIN
declare l_qtr int;
set l_qtr = `get_qtr`(p_month, p_year, 'specific');

insert into income_batch_log set
stock_id=p_stock_id,
qtr_id=l_qtr,
type=p_type,
exchange=p_exchange,
params=p_params,
url=p_url,
response=p_response,
mod_time=now();
commit;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` PROCEDURE `insert_income_statements`(IN p_stock_id int, IN p_income_month smallint,IN p_income_year smallint,
IN p_income_stmt_name varchar(500),IN p_income_value decimal(25,7),IN p_status varchar(1),IN p_result_cat_name varchar(200),IN p_exchange_name varchar(50), OUT p_message varchar(200))
BEGIN
declare l_stmt_id int;
declare l_result_cat_id int;
declare l_exchange_id int;
declare l_qtr_identifier int;

DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
set p_message="E";
resignal;
  END;

call `insert_exchange`(p_exchange_name,@l_exchange_id);
call `insert_result_category`(p_result_cat_name,@l_exchange_id,@l_result_cat_id);
call `insert_stmt_type`(p_income_stmt_name,@l_result_cat_id,@l_stmt_id);
set l_qtr_identifier = `get_qtr`(p_income_month,p_income_year,'specific');

insert into income_statements set 
stock_id=p_stock_id,
income_month=p_income_month,
income_year=p_income_year,
income_stmt_type_id=@l_stmt_id,
income_value=p_income_value,
status=p_status,
mod_timestamp=now(),
result_cat_id=@l_result_cat_id,
exchange_id=@l_exchange_id,
qtr_identifier=l_qtr_identifier ON DUPLICATE KEY UPDATE income_value=p_income_value;
commit;
set p_message="S";
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`10.0.0.45` PROCEDURE `insert_mutual_funds`(IN p_amc_name varchar(500),IN p_sheme_code int,IN p_scheme_name varchar(500),
IN p_scheme_type_name varchar(500),
IN p_scheme_category_name varchar(500),
IN p_scheme_category_short_name varchar(500),
IN p_scheme_nav_name varchar(500),
IN p_scheme_min_amount varchar(500),
IN p_launch_date date,
IN p_issue_date date,
IN p_isin varchar(500),
 OUT p_message varchar(200))
BEGIN
declare l_amc_id int;
declare l_scheme_type_id int;
declare l_scheme_cat_id int;

DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
set p_message="E";
resignal;
  END;

call `insert_amc`(p_amc_name,@l_amc_id);
call `insert_scheme_type`(p_scheme_type_name,@l_scheme_type_id);
call `insert_scheme_category`(p_scheme_category_name,p_scheme_category_short_name,@l_scheme_cat_id);

insert into mutual_funds set 
Code=p_sheme_code,
AMC=@l_amc_id,
scheme_name=p_scheme_name,
scheme_type=@l_scheme_type_id,
scheme_category=@l_scheme_cat_id,
scheme_nav_name=p_scheme_nav_name,
scheme_minimum_amount=p_scheme_min_amount,
launch_date=p_launch_date,
closure_date=p_issue_date,
ISIN_Div_Payout_ISIN_GrowthISIN_Div_Reinvestment=p_isin
 ON DUPLICATE KEY UPDATE scheme_nav_name=p_scheme_nav_name;
commit;
set p_message="S";
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` PROCEDURE `insert_result_category`(IN P_result_category_name varchar(500), IN P_exchange INT, OUT o_id int)
BEGIN
declare l_rc_id int;
declare l_id int;

DECLARE EXIT HANDLER FOR 1062
  BEGIN
    select category_id into l_id from result_category where category_name=P_result_category_name;
    set o_id=l_id;
  END;

select IFNULL(max(category_id),0)+1 into l_id from result_category;
  
	insert into result_category set 
    category_id=l_id,
    category_name=P_result_category_name,
    exchange=P_exchange;
    commit;
   set o_id=l_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`10.0.0.45` PROCEDURE `insert_scheme_category`(IN P_scheme_category_name varchar(500),IN P_scheme_category_short_name varchar(500), OUT o_id int)
BEGIN

DECLARE EXIT HANDLER FOR 1062
  BEGIN
select scheme_cat_id into o_id from scheme_category where scheme_cat_name=P_scheme_category_name;
  END;
	insert into scheme_category(scheme_cat_name,scheme_cat_short_name) values(P_scheme_category_name,P_scheme_category_short_name);
    commit;
SELECT 
    scheme_cat_id
INTO o_id FROM
    scheme_category
WHERE
    scheme_cat_name = P_scheme_category_name;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`10.0.0.45` PROCEDURE `insert_scheme_type`(IN p_scheme_type_name varchar(500), OUT o_id int)
BEGIN
declare l_rc_id int;
declare l_id int;

DECLARE EXIT HANDLER FOR 1062
  BEGIN
select scheme_type_id into o_id from scheme_type where scheme_type_name=p_scheme_type_name;
  END;
	insert into scheme_type(scheme_type_name) values(p_scheme_type_name);
    commit;
SELECT 
    scheme_type_id
INTO o_id FROM
    scheme_type
WHERE
    scheme_type_name = p_scheme_type_name;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` PROCEDURE `insert_stmt_type`(IN P_stmt_type_name varchar(500),IN p_result_cat_id int, OUT o_id int)
BEGIN
declare l_id int;

DECLARE EXIT HANDLER FOR 1062
  BEGIN
    select income_stmt_type_id into l_id from income_stmt_type where income_stmt_name=P_stmt_type_name and result_category_id=p_result_cat_id;
    set o_id=l_id;
  END;

select IFNULL(max(income_stmt_type_id),0)+1 into l_id from income_stmt_type;
  
	insert into income_stmt_type set 
    income_stmt_type_id=l_id,
    income_stmt_name=P_stmt_type_name,
    result_category_id=p_result_cat_id,
    mod_timestamp=now();
    commit;
   set o_id=l_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` PROCEDURE `merge_duplicate_stocks`(IN p_main varchar(45),IN p_normain varchar(45))
BEGIN
insert into income_statements(stock_id,income_month,income_year,income_stmt_type_id,income_value,status,mod_timestamp,result_cat_id,exchange_id,qtr_identifier)
select p_main,income_month,income_year,income_stmt_type_id,income_value,status,mod_timestamp,result_cat_id,exchange_id,qtr_identifier from income_statements where stock_id=p_normain
on duplicate key update mod_timestamp=now();
delete from income_statements where stock_id=p_normain;

insert into montly_price select * from montly_price p where stock_id=p_normain on duplicate key update spread_open_close=p.spread_open_close;
delete from montly_price where stock_id=p_normain;
delete from stocks where stock_id=p_normain;
commit;

END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` PROCEDURE `merge_or_get_stock`(IN p_nse_id varchar(100),IN p_stock_name varchar(1000),IN p_isin varchar(100),OUT o_stock_id int)
BEGIN
declare l_count int;

select count(*) into l_count from stocks where nse_id=p_nse_id;

if l_count<1 then

insert into stocks(stock_name,bse_id,nse_id,isin,impact_cost,cin,STATUS,INDUSTRY_ID,BC_RD,MARKET_LOT,ISSUE_DATE)
values(p_stock_name,null,p_nse_id,p_isin,null,null,'A',0,null,0,null);
commit;
select stock_id into o_stock_id from stocks where nse_id=p_nse_id;
else

select stock_id into o_stock_id from stocks where nse_id=p_nse_id limit 1;
update stocks set stock_name=p_stock_name where nse_id=p_nse_id ;
commit;
end if;


END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` PROCEDURE `next_proxy`()
BEGIN
select proxy from proxies where banned='N' limit 1;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` PROCEDURE `register_user`(IN p_email varchar(100),IN p_email_sent_status varchar(1),IN p_token varchar(45),out p_message varchar(200),out p_activation_link varchar(1000))
BEGIN
  declare l_user_count int;
  declare l_id int;
DECLARE exit HANDLER FOR 1062
  BEGIN
set p_message="AR";
  END;
  
  select count(*) into l_user_count from registered_user where email=p_email;
  
  if l_user_count>0 then
  set p_message="AR";
  else

select ifnull(max(id),0)+1 into l_id from activation_pending;
set p_activation_link=concat("https://www.stocksandcharts.in/activate/",l_id,"/",p_token);
insert into activation_pending(id,email,email_sent_time,email_sent_status,activation_link)
values(l_id,p_email,now(),p_email_sent_status,p_activation_link);
commit;
set p_message="success";
end if;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` PROCEDURE `save_proxy`(IN proxy varchar(100))
BEGIN
DECLARE EXIT HANDLER FOR 1062
  BEGIN
  END;
insert into proxies values(proxy,'N');
commit;

END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` PROCEDURE `update_data_date_batch`(IN p_batch_id int,IN p_date date)
BEGIN
update batches set start_date_of_data=p_date where batch_id=p_batch_id;
commit;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` PROCEDURE `validate_session`(IN p_token varchar(45),out p_message varchar(100))
BEGIN

declare l_seconds int;
set p_message="valid";

select count(*) into l_seconds from sessions where token=p_token;

if l_seconds<>1 then
set p_message="expired";
else
select TIME_TO_SEC(timediff(now(),mod_time)) into l_seconds from sessions where token=p_token;
if l_seconds>7200 then
set p_message="expired";
end if;
end if;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` PROCEDURE `verify_user`(IN p_email varchar(200),out p_message varchar(1))
BEGIN
declare l_cnt int;
select count(*) into l_cnt from registered_user where email=p_email;

if l_cnt>0 then
set p_message='Y';
else
set p_message='N';
end if;
END$$
DELIMITER ;
