CREATE TABLE `activation_pending` (
  `id` int(11) NOT NULL,
  `email` varchar(100) NOT NULL,
  `email_sent_time` datetime DEFAULT NULL,
  `email_sent_status` varchar(1) NOT NULL,
  `user_activated` varchar(1) NOT NULL DEFAULT 'N',
  `activated_time` datetime DEFAULT NULL,
  `activation_link` varchar(1000) NOT NULL,
  `expired` varchar(1) DEFAULT 'N',
  `insert_time` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_unique` (`email`,`user_activated`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `amc` (
  `AMC_ID` int(11) NOT NULL AUTO_INCREMENT,
  `AMC_NAME` varchar(500) DEFAULT NULL,
  `status` varchar(1) DEFAULT 'A',
  `ctimme` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`AMC_ID`),
  UNIQUE KEY `idx_amc_name` (`AMC_NAME`)
) ENGINE=InnoDB AUTO_INCREMENT=18755 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `batch_log` (
  `batch_log_id` int(11) NOT NULL AUTO_INCREMENT,
  `batch_id` int(11) NOT NULL,
  `message` longtext DEFAULT NULL,
  `create_date` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`batch_log_id`),
  KEY `fx_batch_id_idx` (`batch_id`),
  CONSTRAINT `fx_batch_id` FOREIGN KEY (`batch_id`) REFERENCES `batches` (`batch_id`)
) ENGINE=InnoDB AUTO_INCREMENT=290 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `batches` (
  `batch_id` int(11) NOT NULL AUTO_INCREMENT,
  `batch_name` varchar(45) DEFAULT NULL,
  `status` varchar(1) DEFAULT NULL,
  `start_date_of_data` date DEFAULT NULL,
  PRIMARY KEY (`batch_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `bse_stocks` (
  `STOCK_ID` int(11) DEFAULT NULL,
  `STOCK_NAME` text DEFAULT NULL,
  `ISIN` text DEFAULT NULL,
  `BSE_ID` int(11) DEFAULT NULL,
  `NSE_ID` text DEFAULT NULL,
  `CIN` text DEFAULT NULL,
  `STATUS` text DEFAULT NULL,
  `INDUSTRY_ID` int(11) DEFAULT NULL,
  `IMPACT_COST` text DEFAULT NULL,
  `BC_RD` text DEFAULT NULL,
  `MARKET_LOT` int(11) DEFAULT NULL,
  `ISSUE_DATE` text DEFAULT NULL,
  `CREATED_DATE` text DEFAULT NULL,
  `MOD_DATE` text DEFAULT NULL,
  `flag` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `cm25jul2019bhav` (
  `SYMBOL` text DEFAULT NULL,
  `ISIN` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `dual` (
  `dummy` varchar(1) NOT NULL,
  PRIMARY KEY (`dummy`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `exchange` (
  `exchange_id` int(11) NOT NULL AUTO_INCREMENT,
  `exchange_name` varchar(45) NOT NULL,
  PRIMARY KEY (`exchange_id`),
  UNIQUE KEY `exchange_name_UNIQUE` (`exchange_name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `income_batch_log` (
  `income_batch_log_id` bigint(12) NOT NULL AUTO_INCREMENT,
  `stock_id` int(11) NOT NULL,
  `qtr_id` smallint(5) DEFAULT NULL,
  `type` varchar(45) NOT NULL DEFAULT 'I',
  `exchange` varchar(20) DEFAULT NULL,
  `params` mediumtext DEFAULT NULL,
  `url` varchar(500) DEFAULT NULL,
  `response` longtext DEFAULT NULL,
  `mod_time` datetime NOT NULL,
  PRIMARY KEY (`income_batch_log_id`),
  KEY `idx_stock` (`stock_id`),
  KEY `idx_time` (`mod_time`),
  KEY `idx_type` (`type`)
) ENGINE=InnoDB AUTO_INCREMENT=45854 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `income_batch_log_batch_backup` (
  `income_batch_log_id` bigint(12) NOT NULL DEFAULT 0,
  `stock_id` int(11) NOT NULL,
  `qtr_id` smallint(5) DEFAULT NULL,
  `type` varchar(45) NOT NULL DEFAULT 'I',
  `exchange` varchar(20) DEFAULT NULL,
  `params` mediumtext DEFAULT NULL,
  `url` varchar(500) DEFAULT NULL,
  `response` longtext DEFAULT NULL,
  `mod_time` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `income_statements` (
  `income_statements_id` int(11) NOT NULL AUTO_INCREMENT,
  `stock_id` int(11) NOT NULL,
  `income_month` smallint(5) NOT NULL,
  `income_year` smallint(5) NOT NULL,
  `income_stmt_type_id` int(11) NOT NULL,
  `income_value` decimal(25,7) DEFAULT 0.0000000,
  `status` varchar(1) NOT NULL DEFAULT 'A',
  `mod_timestamp` datetime DEFAULT NULL,
  `result_cat_id` int(11) NOT NULL,
  `exchange_id` int(11) NOT NULL,
  `qtr_identifier` int(11) NOT NULL,
  PRIMARY KEY (`income_statements_id`),
  UNIQUE KEY `uq_value_on_tables` (`stock_id`,`income_stmt_type_id`,`status`,`result_cat_id`,`exchange_id`,`qtr_identifier`),
  KEY `fx_income_stmt_id_idx` (`income_stmt_type_id`),
  KEY `fx_stock_id_idx` (`stock_id`),
  KEY `fx_result_cat_id_idx` (`result_cat_id`),
  KEY `fx_exchange_id_idx` (`exchange_id`),
  CONSTRAINT `fx_exchange_id` FOREIGN KEY (`exchange_id`) REFERENCES `exchange` (`exchange_id`),
  CONSTRAINT `fx_income_stmt_id` FOREIGN KEY (`income_stmt_type_id`) REFERENCES `income_stmt_type` (`income_stmt_type_id`),
  CONSTRAINT `fx_result_cat_id` FOREIGN KEY (`result_cat_id`) REFERENCES `result_category` (`category_id`),
  CONSTRAINT `fx_stock_id` FOREIGN KEY (`stock_id`) REFERENCES `stocks` (`stock_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2751456 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `income_stmt_type` (
  `income_stmt_type_id` int(11) NOT NULL,
  `income_stmt_name` varchar(500) NOT NULL,
  `result_category_id` int(11) NOT NULL,
  `mod_timestamp` datetime DEFAULT NULL,
  PRIMARY KEY (`income_stmt_type_id`),
  UNIQUE KEY `uq_values_row` (`income_stmt_name`,`result_category_id`),
  KEY `result_category_id_idx` (`result_category_id`),
  CONSTRAINT `result_category_id` FOREIGN KEY (`result_category_id`) REFERENCES `result_category` (`category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `income_stmt_type_bkp` (
  `income_stmt_type_id` int(11) NOT NULL,
  `income_stmt_name` varchar(500) NOT NULL,
  `result_category_id` int(11) NOT NULL,
  `mod_timestamp` datetime DEFAULT NULL,
  `name2` varchar(500) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `montly_price` (
  `price_id` int(11) NOT NULL AUTO_INCREMENT,
  `stock_id` int(11) NOT NULL,
  `month` smallint(2) NOT NULL,
  `year` mediumint(4) NOT NULL,
  `open` float DEFAULT NULL,
  `high` float DEFAULT NULL,
  `low` float DEFAULT NULL,
  `close` float DEFAULT NULL,
  `no_of_shares` int(11) DEFAULT NULL,
  `delivery_quantity` int(11) DEFAULT NULL,
  `delivery_percentage` float DEFAULT NULL,
  `spread_high_low` float DEFAULT NULL,
  `spread_open_close` float DEFAULT NULL,
  `qtr` int(11) NOT NULL,
  PRIMARY KEY (`price_id`),
  KEY `fx_stock_id_idx` (`stock_id`),
  CONSTRAINT `fx_stock_id_price` FOREIGN KEY (`stock_id`) REFERENCES `stocks` (`stock_id`)
) ENGINE=InnoDB AUTO_INCREMENT=567878 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `mutual_funds` (
  `Code` int(11) NOT NULL,
  `AMC` int(11) NOT NULL,
  `scheme_name` varchar(500) DEFAULT NULL,
  `scheme_type` int(11) NOT NULL,
  `scheme_category` int(11) NOT NULL,
  `scheme_nav_name` varchar(500) DEFAULT NULL,
  `scheme_minimum_amount` varchar(500) DEFAULT NULL,
  `launch_date` datetime DEFAULT NULL,
  `closure_date` datetime DEFAULT NULL,
  `ISIN_Div_Payout_ISIN_GrowthISIN_Div_Reinvestment` varchar(500) DEFAULT NULL,
  `status` varchar(1) DEFAULT NULL,
  `ctime` datetime DEFAULT NULL,
  PRIMARY KEY (`Code`),
  UNIQUE KEY `scheme_nav_name_UNIQUE` (`scheme_nav_name`),
  KEY `fx_scheme_type_idx` (`scheme_type`),
  KEY `fx_scheme_cat_idx` (`scheme_category`),
  KEY `fx_amc_name_idx` (`AMC`),
  CONSTRAINT `fx_amc_name` FOREIGN KEY (`AMC`) REFERENCES `amc` (`AMC_ID`),
  CONSTRAINT `fx_scheme_cat` FOREIGN KEY (`scheme_category`) REFERENCES `scheme_category` (`scheme_cat_id`),
  CONSTRAINT `fx_scheme_type` FOREIGN KEY (`scheme_type`) REFERENCES `scheme_type` (`scheme_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `mutual_funds_nav` (
  `nav_id` int(11) NOT NULL AUTO_INCREMENT,
  `scheme_code` int(11) DEFAULT NULL,
  `nav_date` date DEFAULT NULL,
  `nav_value` float DEFAULT NULL,
  `ctime` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`nav_id`),
  UNIQUE KEY `uq_values` (`scheme_code`,`nav_date`),
  CONSTRAINT `fx_scheme_code` FOREIGN KEY (`scheme_code`) REFERENCES `mutual_funds` (`Code`)
) ENGINE=InnoDB AUTO_INCREMENT=6689062 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `nse_stocks` (
  `nse_id` text DEFAULT NULL,
  `isin` text DEFAULT NULL,
  `stock_name` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `proxies` (
  `proxy` varchar(100) NOT NULL,
  `banned` varchar(45) NOT NULL DEFAULT 'N',
  UNIQUE KEY `proxy_UNIQUE` (`proxy`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `registered_user` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(100) NOT NULL,
  `mod_time` datetime DEFAULT current_timestamp(),
  `status` varchar(1) NOT NULL DEFAULT 'A',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email_UNIQUE` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=70 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `result_category` (
  `category_id` int(11) NOT NULL,
  `category_name` varchar(200) NOT NULL,
  `exchange` smallint(3) DEFAULT NULL,
  PRIMARY KEY (`category_id`),
  UNIQUE KEY `category_name_UNIQUE` (`category_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='income statements can be of several category like segment stmts operations';

CREATE TABLE `scheme_category` (
  `scheme_cat_id` int(11) NOT NULL AUTO_INCREMENT,
  `scheme_cat_name` varchar(500) NOT NULL,
  `scheme_cat_short_name` varchar(100) NOT NULL,
  `status` varchar(1) DEFAULT 'A',
  `ctime` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`scheme_cat_id`),
  UNIQUE KEY `scheme_cat_name_UNIQUE` (`scheme_cat_name`)
) ENGINE=InnoDB AUTO_INCREMENT=18750 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `scheme_type` (
  `scheme_type_id` int(11) NOT NULL AUTO_INCREMENT,
  `scheme_type_name` varchar(500) DEFAULT NULL,
  `status` varchar(1) DEFAULT 'A',
  `ctime` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`scheme_type_id`),
  UNIQUE KEY `scheme_type_name_UNIQUE` (`scheme_type_name`)
) ENGINE=InnoDB AUTO_INCREMENT=18755 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `sessions` (
  `email` varchar(200) NOT NULL,
  `token` varchar(45) NOT NULL,
  `mod_time` datetime DEFAULT NULL,
  KEY `ixsx` (`email`(191),`token`),
  KEY `idx_token` (`token`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `stock_industry` (
  `stock_industry_id` int(11) NOT NULL,
  `stock_industry_name` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`stock_industry_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `stocks` (
  `stock_id` int(11) NOT NULL AUTO_INCREMENT,
  `stock_name` varchar(1000) NOT NULL,
  `bse_id` int(11) DEFAULT NULL,
  `nse_id` varchar(45) DEFAULT NULL,
  `isin` varchar(100) NOT NULL,
  `impact_cost` int(11) DEFAULT NULL,
  `CIN` varchar(50) DEFAULT NULL,
  `STATUS` varchar(1) NOT NULL DEFAULT 'A',
  `INDUSTRY_ID` int(11) DEFAULT NULL,
  `BC_RD` varchar(100) DEFAULT NULL,
  `MARKET_LOT` decimal(5,0) DEFAULT NULL,
  `ISSUE_DATE` datetime DEFAULT NULL,
  `MOD_DATE` datetime DEFAULT current_timestamp(),
  `outstanding_shares` bigint(32) DEFAULT 0,
  PRIMARY KEY (`stock_id`),
  KEY `fx_industry_idx` (`INDUSTRY_ID`),
  KEY `isin_idx` (`isin`),
  CONSTRAINT `fx_industry` FOREIGN KEY (`INDUSTRY_ID`) REFERENCES `stock_industry` (`stock_industry_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7698 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `t` (
  `stock_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `temp` (
  `isin` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
