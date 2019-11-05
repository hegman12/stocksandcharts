DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` FUNCTION `get_month_name`(p_month int) RETURNS varchar(3) CHARSET utf8mb4
    DETERMINISTIC
BEGIN
declare l_month varchar(3);

if p_month=1 then
set l_month= 'Jan';
elseif p_month=2 then
set l_month= 'Feb';
elseif p_month=3 then
set l_month= 'Mar';
elseif p_month=4 then
set l_month= 'Apr';
elseif p_month=5 then
set l_month= 'May';
elseif p_month=6 then
set l_month= 'Jun';
elseif p_month=7 then
set l_month= 'Jul';
elseif p_month=8 then
set l_month= 'Aug';
elseif p_month=9 then
set l_month= 'Sep';
elseif p_month=10 then
set l_month= 'Oct';
elseif p_month=11 then
set l_month= 'Nov';
else
set l_month= 'Dec';
end if;
return l_month;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` FUNCTION `get_qtr`(p_month int,p_year int, p_type varchar(100)) RETURNS int(11)
    READS SQL DATA
BEGIN
declare l_return int;
if p_type='specific' then
select qtr into l_return from vw_qtr_to_num where month=p_month and year=p_year;
else
if p_month<4 then
	select max(qtr) into l_return from vw_qtr_to_num where year=p_year-1;
else
	select max(qtr) into l_return from vw_qtr_to_num where month<p_month and year=p_year;
end if;
end if;
RETURN l_return;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`stocks`@`localhost` FUNCTION `get_stock_name`(p_bseId int) RETURNS int(11)
    READS SQL DATA
BEGIN
declare l_return int;

select stock_id into l_return from stocks where bse_id=p_bseId;

RETURN l_return;
END$$
DELIMITER ;
