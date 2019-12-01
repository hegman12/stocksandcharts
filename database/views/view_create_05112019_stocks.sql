SELECT count(*) FROM stocksdb.mutual_funds_nav where nav_date= str_to_date('17-09-2019','%d-%m-%Y');
CREATE ALGORITHM=UNDEFINED DEFINER=`stocks`@`10.0.0.45` SQL SECURITY DEFINER VIEW `dup_stocks` AS select `d`.`stock_id` AS `stock_id`,count(`ic`.`stock_id`) AS `count(ic.stock_id)` from (`stock_dup2` `d` left join `income_statements` `ic` on(`d`.`stock_id` = `ic`.`stock_id`)) where `ic`.`stock_id` is null group by `d`.`stock_id`;

CREATE ALGORITHM=UNDEFINED DEFINER=`stocks`@`10.0.0.45` SQL SECURITY DEFINER VIEW `mf_day_list` AS with recursive cte as (select cast(current_timestamp() - interval 5000 day as date) AS `day` union all select `cte`.`day` + interval 1 day AS `DATE_add(day, INTERVAL 1 day)` from `cte` where `cte`.`day` < cast(current_timestamp() - interval 1 day as date))select `cte`.`day` AS `day` from `cte` where dayofweek(`cte`.`day`) not in (1,7) order by `cte`.`day` desc;

CREATE ALGORITHM=UNDEFINED DEFINER=`stocks`@`10.0.0.45` SQL SECURITY DEFINER VIEW `stock_dup2` AS select `s`.`stock_id` AS `stock_id`,`s`.`nse_id` AS `nse_id` from (`stocks` `s` join `stock_dups` `d` on(`s`.`nse_id` = `d`.`nse_id`));

CREATE ALGORITHM=UNDEFINED DEFINER=`stocks`@`10.0.0.45` SQL SECURITY DEFINER VIEW `stock_dups` AS select `s`.`nse_id` AS `nse_id` from `stocks` `s` where `s`.`nse_id` <> '' group by `s`.`nse_id` having count(`s`.`nse_id`) > 1;

CREATE ALGORITHM=UNDEFINED DEFINER=`stocks`@`localhost` SQL SECURITY DEFINER VIEW `vw_qtr_to_num` AS with recursive cte as (select str_to_date('31-12-2009','%d-%m-%Y') AS `d`,64 AS `id` union all select `cte`.`d` + interval 1 quarter AS `DATE_ADD(d,interval 1 QUARTER)`,`cte`.`id` + 1 AS `id+1` from `cte` where year(`cte`.`d`) <= year(current_timestamp()))select month(`cte`.`d`) AS `month`,year(`cte`.`d`) AS `year`,`cte`.`id` AS `qtr` from `cte` order by `cte`.`d`;

select str_to_date('17-09-2019','%d-%m-%Y');

SELECT * FROM stocksdb.mutual_funds_nav where nav_date= str_to_date('20-09-2019','%d-%m-%Y');